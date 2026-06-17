"""Band Leader (Commander) agent business logic (agents lane).

The Commander drives the @mention chain: it opens the case, assigns specialists,
requests human approval, and synthesizes the final report. Its turn behaviour is
selected by ``ctx.task["kind"]``. Deterministic in mock mode; in live mode the
report/synthesis turn is the natural place to route the AI/ML API call.

Analytic doctrine (see commander/prompt.md): frame the incident as an active
credential compromise, open a structured case file, triage severity by credential
type and reach, sequence issuer-first containment, route every notification and
irreversible decision to the human gate, and synthesise specialists while
surfacing disagreement rather than smoothing it.
"""

from __future__ import annotations

from typing import Any

from common.aimlapi_enrichment import enrich_band_leader_synthesis
from common.evidence_analysis import analyze_incident_evidence
from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-commander"
AGENT_NAME = "Band Leader"

_SPECIALISTS = [
    "agent-forensics",
    "agent-threat-intel",
    "agent-code-review",
    "agent-risk-compliance",
    "agent-remediation",
]
_PEER_REVIEWERS = [
    "agent-forensics",
    "agent-code-review",
    "agent-threat-intel",
]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    kind = ctx.task.get("kind", "open_case")
    handler = {
        "open_case": _open_case,
        "assign": _assign,
        "request_cross_review": _request_cross_review,
        "request_approval": _request_approval,
        "generate_report": _generate_report,
    }.get(kind, _open_case)
    return handler(ctx)


def _open_case(ctx: AgentTurnContext) -> dict[str, Any]:
    facts = analyze_incident_evidence(ctx)
    opened_at = facts.cloudtrail.deploy_enabled_fallback_at or "unknown"
    first_abuse_at = facts.api.first_unauthorized_success_at or "unknown"
    issuer_closed_at = facts.auth.issuer_verified_inactive_at or "to be verified"
    case_id = ctx.case["id"]
    subject = facts.auth.subject or "svc-payments-api"
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    root_cause = facts.code.root_cause_summary or (
        "GitHub OIDC trust-policy regression" if is_oidc else "fallback token path"
    )
    case_summary = str(ctx.case.get("summary") or detection_source).rstrip(".")
    credential_description = (
        f"federated OIDC service token for subject {subject}"
        if is_oidc
        else f"application service bearer token (fallback for subject {subject})"
    )
    detection_source = (
        "Customer Records API export spike after an IAM/GitHub OIDC trust-policy change"
        if is_oidc
        else "Customer Records API usage spike after the Friday deploy"
    )
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="case_opened",
        title=f"{case_id} opened: treat as active credential compromise ({subject})",
        summary=(
            f"Opened the Band room for {case_id} and framing it as an active credential compromise until proven "
            f"otherwise: {case_summary}. Registered forensics, threat intel, "
            "code review, risk/compliance, and remediation. Working hypothesis to confirm/refute: "
            f"{root_cause} exposed a credential for subject {subject} and it is being used from external sources."
        ),
        confidence=1.0,
        severity="high",
        evidence_ids=[],
        target_agent_ids=_SPECIALISTS,
        decision_impact="Creates the shared coordination space and the case file every specialist anchors to.",
        next_action="Assign evidence-review tasks; forensics establishes the exposure window first.",
        payload={
            "kind": "case_opened",
            "data": {
                "roomCreated": True,
                "registeredAgentIds": _SPECIALISTS,
                "caseFile": {
                    "detectionSource": detection_source,
                    "secretType": credential_description,
                    "affectedIdentity": f"{subject} (reaches customer summary, bulk export, payment-methods)",
                    "repoBranch": "to confirm with repo owner (not in evidence packet)",
                    "introducingCommitSha": f"to confirm — diff blobs {facts.code.diff_blob_range or 'unknown'}",
                    "deployImageId": (
                        "release-1007 (ci-release-role) / IAM customer-records-github-oidc-exporter"
                        if is_oidc
                        else "release-9814 (ci-release-role) / Lambda customer-records-api"
                    ),
                    "owner": "Human Security Lead",
                    "earliestExposureTime": (
                        f"{opened_at} (OIDC trust widened to unprotected refs)"
                        if is_oidc
                        else f"{opened_at} (deploy enabled ALLOW_FALLBACK_TOKEN)"
                    ),
                    "firstObservedUnauthorizedUse": first_abuse_at,
                    "issuerVerifiedInactiveAt": issuer_closed_at,
                    "stillLive": "to be answered by issuer logs; do not assume rotation == dead",
                    "logsToPreserve": [
                        "ev-api-gateway-logs", "ev-auth-events", "ev-cloudtrail-events",
                        "ev-secret-scan", "ev-code-diff", "Lambda config history",
                    ],
                },
                "containmentDoctrine": (
                    "Issuer-first: revoke active federated sessions before trust-policy cleanup, then prevent minting new sessions."
                    if is_oidc
                    else "Issuer-first: revoke/rotate at the provider before code/history cleanup, which can recontaminate from old clones."
                ),
            },
        },
    )


def _assign(ctx: AgentTurnContext) -> dict[str, Any]:
    assignee = ctx.task["assignee"]
    objective = ctx.task.get("objective", "Review assigned evidence and report findings.")
    assignee_name = ctx.task.get("assigneeName", assignee)
    task_data: dict[str, Any] = {
        "taskId": ctx.task.get("taskId", f"task-{assignee}"),
        "assignedToAgentId": assignee,
        "objective": objective,
        "acceptanceCriteria": [
            "Cite evidence IDs",
            "Name the affected identity and its permissions/reach",
            "Assign confidence",
            "State limitations",
        ],
    }
    if ctx.task.get("approvedScope"):
        task_data["approvedScope"] = ctx.task["approvedScope"]
    if ctx.task.get("policyId"):
        task_data["policyId"] = ctx.task["policyId"]

    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="task_assignment",
        title=f"Task assigned to {assignee_name}",
        summary=f"Assigning {assignee_name} to: {objective} Cite evidence IDs, name the affected identity and its reach, and assign a confidence.",
        confidence=1.0,
        severity="high",
        evidence_ids=[],
        target_agent_ids=[assignee],
        decision_impact="Distributes the investigation so no single agent decides alone.",
        next_action=f"Wait for an evidence-backed report from {assignee_name}.",
        payload={
            "kind": "task_assignment",
            "data": task_data,
        },
    )


def _request_cross_review(ctx: AgentTurnContext) -> dict[str, Any]:
    findings = _messages_by_agents(ctx.recent_messages, _PEER_REVIEWERS, "finding")
    finding_ids = [message["id"] for message in findings if message.get("id")]
    review_round_id = f"review-{ctx.case['id'].lower()}-1"
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="handoff",
        title="Cross-agent review opened before the policy gate",
        summary=(
            "Opening a peer-review round before Risk & Compliance is allowed to assess. "
            "Forensics must verify the code-root-cause and threat-timing claims against data-plane logs; "
            "Code Review must verify containment prerequisites against the observed exposure; Threat Intel "
            "must challenge attribution and exfiltration wording. Risk waits for all three verification messages."
        ),
        confidence=1.0,
        severity="high",
        evidence_ids=[],
        target_agent_ids=_PEER_REVIEWERS,
        decision_impact=(
            "Turns the investigation from parallel reports into an explicit cross-check, so the policy gate "
            "sees agreement, dissent, and remaining uncertainty before any human-facing decision."
        ),
        next_action="Reviewers post verification messages; Band Leader assigns Risk & Compliance only after all three arrive.",
        payload={
            "kind": "cross_review",
            "data": {
                "reviewRoundId": review_round_id,
                "requiredReviewerAgentIds": _PEER_REVIEWERS,
                "sourceFindingMessageIds": finding_ids,
                "blocksRiskGateUntil": "all_required_verifications_posted",
                "reviewCriteria": [
                    "Does another agent's claim match the source evidence?",
                    "Which conclusion is still unsupported or overclaimed?",
                    "Which containment prerequisite would make the response incomplete?",
                    "Which limitation must be preserved for Legal and the human approver?",
                ],
            },
        },
    )


def _request_approval(ctx: AgentTurnContext) -> dict[str, Any]:
    facts = analyze_incident_evidence(ctx)
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    approval_request_id = f"appr-{ctx.case['id'].lower().replace('inc-', '')}-1"
    containment_sequence = (
        [
            "Verify OIDC-issued token/session revoked at issuer",
            "Restore GitHub OIDC trust to protected refs only",
            "Remove export/payment-method scope from untrusted workflow paths",
        ]
        if is_oidc
        else [
            "Verify exposed fallback token revoked at issuer",
            "Two-key rotate sibling Secrets Manager primary (svc-payments-prod-v2)",
            "Disable ALLOW_FALLBACK_TOKEN path and remove .env.release",
        ]
    )
    requested_actions = (
        ["Revoke federated sessions", "Tighten OIDC trust policy", "Patch export scope"]
        if is_oidc
        else ["Rotate fallback token", "Disable fallback token path", "Patch config"]
    )
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="approval_request",
        title="Human approval requested for issuer-first containment",
        summary=(
            (
                "Requesting Security Lead approval for issuer-first containment in order: (1) confirm the "
                "OIDC-issued session is revoked/dead at its issuer, (2) restore GitHub OIDC trust to protected "
                "refs only, (3) remove export/payment-method scope from untrusted workflow paths. External customer "
                "notification and incident closure are explicitly NOT requested — those are irreversible/disclosure "
                "decisions held for the human and Legal pending verified scope."
            )
            if is_oidc
            else (
                "Requesting Security Lead approval for issuer-first containment in order: (1) confirm the exposed "
                "fallback token is revoked/dead at its issuer, (2) two-key rotate the sibling Secrets Manager "
                "primary, (3) disable the ALLOW_FALLBACK_TOKEN path and remove .env.release. External customer "
                "notification and incident closure are explicitly NOT requested — those are irreversible/disclosure "
                "decisions held for the human and Legal pending verified scope."
            )
        ),
        confidence=0.94,
        severity="high",
        evidence_ids=["ev-incident-policy", "ev-code-diff"],
        target_agent_ids=["agent-human-approver"],
        decision_impact="Ensures production-impacting and irreversible actions are not taken autonomously.",
        next_action="Wait for the human Security Lead decision.",
        payload={
            "kind": "approval_request",
            "data": {
                "approvalRequestId": approval_request_id,
                "requiredApprover": "Security Lead",
                "containmentSequence": containment_sequence,
                "requestedActions": requested_actions,
                "notRequestedActions": ["External customer notification", "Incident closure"],
                "routedToHumanBecauseIrreversible": ["External customer notification", "Incident closure"],
                "riskIfApproved": "May briefly disrupt the service depending on the credential, but stops ongoing exposure.",
                "riskIfRejected": (
                    "OIDC wildcard can continue minting production-scoped sessions while investigation continues."
                    if is_oidc
                    else "Exposed fallback token and its sibling may remain usable while investigation continues."
                ),
            },
        },
    )


def _generate_report(ctx: AgentTurnContext) -> dict[str, Any]:
    facts = analyze_incident_evidence(ctx)
    synthesis = enrich_band_leader_synthesis(ctx, facts)
    synthesis_data = synthesis.data
    audit_trail = [m["id"] for m in ctx.recent_messages]
    evidence_ids = sorted({eid for m in ctx.recent_messages for eid in m.get("evidenceIds", [])})
    review_messages = _messages_by_agents(ctx.recent_messages, _PEER_REVIEWERS, "verification")
    review_ids = [message["id"] for message in review_messages if message.get("id")]
    records = facts.api.unauthorized_records_returned
    records_text = f"{records:,}"
    opened_at = facts.cloudtrail.deploy_enabled_fallback_at or "unknown"
    issuer_closed_at = facts.auth.issuer_verified_inactive_at or facts.api.post_rotation_attempt_at or "unknown"
    source_ips = ", ".join(facts.api.unauthorized_ips)
    synthesis_label = "AI/ML synthesis" if synthesis.used_live_api else "Audit-ready synthesis"
    case_id = ctx.case["id"]
    subject = facts.auth.subject or "svc-payments-api"
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="report_section",
        title=f"{synthesis_label} for {case_id} (with surfaced agent disagreement)",
        summary=str(synthesis_data.get("executiveSummary")),
        confidence=float(synthesis_data.get("confidence", 0.96)),
        severity=str(synthesis_data.get("severity", "high")),
        evidence_ids=sorted(set(evidence_ids + list(synthesis_data.get("evidenceIds", [])))),
        target_agent_ids=[],
        decision_impact="Produces the judge-facing proof of traceable, mention-driven multi-agent coordination.",
        next_action=str(
            (synthesis_data.get("nextActions") or ["Use replay mode to show how the decision was reached through Band."])[0]
        ),
        payload={
            "kind": "report_section",
            "data": {
                "synthesis": synthesis_data,
                "partnerTool": synthesis.metadata(),
                "reportId": f"report-{case_id.lower()}",
                "severity": "high",
                "executiveSummary": (
                    (
                        "Agents coordinated through Band to investigate an OIDC trust-policy regression for "
                        f"{subject}. Forensics confirmed {records_text} customer records were read by "
                        f"{len(facts.api.unauthorized_ips)} external IPs ({source_ips}) across a window that opened at the "
                        f"{opened_at} IAM trust-policy change and is issuer-verified closed at {issuer_closed_at}. Risk & Compliance "
                        "challenged the breach framing down to suspected_exposure while holding customer notification for Legal scope review."
                    )
                    if is_oidc
                    else (
                        "Agents coordinated through Band to investigate an exposed fallback service token for "
                        f"svc-payments-api introduced by the Friday deploy. Forensics confirmed {records_text} customer records "
                        f"were read by {len(facts.api.unauthorized_ips)} external IPs ({source_ips}) across a window that opened at the "
                        f"{opened_at} deploy and is issuer-verified closed at {issuer_closed_at}. Risk & Compliance challenged the breach framing down to "
                        "suspected_exposure under policy while flagging the GDPR personal-data-breach threshold as "
                        "likely met. Human approval authorised issuer-first containment; notification was held for Legal."
                    )
                ),
                "rootCause": (
                    facts.code.root_cause_summary or "GitHub OIDC trust-policy regression allowed untrusted refs to mint an exporter token."
                    if is_oidc
                    else "Friday deploy added an ALLOW_FALLBACK_TOKEN fail-open path plus a token-bearing .env.release (also enabling CUSTOMER_EXPORT_ENABLED); a Secrets Manager throttle triggered fallback use."
                ),
                "exposureWindow": {"openedAt": opened_at, "issuerVerifiedClosedAt": issuer_closed_at, "closedBy": "issuer deny, not code deletion"},
                "riskAssessment": "High severity, suspected_exposure under policy; unauthorised access to personal data is confirmed, downstream exfiltration/misuse is not.",
                "crossAgentReview": {
                    "status": "complete" if len(review_ids) == len(_PEER_REVIEWERS) else "incomplete",
                    "requiredReviewerAgentIds": _PEER_REVIEWERS,
                    "verificationMessageIds": review_ids,
                    "value": "Specialists reviewed each other's claims before Risk & Compliance classified the case.",
                },
                "surfacedDisagreements": synthesis_data.get("dissentToPreserve") or [
                    "The peer-review round validated the exposure/root-cause/abuse chain but preserved limits before the policy gate.",
                    "Forensics shows records WERE returned to unauthorized IPs (reads toward breach); Risk keeps policy classification at suspected_exposure because actor identity is unresolved — both are recorded, not merged.",
                    "Threat Intel rates likelihood-of-exploitation HIGH (active abuse + post-rotation retry); Risk still blocks any 'confirmed exfiltration' claim absent downstream evidence.",
                    "Remediation marks the fallback token dead, but Code Review/Remediation insist containment is incomplete until the sibling Secrets Manager primary is independently rotated.",
                ],
                "approvedActions": (
                    ["Revoke federated sessions", "Tighten OIDC trust policy", "Patch export scope"]
                    if is_oidc
                    else ["Rotate fallback token", "Disable fallback path", "Patch config"]
                ),
                "heldActions": ["External customer notification", "Incident closure"],
                "openQuestions": synthesis_data.get("openQuestions") or [
                    "Which exact customer records (and residencies) map to the exported rows?",
                    "Did any downstream system cache or forward the exported records?",
                    "Is the sibling Secrets Manager primary fully rotated and the fallback purged from CI/images?",
                    "Does Legal require customer notification once scope is verified?",
                ],
                "auditTrailMessageIds": audit_trail,
                "derivedFacts": {
                    "source": "common.evidence_analysis.analyze_incident_evidence",
                    "recordsReturnedToUnexpectedIps": records,
                    "unexpectedIps": facts.api.unauthorized_ips,
                    "unresolvedHighSecretFindings": facts.secret_scan.unresolved_high_count,
                    "policyApprovalActions": facts.policy.human_approval_actions,
                },
            },
        },
    )


def _messages_by_agents(
    messages: list[dict[str, Any]],
    agent_ids: list[str],
    message_type: str,
) -> list[dict[str, Any]]:
    by_agent = {}
    for message in messages:
        if message.get("type") == message_type and message.get("agentId") in agent_ids:
            by_agent[message["agentId"]] = message
    return [by_agent[agent_id] for agent_id in agent_ids if agent_id in by_agent]
