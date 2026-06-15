"""Risk & Compliance agent business logic (agents lane).

Applies the incident policy, challenges any "confirmed breach" overclaim, and
determines what requires human approval. Deterministic in mock mode; in live
mode this is the natural place to route the AI/ML API policy-gate call.
"""

from __future__ import annotations

from typing import Any

from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-risk-compliance"
AGENT_NAME = "Risk & Compliance Agent"

_EVIDENCE = ["ev-incident-policy", "ev-api-gateway-logs", "ev-code-diff"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    policy_id = ctx.task.get("policyId") or "SEC-IR-API-KEY-001"
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="challenge",
        title="Classify as suspected exposure — challenge any confirmed-breach claim",
        summary=(
            "Evidence supports likely token exposure and unauthorized customer-record "
            "export, but actor identity and downstream reuse are unproven. Per policy "
            "this is suspected exposure, not a confirmed breach; containment needs "
            "Security Lead approval and external notification is deferred to Legal."
        ),
        confidence=0.88,
        severity="high",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact="Prevents overstating breach scope and forces a human approval gate before high-impact actions.",
        next_action="Commander should request human approval for containment and hold external notification.",
        payload={
            "kind": "risk_assessment",
            "data": {
                "recommendedSeverity": "high",
                "classification": "suspected_exposure",
                "challenges": [
                    "Do not claim confirmed breach until an unauthorized actor and record mapping are established.",
                    "External customer notification must not proceed without Legal sign-off.",
                ],
                "policyRefs": [policy_id],
                "humanApprovalRequired": [
                    "rotate_or_revoke_production_credentials",
                    "disable_customer_export_endpoint",
                    "external_customer_notification",
                ],
                "deferredPendingHuman": ["external_customer_notification", "incident_closure"],
            },
        },
    )
