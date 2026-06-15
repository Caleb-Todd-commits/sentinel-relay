"""Forensics agent business logic (agents lane).

Reads the gateway / auth / CloudTrail evidence and reports the measured exposure.
Deterministic in mock mode; an LLM enrichment layer can wrap ``handle_turn`` for
live mode without changing the transport seam.
"""

from __future__ import annotations

from typing import Any

from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-forensics"
AGENT_NAME = "Forensics Agent"

_EVIDENCE = ["ev-api-gateway-logs", "ev-auth-events", "ev-cloudtrail-events"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    findings = [
        {
            "claim": "Customer export endpoints returned ~10,227 records via the fallback token before rotation.",
            "evidenceRef": "ev-api-gateway-logs",
            "source": "api_gateway_logs.jsonl",
            "observation": "Request spike 21:04:59Z–21:11:38Z from two external IPs; post-rotation requests return 401.",
        },
        {
            "claim": "The fallback service token was loaded after a secrets-manager throttle and then used by unexpected sources.",
            "evidenceRef": "ev-auth-events",
            "source": "auth_events.jsonl",
            "observation": "Fallback loaded 20:55:38Z; rotation started 21:11:38Z, token revoked 21:12:02Z.",
        },
        {
            "claim": "Deployment updated the Lambda config to enable the fallback path just before the throttle.",
            "evidenceRef": "ev-cloudtrail-events",
            "source": "cloudtrail_events.jsonl",
            "observation": "Config update 20:47:11Z; secrets-manager ThrottlingException 20:55:36Z.",
        },
    ]
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="finding",
        title="Fallback token used to export ~10,227 customer records",
        summary=(
            "Gateway and auth logs show the fallback service token, loaded after a "
            "secrets-manager throttle, was used by two external IPs to export roughly "
            "10,227 customer records until rotation cut access at 21:11:38Z."
        ),
        confidence=0.86,
        severity="high",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact="Quantifies record exposure but does not by itself prove actor identity or downstream reuse.",
        next_action="Risk & Compliance should classify severity and required approvals; do not yet claim confirmed breach.",
        payload={
            "kind": "finding",
            "data": {
                "findings": findings,
                "recordsExportedEstimate": 10227,
                "limitations": [
                    "No actor attribution from logs alone.",
                    "Downstream reuse of exported records is unverified.",
                ],
            },
        },
    )
