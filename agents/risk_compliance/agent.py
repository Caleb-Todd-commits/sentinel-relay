"""Risk & Compliance agent business logic (agents lane).

Applies the incident policy, challenges any "confirmed breach" overclaim, and
determines what requires human approval. Deterministic in mock mode; in live
mode this is the natural place to route the AI/ML API policy-gate call.

Analytic doctrine (see risk_compliance/prompt.md): separate the GDPR
personal-data-breach threshold (unauthorised ACCESS to personal data) from a
confirmed-exfiltration claim; the access threshold can be met before any actor is
identified, which starts the assessment clock even while the final determination
and customer notification stay held for the human and Legal.
"""

from __future__ import annotations

from typing import Any

from common.aimlapi_enrichment import enrich_risk_policy_gate
from common.evidence_analysis import analyze_incident_evidence
from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-risk-compliance"
AGENT_NAME = "Risk & Compliance Agent"

_EVIDENCE = ["ev-incident-policy", "ev-api-gateway-logs", "ev-code-diff"]
_PEER_REVIEWERS = [
    "agent-forensics",
    "agent-code-review",
    "agent-threat-intel",
]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    facts = analyze_incident_evidence(ctx)
    policy_gate = enrich_risk_policy_gate(ctx, facts)
    gate = policy_gate.data
    policy_id = ctx.task.get("policyId") or "SEC-IR-API-KEY-001"
    records = facts.api.unauthorized_records_returned
    records_text = f"{records:,}"
    source_ips = ", ".join(facts.api.unauthorized_ips)
    approval_actions = facts.policy.human_approval_actions
    legal_actions = facts.policy.legal_approval_actions
    gate_label = "AI/ML policy gate" if policy_gate.used_live_api else "Policy gate"
    review_gate = _cross_review_gate(ctx)
    review_status = (
        "The peer-review gate is satisfied: Forensics, Code Review, and Threat Intel each cross-checked the others before this policy call."
        if review_gate["gateSatisfied"]
        else "The peer-review gate is incomplete, so this policy call should remain provisional until specialist verifications arrive."
    )
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="challenge",
        title=f"{gate_label}: challenge the 'confirmed exfiltration' framing; hold notification",
        summary=(
            f"{review_status} Two findings must be separated. (1) The GDPR personal-data-breach threshold is about unauthorised "
            f"ACCESS to personal data, not actor identification: gateway logs show {records_text} customer records "
            f"(including payment-methods) returned to unexpected external IPs ({source_ips}), so a confidentiality breach is "
            "likely already established and the 72h assessment clock should be treated as running from awareness. "
            "(2) I still CHALLENGE any 'confirmed exfiltration / misuse' claim — downstream resale or reuse is "
            "unproven, and actor identity is unresolved, so under our incident policy the case classification "
            "stays suspected_exposure. Customer notification stays HELD for the human Security Lead + Legal until "
            "scope, residency, and the controller/processor question are verified."
        ),
        confidence=float(gate.get("confidence", 0.88)),
        severity=str(gate.get("recommendedSeverity", "high")),
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact=(
            "Stops two opposite errors: under-reacting ('just a leaked secret, no breach') and over-claiming "
            "('confirmed mass exfiltration'). Forces a human + Legal gate before any notification."
        ),
        next_action=str(
            (gate.get("nextActions") or ["Commander should request human approval for issuer-first containment and hold all external notification pending Legal scope review."])[0]
        ),
        payload={
            "kind": "risk_assessment",
            "data": {
                "policyGate": gate,
                "partnerTool": policy_gate.metadata(),
                "recommendedSeverity": gate.get("recommendedSeverity", "high"),
                "classification": gate.get("classification", "suspected_exposure"),
                "crossReviewGate": review_gate,
                "breachThresholdAssessment": {
                    "gdprPersonalDataBreach": "likely_met",
                    "basis": "Unauthorised access to personal data (customer records + payment-methods returned to external IPs) is a confidentiality breach under GDPR Art 4(12); it does not require identifying the actor.",
                    "confirmedExfiltration": "unproven",
                    "policyClassificationReason": "Per SEC-IR-API-KEY-001, records were returned but actor identity is unresolved -> classify as suspected exposure and keep collecting evidence.",
                },
                "challenges": [
                    "Do NOT state 'confirmed breach with exfiltration' — logs prove unauthorised access, not downstream misuse or resale.",
                    "Do NOT attribute to a named actor — indicators are documentation-range IPs (per Threat Intel).",
                    "Do NOT send external customer notification without Legal sign-off on scope and wording.",
                    "Do NOT call the incident closed until the credential is issuer-verified dead AND sibling credentials are confirmed handled (per Code Review).",
                ],
                "notificationClocks": {
                    "note": "Clocks are flagged as likely-triggered; the human + Legal confirm the trigger and start time. Counts/residency not yet verified.",
                    "gdpr": "72h to the supervisory authority from awareness (Art 33); Art 34 notice to individuals if high risk — payment-method data points to high risk.",
                    "controllerVsProcessor": "If Payments Platform is a processor here, Art 33(2) requires notifying the controller without undue delay; DPAs often impose stricter/shorter contractual windows than statute.",
                    "california": "CCPA/CPRA: notify affected residents without unreasonable delay; if >500 CA residents, sample to the CA AG (treat ~30-day / 15-day expectations as planning targets pending Legal).",
                    "ccpaPrivateRight": "Cal. Civ. Code 1798.150 private right of action exposure for unauthorised access/exfiltration of personal information due to failure to maintain reasonable security.",
                },
                "openScopeQuestions": [
                    f"How many of the {records_text} records belong to EU vs California vs other residents?",
                    "Is Payments Platform controller or processor for these records, and what does the DPA notification matrix require?",
                    "Which exact customers/payment-methods are in the exported rows?",
                ],
                "policyRefs": [policy_id],
                "humanApprovalRequired": gate.get("requiredApprovals", approval_actions),
                "deferredPendingHuman": sorted(set(legal_actions + ["incident_closure"])),
                "derivedFacts": {
                    "source": "common.evidence_analysis.analyze_incident_evidence",
                    "recordsReturnedToUnexpectedIps": records,
                    "unexpectedIps": facts.api.unauthorized_ips,
                    "policyId": facts.policy.policy_id,
                    "highSeverityCondition": facts.policy.high_severity_condition,
                    "criticalSeverityCondition": facts.policy.critical_severity_condition,
                },
            },
        },
    )


def _cross_review_gate(ctx: AgentTurnContext) -> dict[str, Any]:
    reviews = [
        message
        for message in ctx.recent_messages
        if message.get("type") == "verification" and message.get("agentId") in _PEER_REVIEWERS
    ]
    latest_by_agent: dict[str, dict[str, Any]] = {}
    for message in reviews:
        latest_by_agent[str(message["agentId"])] = message

    received_ids = [
        latest_by_agent[agent_id]["id"]
        for agent_id in _PEER_REVIEWERS
        if agent_id in latest_by_agent and latest_by_agent[agent_id].get("id")
    ]
    preserved_challenges: list[str] = []
    for message in latest_by_agent.values():
        payload = message.get("payload") if isinstance(message.get("payload"), dict) else {}
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        challenges = data.get("challengesPreserved")
        if isinstance(challenges, list):
            preserved_challenges.extend(str(item) for item in challenges if str(item).strip())

    return {
        "requiredReviewerAgentIds": _PEER_REVIEWERS,
        "receivedVerificationMessageIds": received_ids,
        "gateSatisfied": len(received_ids) == len(_PEER_REVIEWERS),
        "blocksApprovalIfIncomplete": True,
        "preservedChallenges": preserved_challenges[:6],
    }
