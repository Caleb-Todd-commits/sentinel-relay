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

from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-forensics"
AGENT_NAME = "Forensics Agent"

_EVIDENCE = ["ev-api-gateway-logs", "ev-auth-events", "ev-cloudtrail-events"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    # Findings are evidence-anchored and ordered the way a SOC analyst reconstructs
    # the kill chain: window -> credential identity -> use vs mere exposure.
    findings = [
        {
            "claim": (
                "Exposure window opened with the Friday deploy and is issuer-verified "
                "closed at 21:12:02Z; rotation alone did not close it — the issuer deny did."
            ),
            "evidenceRef": "ev-cloudtrail-events",
            "source": "cloudtrail_events.jsonl",
            "observation": (
                "UpdateFunctionConfiguration set ALLOW_FALLBACK_TOKEN=true at 20:47:11Z "
                "(ci-release-role/release-9814); Secrets Manager GetSecretValue threw "
                "ThrottlingException at 20:55:36Z, forcing the fallback path."
            ),
        },
        {
            "claim": (
                "Compromised principal is the service identity svc-payments-api via its "
                "STATIC fallback bearer token svc-payments-fallback-redacted, not an AWS "
                "IAM key — blast radius is whatever that subject can call on Customer Records."
            ),
            "evidenceRef": "ev-auth-events",
            "source": "auth_events.jsonl",
            "observation": (
                "fallback_token_loaded at 20:55:38Z (signals: secret_manager_timeout, "
                "fallback_enabled); same subject normally served by svc-payments-prod-v2."
            ),
        },
        {
            "claim": (
                "Token was not merely exposed but actively USED by two off-baseline external "
                "sources, including enumeration-then-export and a retry after rotation."
            ),
            "evidenceRef": "ev-auth-events",
            "source": "auth_events.jsonl",
            "observation": (
                "203.0.113.77 first used the token at 21:04:59Z (signals: new_ip_for_token, "
                "impossible_travel, user_agent_changed), then bulk_access_pattern; 198.51.100.188 "
                "ran a canary_probe at 21:08:44Z; 203.0.113.77 retried at 21:12:02Z and was DENIED "
                "(token_revoked, post_rotation_attempt)."
            ),
        },
        {
            "claim": (
                "Gateway data-plane logs quantify 10,227 customer records returned to "
                "unauthorized IPs before rotation; benign prod worker traffic is excluded."
            ),
            "evidenceRef": "ev-api-gateway-logs",
            "source": "api_gateway_logs.jsonl",
            "observation": (
                "Bulk /v1/customers/export 5000+5000 (203.0.113.77, curl/8.1.2, eu-west-3), "
                "two /payment-methods reads of 4 each (customers 42 and 2871), and a VIP export "
                "of 219 (198.51.100.188, python-requests/2.31, us-west-2). /v1/billing/events/export "
                "was 403 (out of scope) and the post-rotation export was 401."
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
        title="svc-payments-api fallback token: 10,227 records read across a verified-closed window",
        summary=(
            "Treating this as an active credential compromise: the static fallback bearer token for "
            "subject svc-payments-api was loaded after a Secrets Manager throttle (20:55:38Z) and then "
            "used by two off-baseline external IPs to read 10,227 customer records (bulk export + "
            "payment-methods) until the issuer verified the token dead at 21:12:02Z. The exposure window "
            "opened at the 20:47:11Z deploy, not at first abuse; rotation started 21:11:38Z but the window "
            "only closes on the 21:12:02Z issuer deny. Records were returned to unauthorized sources, but "
            "actor identity and any downstream reuse are unproven from logs alone."
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
                    "subject": "svc-payments-api",
                    "credentialType": "static application service bearer token (fallback)",
                    "credentialLabel": "svc-payments-fallback-redacted",
                    "notAnIamOrCloudKey": True,
                    "reachableScope": [
                        "/v1/customers/summary",
                        "/v1/customers/export (bulk)",
                        "/v1/customers/{id}/payment-methods (sensitive)",
                    ],
                    "deniedScope": ["/v1/billing/events/export (403 — outside this subject's grant)"],
                },
                "exposureWindow": {
                    "openedAt": "2026-06-12T20:47:11Z",
                    "openedBy": "deploy: UpdateFunctionConfiguration set ALLOW_FALLBACK_TOKEN=true (release-9814)",
                    "fallbackFirstLoadedAt": "2026-06-12T20:55:38Z",
                    "firstUnauthorizedUseAt": "2026-06-12T21:04:59Z",
                    "rotationStartedAt": "2026-06-12T21:11:38Z",
                    "issuerVerifiedInactiveAt": "2026-06-12T21:12:02Z",
                    "status": "verified_closed",
                    "note": "A later code deletion would NOT close the window; only the issuer-side deny does.",
                },
                "recordsExportedEstimate": 10227,
                "exportBreakdown": [
                    {"requestId": "req-1042-0002", "ip": "203.0.113.77", "endpoint": "/v1/customers/export?segment=all&limit=5000", "records": 5000},
                    {"requestId": "req-1042-0003", "ip": "203.0.113.77", "endpoint": "/v1/customers/export?segment=all&cursor=5000", "records": 5000},
                    {"requestId": "req-1042-0004", "ip": "203.0.113.77", "endpoint": "/v1/customers/42/payment-methods", "records": 4},
                    {"requestId": "req-1042-0005", "ip": "203.0.113.77", "endpoint": "/v1/customers/2871/payment-methods", "records": 4},
                    {"requestId": "req-1042-0008", "ip": "198.51.100.188", "endpoint": "/v1/customers/export?segment=vip", "records": 219},
                ],
                "exposedVsUsed": {
                    "exposed": "Fallback token shipped in .env.release and live behind ALLOW_FALLBACK_TOKEN.",
                    "actuallyUsed": "Confirmed used: new_ip_for_token + impossible_travel + user_agent_changed, then bulk_access_pattern and a VIP canary_probe->export sequence.",
                    "offBaseline": "curl/8.1.2 and python-requests/2.31 from eu-west-3/us-west-2 vs the baseline payments-worker/7.12.0 from us-east-1.",
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
                    "Downstream reuse, resale, or caching of the 10,227 records is unverified.",
                    "Exact customer-row identities behind the export counts still need data mapping.",
                ],
            },
        },
    )
