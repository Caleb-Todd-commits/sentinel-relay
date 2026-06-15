"""Threat Intel agent business logic (agents lane).

Assesses the source IPs and behavior, deliberately refusing real-world
attribution overreach (the IPs are documentation-range demo indicators).
Deterministic in mock mode.
"""

from __future__ import annotations

from typing import Any

from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-threat-intel"
AGENT_NAME = "Threat Intel Agent"

_EVIDENCE = ["ev-ip-intel", "ev-api-gateway-logs"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    findings = [
        {
            "claim": "Two external IPs (203.0.113.77, 198.51.100.188) used the token; 198.51.100.24 is expected CI egress.",
            "evidenceRef": "ev-ip-intel",
            "source": "suspicious_ips.json",
            "observation": "Unexpected sources used curl and python-requests user agents during the spike window.",
        },
    ]
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="finding",
        title="External IPs used the token; attribution intentionally withheld",
        summary=(
            "Two unexpected external IPs exercised the fallback token during the spike "
            "while one source was benign CI egress. Behavior is suspicious, but these "
            "are documentation-range demo indicators, so no real-world actor attribution is claimed."
        ),
        confidence=0.74,
        severity="medium",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact="Strengthens unauthorized-use evidence while keeping attribution and intent unproven.",
        next_action="Risk & Compliance should treat this as suspected exposure, not confirmed breach.",
        payload={
            "kind": "finding",
            "data": {
                "findings": findings,
                "strongestSignals": ["unexpected source IPs", "automation user agents", "post-deploy timing"],
                "weakSignals": ["IP reputation alone"],
                "limitations": ["Documentation-range IPs; do not claim real-world threat-actor attribution."],
            },
        },
    )
