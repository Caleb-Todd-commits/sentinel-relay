"""Forensics agent business logic (agents lane).

Reads the gateway / auth / CloudTrail evidence and reports the measured exposure.
Deterministic in mock mode; an LLM enrichment layer can wrap ``handle_turn`` for
live mode without changing the transport seam.

Analytic doctrine (see forensics/prompt.md): establish the exposure window from
the introducing deploy to issuer-verified credential death, pull issuer/provider
identity logs tied to the principal, separate "exposed" from "actually used", and
be explicit about the control-plane vs data-plane logging split.
"""

from __future__ import annotations

from typing import Any

from common.evidence_analysis import analyze_incident_evidence
from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-forensics"
AGENT_NAME = "Forensics Agent"

_EVIDENCE = ["ev-api-gateway-logs", "ev-auth-events", "ev-cloudtrail-events"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    if ctx.task.get("kind") == "cross_review":
        return _cross_review(ctx)

    facts = analyze_incident_evidence(ctx)
    records = facts.api.unauthorized_records_returned
    records_text = f"{records:,}"
    source_ips = ", ".join(facts.api.unauthorized_ips)
    opened_at = facts.cloudtrail.deploy_enabled_fallback_at or "unknown"
    fallback_loaded_at = facts.auth.fallback_loaded_at or "unknown"
    first_use_at = facts.api.first_unauthorized_success_at or facts.auth.first_external_use_at or "unknown"
    rotation_started_at = facts.auth.rotation_started_at or "unknown"
    issuer_closed_at = facts.auth.issuer_verified_inactive_at or facts.api.post_rotation_attempt_at or "unknown"
    subject = facts.auth.subject or "svc-payments-api"
    credential_label = facts.auth.compromised_token_id or facts.auth.fallback_token_id or "svc-payments-fallback-redacted"
    primary_token = facts.auth.primary_token_ids[0] if facts.auth.primary_token_ids else "svc-payments-prod-v2"
    regions = "/".join(facts.api.unauthorized_regions) or "unknown regions"
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    credential_type = (
        "federated service token minted through overbroad GitHub OIDC trust"
        if is_oidc
        else "static application service bearer token (fallback)"
    )
    credential_first_seen_at = facts.auth.credential_first_observed_at or fallback_loaded_at
    mechanism = facts.auth.credential_mechanism or ("overbroad OIDC trust" if is_oidc else "static fallback bearer token")
    opener = (
        f"IAM trust-policy update: {facts.cloudtrail.configuration_change_event_name or 'configuration change'} on "
        f"{facts.cloudtrail.function_name or 'customer-records exporter role'}"
        if is_oidc
        else "deploy: UpdateFunctionConfiguration set ALLOW_FALLBACK_TOKEN=true (release-9814)"
    )

    # Findings are evidence-anchored and ordered the way a SOC analyst reconstructs
    # the kill chain: window -> credential identity -> use vs mere exposure.
    if is_oidc:
        findings = [
            {
                "claim": (
                    f"Exposure window opened with the IAM trust-policy change at {opened_at} and is "
                    f"issuer-verified closed at {issuer_closed_at}; revocation, not policy cleanup alone, "
                    "is what closed the active token."
                ),
                "evidenceRef": "ev-cloudtrail-events",
                "source": "cloudtrail_events.jsonl",
                "observation": (
                    f"{facts.cloudtrail.configuration_change_event_name or 'configuration change'} widened "
                    f"{facts.cloudtrail.function_name or 'the OIDC exporter role'} at {opened_at}; STS then "
                    f"issued {credential_label} at {credential_first_seen_at} from an untrusted workflow."
                ),
            },
            {
                "claim": (
                    f"Compromised principal is {subject} via {mechanism}; this is a federated credential "
                    "control failure, not a committed static secret."
                ),
                "evidenceRef": "ev-auth-events",
                "source": "auth_events.jsonl",
                "observation": (
                    f"{facts.auth.credential_event_type or 'credential event'} at {credential_first_seen_at} "
                    f"issued token label {credential_label}; the normal production credential is {primary_token}."
                ),
            },
            {
                "claim": (
                    f"The federated token was actively USED by {len(facts.api.unauthorized_ips)} off-baseline "
                    "external sources for export and payment-method reads."
                ),
                "evidenceRef": "ev-auth-events",
                "source": "auth_events.jsonl",
                "observation": (
                    f"{source_ips} used {credential_label} starting at {first_use_at}. "
                    f"A post-revocation retry at {facts.api.post_rotation_attempt_at or issuer_closed_at} was DENIED "
                    f"({', '.join(facts.auth.deny_signals) or 'token_revoked, post_rotation_attempt'})."
                ),
            },
            {
                "claim": (
                    f"Gateway data-plane logs quantify {records_text} customer records returned to "
                    "unauthorized IPs; expected analytics-worker traffic is excluded."
                ),
                "evidenceRef": "ev-api-gateway-logs",
                "source": "api_gateway_logs.jsonl",
                "observation": (
                    f"{len(facts.api.export_breakdown)} successful federated-token responses returned records "
                    f"from {regions}; denied scopes: {', '.join(facts.api.denied_scope_endpoints) or 'none observed'}."
                ),
            },
        ]
    else:
        findings = [
            {
                "claim": (
                    f"Exposure window opened with the Friday deploy at {opened_at} and is issuer-verified "
                    f"closed at {issuer_closed_at}; rotation alone did not close it — the issuer deny did."
                ),
                "evidenceRef": "ev-cloudtrail-events",
                "source": "cloudtrail_events.jsonl",
                "observation": (
                    f"UpdateFunctionConfiguration set ALLOW_FALLBACK_TOKEN=true at {opened_at} "
                    f"({facts.cloudtrail.release_role or 'release role unknown'}); Secrets Manager "
                    f"GetSecretValue threw ThrottlingException at {facts.cloudtrail.secret_throttle_at or 'unknown'}, "
                    "forcing the fallback path."
                ),
            },
            {
                "claim": (
                    f"Compromised principal is the service identity {subject} via its "
                    f"STATIC fallback bearer token {credential_label}, not an AWS "
                    "IAM key — blast radius is whatever that subject can call on Customer Records."
                ),
                "evidenceRef": "ev-auth-events",
                "source": "auth_events.jsonl",
                "observation": (
                    f"fallback_token_loaded at {fallback_loaded_at} (signals: secret_manager_timeout, "
                    f"fallback_enabled); same subject normally served by {primary_token}."
                ),
            },
            {
                "claim": (
                    f"Token was not merely exposed but actively USED by {len(facts.api.unauthorized_ips)} off-baseline external "
                    "sources, including enumeration-then-export and a retry after rotation."
                ),
                "evidenceRef": "ev-auth-events",
                "source": "auth_events.jsonl",
                "observation": (
                    f"{source_ips} used the fallback token starting at {first_use_at}. "
                    f"One source retried at {facts.api.post_rotation_attempt_at or issuer_closed_at} and was DENIED "
                    f"({', '.join(facts.auth.deny_signals) or 'token_revoked, post_rotation_attempt'})."
                ),
            },
            {
                "claim": (
                    f"Gateway data-plane logs quantify {records_text} customer records returned to "
                    "unauthorized IPs before rotation; benign prod worker traffic is excluded."
                ),
                "evidenceRef": "ev-api-gateway-logs",
                "source": "api_gateway_logs.jsonl",
                "observation": (
                    f"{len(facts.api.export_breakdown)} successful fallback-token responses returned records from "
                    f"{regions}; denied scopes: {', '.join(facts.api.denied_scope_endpoints) or 'none observed'}. "
                    f"Post-rotation export was denied at {facts.api.post_rotation_attempt_at or 'unknown'}."
                ),
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
            f"{subject} federated token: {records_text} records read across a verified-closed window"
            if is_oidc
            else f"{subject} fallback token: {records_text} records read across a verified-closed window"
        ),
        summary=(
            (
                "Treating this as an active credential compromise: an overbroad GitHub OIDC trust issued "
                f"{credential_label} for subject {subject} at {credential_first_seen_at}; it was then used "
                f"by {len(facts.api.unauthorized_ips)} off-baseline external IPs ({source_ips}) to read "
                f"{records_text} customer records until the issuer verified the token dead at {issuer_closed_at}. "
                f"The exposure window opened at the {opened_at} IAM trust-policy change, not at first abuse; "
                f"rotation started {rotation_started_at} but the window only closes on the issuer deny. Records "
                "were returned to unauthorized sources, but actor identity and downstream reuse are unproven."
            )
            if is_oidc
            else (
                "Treating this as an active credential compromise: the static fallback bearer token for "
                f"subject {subject} was loaded after a Secrets Manager throttle ({fallback_loaded_at}) and then "
                f"used by {len(facts.api.unauthorized_ips)} off-baseline external IPs ({source_ips}) to read "
                f"{records_text} customer records (bulk export + payment-methods) until the issuer verified "
                f"the token dead at {issuer_closed_at}. The exposure window opened at the {opened_at} deploy, "
                f"not at first abuse; rotation started {rotation_started_at} but the window only closes on "
                f"the issuer deny. Records were returned to unauthorized sources, but actor identity and any "
                "downstream reuse are unproven from logs alone."
            )
        ),
        confidence=0.86,
        severity="high",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact=(
            "Quantifies confirmed unauthorized data-plane access and fixes the exposure window for the "
            "legal clock, but does not by itself prove actor identity or downstream misuse."
        ),
        next_action=(
            "Risk & Compliance should classify severity and the breach-notification posture; Code Review "
            "should hunt for sibling credentials that survive rotation. Do not yet claim confirmed exfiltration."
        ),
        payload={
            "kind": "finding",
            "data": {
                "findings": findings,
                "compromisedIdentity": {
                    "subject": subject,
                    "credentialType": credential_type,
                    "credentialLabel": credential_label,
                    "notAnIamOrCloudKey": not is_oidc,
                    "reachableScope": [
                        "/v1/customers/summary",
                        "/v1/customers/export (bulk)",
                        "/v1/customers/{id}/payment-methods (sensitive)",
                    ],
                    "deniedScope": ["/v1/billing/events/export (403 — outside this subject's grant)"],
                },
                "exposureWindow": {
                    "openedAt": opened_at,
                    "openedBy": opener,
                    "fallbackFirstLoadedAt": fallback_loaded_at,
                    "credentialFirstObservedAt": credential_first_seen_at,
                    "firstUnauthorizedUseAt": first_use_at,
                    "rotationStartedAt": rotation_started_at,
                    "issuerVerifiedInactiveAt": issuer_closed_at,
                    "status": "verified_closed",
                    "note": "A later code deletion would NOT close the window; only the issuer-side deny does.",
                },
                "recordsExportedEstimate": records,
                "exportBreakdown": facts.api.export_breakdown,
                "exposedVsUsed": {
                    "exposed": (
                        "OIDC trust widened to unprotected refs and allowed a preview workflow to mint a production-scoped federated token."
                        if is_oidc
                        else "Fallback token shipped in .env.release and live behind ALLOW_FALLBACK_TOKEN."
                    ),
                    "actuallyUsed": (
                        "Confirmed used: new_ip_for_token + untrusted_workflow, then bulk_access_pattern and canary/payment-method probing."
                        if is_oidc
                        else "Confirmed used: new_ip_for_token + impossible_travel + user_agent_changed, then bulk_access_pattern and a VIP canary_probe->export sequence."
                    ),
                    "offBaseline": f"{', '.join(facts.api.unauthorized_user_agents)} from {regions} vs baseline IP(s) {', '.join(facts.api.baseline_ips)}.",
                },
                "loggingGap": (
                    "Control-plane (CloudTrail) and data-plane (API gateway) logging are separate. Here the "
                    "gateway data-plane captured records_returned, so we can quantify what was read. If "
                    "data-plane logging had been off, CloudTrail would still show the throttle, fallback load, "
                    "and Lambda invokes — i.e. suspicious admin activity — but we could NOT prove customer "
                    "records were actually returned. Absence of data-plane logs is not evidence of no access."
                ),
                "chainOfCustody": {
                    "preservedEvidence": _EVIDENCE,
                    "alsoPreserve": ["ev-secret-scan", "ev-code-diff", "Lambda config history for customer-records-api"],
                    "collectionNote": "Evidence IDs are immutable references collected with deterministic timestamps; do not mutate source logs.",
                },
                "limitations": [
                    "No actor attribution from logs alone (see Threat Intel).",
                    f"Downstream reuse, resale, or caching of the {records_text} records is unverified.",
                    "Exact customer-row identities behind the export counts still need data mapping.",
                ],
                "derivedFacts": {
                    "source": "common.evidence_analysis.analyze_incident_evidence",
                    "unauthorizedSourceIps": facts.api.unauthorized_ips,
                    "unauthorizedSuccessCount": facts.api.unauthorized_success_count,
                    "bulkExportRecords": facts.api.bulk_export_records,
                    "vipExportRecords": facts.api.vip_export_records,
                },
            },
        },
    )


def _cross_review(ctx: AgentTurnContext) -> dict[str, Any]:
    facts = analyze_incident_evidence(ctx)
    records = facts.api.unauthorized_records_returned
    records_text = f"{records:,}"
    source_ips = ", ".join(facts.api.unauthorized_ips)
    opened_at = facts.cloudtrail.deploy_enabled_fallback_at or "unknown"
    first_use_at = facts.api.first_unauthorized_success_at or "unknown"
    issuer_closed_at = facts.auth.issuer_verified_inactive_at or facts.api.post_rotation_attempt_at or "unknown"
    subject = facts.auth.subject or "svc-payments-api"
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    credential = facts.auth.compromised_token_id or facts.auth.fallback_token_id or "redacted credential"
    review_round_id = str(ctx.task.get("reviewRoundId") or f"review-{ctx.case['id'].lower()}-1")
    reviewed_message_ids = _latest_message_ids(
        ctx,
        {
            "agent-code-review": "finding",
            "agent-threat-intel": "finding",
        },
    )

    root_cause_check = (
        "Code Review's OIDC trust-policy finding matches the observed data-plane window: the trust change "
        f"opened at {opened_at}, {credential} was used by unexpected sources, and issuer revocation at "
        f"{issuer_closed_at} is the closure signal."
        if is_oidc
        else (
            "Code Review's fallback-token finding matches the observed data-plane window: the deploy opened "
            f"the path at {opened_at}, the fallback credential was used by unexpected sources, and issuer deny "
            f"at {issuer_closed_at} is the closure signal."
        )
    )
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="verification",
        title="Peer review: data-plane evidence validates root cause and abuse timing",
        summary=(
            f"Reviewed Code Review and Threat Intel before the policy gate. Gateway/auth logs support the "
            f"root-cause and exploitation-timing chain for {subject}: first unauthorized use at {first_use_at}, "
            f"{records_text} records returned to {len(facts.api.unauthorized_ips)} unexpected IPs ({source_ips}), "
            f"and the active window closing only at issuer verification ({issuer_closed_at}). I preserve one "
            "challenge: these logs prove unauthorized reads, not downstream resale, named-actor attribution, or final notification scope."
        ),
        confidence=0.9,
        severity="high",
        evidence_ids=sorted(set(_EVIDENCE + ["ev-code-diff", "ev-ip-intel"])),
        target_agent_ids=["agent-commander"],
        decision_impact=(
            "Gives Risk & Compliance a cross-checked exposure chain while preserving the line between "
            "records returned and downstream misuse."
        ),
        next_action="Code Review and Threat Intel should post their peer checks; Risk should wait until the review round is complete.",
        payload={
            "kind": "cross_review_verification",
            "data": {
                "reviewRoundId": review_round_id,
                "reviewerAgentId": AGENT_ID,
                "reviewedAgentIds": ["agent-code-review", "agent-threat-intel"],
                "reviewedMessageIds": reviewed_message_ids,
                "verifiedClaims": [
                    root_cause_check,
                    (
                        "Threat Intel's high-likelihood assessment is supported by data-plane behavior: "
                        "unexpected IPs, automation user agents, bulk export/payment-method reads, and a post-revocation retry."
                    ),
                ],
                "challengesPreserved": [
                    "Do not convert records-returned evidence into a confirmed downstream resale or reuse claim.",
                    "Do not attribute the source to a named actor from documentation-range IP indicators.",
                    "Do not treat code cleanup as the window close; issuer-side denial is the closure evidence.",
                ],
                "derivedFacts": {
                    "source": "common.evidence_analysis.analyze_incident_evidence",
                    "recordsReturnedToUnexpectedIps": records,
                    "unexpectedIps": facts.api.unauthorized_ips,
                    "firstUnauthorizedUseAt": first_use_at,
                    "issuerVerifiedInactiveAt": issuer_closed_at,
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
