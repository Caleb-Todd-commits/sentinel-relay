"""Threat Intel agent business logic (agents lane).

Assesses the source IPs and behavior, deliberately refusing real-world
attribution overreach (the IPs are documentation-range demo indicators).
Deterministic in mock mode.

Analytic doctrine (see threat_intel/prompt.md): assess exposure velocity
(commodity scanners find and abuse leaked secrets fast), read the abuse and
monetisation path for THIS credential type, and give a likelihood-of-exploitation
view rather than restating that a secret leaked.
"""

from __future__ import annotations

from typing import Any

from common.evidence_analysis import analyze_incident_evidence
from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-threat-intel"
AGENT_NAME = "Threat Intel Agent"

_EVIDENCE = ["ev-ip-intel", "ev-api-gateway-logs"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    if ctx.task.get("kind") == "cross_review":
        return _cross_review(ctx)

    facts = analyze_incident_evidence(ctx)
    minutes_to_abuse = facts.threat.minutes_from_deploy_to_abuse
    minutes_text = f"~{minutes_to_abuse} minutes" if minutes_to_abuse is not None else "within minutes"
    unexpected_ips = ", ".join(facts.threat.unexpected_ips)
    expected_ips = ", ".join(facts.threat.expected_ips) or "expected production egress"
    automation_agents = ", ".join(facts.threat.automation_user_agents)
    post_rotation_retry = ", ".join(facts.threat.post_rotation_retry_ips) or "an external source"
    canary_probe_ips = ", ".join(facts.threat.canary_probe_ips) or "an external source"
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    velocity_assessment = (
        "Fast mint-to-use timing is consistent with an untrusted workflow exercising newly broadened OIDC trust."
        if is_oidc
        else "Leaked tokens committed to env/config files are routinely found and exercised within minutes by commodity scanners and secret-hunting crawlers; the timing here fits opportunistic automation, not a slow targeted operation."
    )
    credential_type = (
        "OIDC-issued customer-records exporter token (read access to customer export + payment-methods)"
        if is_oidc
        else "customer-records service bearer token (read access to customer PII + payment-methods)"
    )
    objective = (
        "bulk export through a federated CI credential that should have been limited to protected refs"
        if is_oidc
        else "bulk exfiltration of customer PII / payment-method data"
    )

    findings = [
        {
            "claim": (
                "Discovery-to-abuse velocity is consistent with automated secret hunting: "
                f"{minutes_text} from the {facts.cloudtrail.deploy_enabled_fallback_at or 'deploy'} deploy "
                f"to first external use at {facts.api.first_unauthorized_success_at or 'unknown'}."
            ),
            "evidenceRef": "ev-api-gateway-logs",
            "source": "api_gateway_logs.jsonl",
            "observation": velocity_assessment,
        },
        {
            "claim": (
                f"{len(facts.threat.unexpected_ips)} off-baseline external IPs used the token; {expected_ips} is expected CI/prod egress "
                "and must not be miscounted as hostile."
            ),
            "evidenceRef": "ev-ip-intel",
            "source": "suspicious_ips.json",
            "observation": (
                f"{unexpected_ips} used automation user agents ({automation_agents}) during the spike; "
                f"{canary_probe_ips} probed a canary path; {expected_ips} is the known payments worker egress."
            ),
        },
        {
            "claim": (
                f"Behavior shows intent to retain access: {post_rotation_retry} attempted another request AFTER "
                "rotation, raising likelihood this is active abuse rather than incidental exposure."
            ),
            "evidenceRef": "ev-ip-intel",
            "source": "suspicious_ips.json",
            "observation": "Post-rotation retry at 21:12:02Z indicates the source was actively working the token, not a passive scan that moved on.",
        },
    ]
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="finding",
        title=(
            "High likelihood of exploitation: fast OIDC minting, bulk export path, retry after revocation"
            if is_oidc
            else "High likelihood of exploitation: fast automated discovery, bulk PII abuse path, attacker persistence"
        ),
        summary=(
            (
                "Assessing this as active abuse of a federated Customer Records exporter token. The "
                f"{minutes_text} gap from trust-policy change to first external use fits fast OIDC mint-and-use "
                "behavior after a CI permission regression; the access pattern (bulk export, payment-method read, "
                f"canary probe) shows a useful data-abuse path, and a post-revocation retry by {post_rotation_retry} "
                "shows the source wanted to keep access. Likelihood of exploitation is HIGH. Indicators are "
                "documentation-range demo IPs, so no real-world actor attribution is claimed."
            )
            if is_oidc
            else (
                "Assessing this as active abuse of an exposed customer-records bearer token. The "
                f"{minutes_text} gap from deploy to first external use fits commodity secret-scanning velocity, "
                "the access pattern (canary probe then bulk and VIP export) is a classic enumerate-then-exfiltrate "
                f"PII monetisation path, and a post-rotation retry by {post_rotation_retry} shows the source wanted "
                "to keep access. Likelihood of exploitation is HIGH. Indicators are documentation-range demo IPs, "
                "so no real-world actor attribution is claimed."
            )
        ),
        confidence=0.74,
        severity="medium",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact=(
            "Raises this from 'a secret leaked' to 'an exposed credential is being actively abused', which "
            "should drive urgency on containment and on the breach-notification assessment."
        ),
        next_action="Risk & Compliance should treat this as active unauthorized use feeding the GDPR/CCPA assessment, not yet as attributed breach.",
        payload={
            "kind": "finding",
            "data": {
                "findings": findings,
                "exposureVelocity": {
                    "deployAt": facts.cloudtrail.deploy_enabled_fallback_at,
                    "firstAbuseAt": facts.api.first_unauthorized_success_at,
                    "minutesToAbuse": minutes_to_abuse,
                    "assessment": "Within the minutes-to-hours window typical of automated secret discovery; supports opportunistic-then-hands-on abuse.",
                },
                "credentialAbusePath": {
                    "credentialType": credential_type,
                    "likelyObjective": objective,
                    "monetisation": [
                        "Resale of customer + payment-method records on data markets",
                        "Account-takeover / payment fraud against affected customers",
                        "Extortion of the platform over the export",
                    ],
                    "observedTradecraft": (
                        ["OIDC token minting from untrusted ref", "bulk paginated export", "payment-method read", "post-revocation retry"]
                        if is_oidc
                        else ["canary/seed-path probing", "bulk paginated export", "targeting the VIP segment", "post-rotation retry"]
                    ),
                },
                "likelihoodOfExploitation": "high",
                "strongestSignals": [
                    "confirmed use by unexpected external IPs (not just exposure)",
                    f"automation user agents ({automation_agents}) off the worker baseline",
                    "enumerate-then-export sequence",
                    "post-rotation persistence attempt",
                    "discovery-to-abuse timing consistent with automated scanning",
                ],
                "weakSignals": ["raw IP reputation alone", "geo of documentation-range IPs"],
                "limitations": [
                    "Documentation-range IPs; do NOT claim real-world threat-actor attribution or geolocation.",
                    "Cannot confirm resale or downstream use; monetisation paths are assessed, not observed.",
                ],
                "derivedFacts": {
                    "source": "common.evidence_analysis.analyze_incident_evidence",
                    "unexpectedIps": facts.threat.unexpected_ips,
                    "expectedIps": facts.threat.expected_ips,
                    "postRotationRetryIps": facts.threat.post_rotation_retry_ips,
                    "canaryProbeIps": facts.threat.canary_probe_ips,
                    "automationUserAgents": facts.threat.automation_user_agents,
                },
            },
        },
    )


def _cross_review(ctx: AgentTurnContext) -> dict[str, Any]:
    facts = analyze_incident_evidence(ctx)
    minutes_to_abuse = facts.threat.minutes_from_deploy_to_abuse
    minutes_text = f"~{minutes_to_abuse} minutes" if minutes_to_abuse is not None else "within minutes"
    unexpected_ips = ", ".join(facts.threat.unexpected_ips)
    post_rotation_retry = ", ".join(facts.threat.post_rotation_retry_ips) or "an external source"
    records_text = f"{facts.api.unauthorized_records_returned:,}"
    subject = facts.auth.subject or "svc-payments-api"
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    review_round_id = str(ctx.task.get("reviewRoundId") or f"review-{ctx.case['id'].lower()}-1")
    reviewed_message_ids = _latest_message_ids(
        ctx,
        {
            "agent-forensics": "finding",
            "agent-code-review": "finding",
        },
    )
    abuse_path = (
        "OIDC minting from an untrusted workflow followed by bulk export and payment-method reads"
        if is_oidc
        else "secret-scanner-style token use followed by canary probing, bulk export, and payment-method reads"
    )

    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="verification",
        title="Peer review: exploitation likelihood is high, attribution remains unsupported",
        summary=(
            f"Reviewed Forensics and Code Review before the policy gate. Their chain is coherent: {subject} became usable "
            f"through the root-cause control failure, unexpected IPs ({unexpected_ips}) used it {minutes_text} after the "
            f"opening change, {records_text} records were returned, and {post_rotation_retry} retried after revocation. "
            "I validate high exploitation likelihood, but challenge any named-actor, geolocation, or downstream reuse/resale claim."
        ),
        confidence=0.78,
        severity="medium",
        evidence_ids=sorted(set(_EVIDENCE + ["ev-auth-events", "ev-code-diff"])),
        target_agent_ids=["agent-commander"],
        decision_impact=(
            "Keeps urgency high for containment while preventing the investigation from overstating attribution "
            "or downstream impact before Legal/customer-scope review."
        ),
        next_action="Risk should classify active unauthorized use as high severity while holding attribution and notification scope for human review.",
        payload={
            "kind": "cross_review_verification",
            "data": {
                "reviewRoundId": review_round_id,
                "reviewerAgentId": AGENT_ID,
                "reviewedAgentIds": ["agent-forensics", "agent-code-review"],
                "reviewedMessageIds": reviewed_message_ids,
                "verifiedClaims": [
                    f"Forensics' record-return evidence supports active unauthorized use, not mere exposure: {records_text} records.",
                    f"Code Review's root-cause path explains the observed abuse path: {abuse_path}.",
                    "Post-revocation retry supports persistence/active abuse and raises urgency.",
                ],
                "challengesPreserved": [
                    "Do not claim real-world threat-actor attribution from documentation-range IPs.",
                    "Do not claim downstream resale, fraud, or reuse without external evidence.",
                    "Do not turn high likelihood into certainty; keep confidence below verified until scope review completes.",
                ],
                "derivedFacts": {
                    "source": "common.evidence_analysis.analyze_incident_evidence",
                    "unexpectedIps": facts.threat.unexpected_ips,
                    "expectedIps": facts.threat.expected_ips,
                    "minutesToAbuse": minutes_to_abuse,
                    "postRotationRetryIps": facts.threat.post_rotation_retry_ips,
                    "rootCauseKind": facts.code.root_cause_kind,
                },
            },
        },
    )


def _latest_message_ids(ctx: AgentTurnContext, wanted: dict[str, str]) -> list[str]:
    ids: list[str] = []
    for agent_id, message_type in wanted.items():
        for message in reversed(ctx.recent_messages):
            if message.get("agentId") == agent_id and message.get("type") == message_type and message.get("id"):
                ids.append(str(message["id"]))
                break
    return ids
