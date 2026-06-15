"""Remediation agent business logic (agents lane).

Produces an approval-scoped containment and fix plan. Only executes the actions
the human approver authorized; deferred actions are left out. Deterministic in
mock mode.
"""

from __future__ import annotations

from typing import Any

from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-remediation"
AGENT_NAME = "Remediation Agent"

_EVIDENCE = ["ev-code-diff", "ev-auth-events"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    approved_scope = ctx.task.get("approvedScope") or [
        "Rotate fallback token",
        "Disable fallback token path",
    ]
    tasks = [
        {
            "id": "rem-001",
            "title": "Rotate fallback service token",
            "status": "done",
            "severity": "high",
            "rationale": "Token was used by unexpected external IPs; rotation already cut access at 21:11:38Z.",
            "evidenceIds": ["ev-auth-events"],
            "acceptanceCriteria": ["Old token fails auth", "Dependent services healthy on rotated token"],
            "rollbackPlan": "Re-issue scoped credential only after Security Lead approval.",
        },
        {
            "id": "rem-002",
            "title": "Disable ALLOW_FALLBACK_TOKEN path and remove .env.release",
            "status": "in_progress",
            "severity": "high",
            "rationale": "The fallback path is the root-cause exposure mechanism from the Friday deploy.",
            "evidenceIds": ["ev-code-diff"],
            "acceptanceCriteria": ["Fallback path removed", "Secret-pattern unit test added"],
            "rollbackPlan": "Never restore the token-like fallback; revert only the surrounding config if deploy breaks.",
        },
        {
            "id": "rem-003",
            "title": "Add deploy-time secret-scan guardrail in CI",
            "status": "todo",
            "severity": "medium",
            "rationale": "Prevent recurrence by blocking token-like values before deployment.",
            "evidenceIds": ["ev-code-diff"],
            "acceptanceCriteria": ["CI fails on token pattern", "Safe placeholder passes"],
            "rollbackPlan": "Manual security override only with an audit-log entry.",
        },
    ]
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="remediation_task",
        title="Approved containment executed; fix and guardrail queued",
        summary=(
            "Within the approved scope, the fallback token is rotated and the fallback "
            "path is being disabled, with a CI secret-scan guardrail queued. External "
            "customer notification is intentionally excluded because it was not approved."
        ),
        confidence=0.92,
        severity="high",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact="Moves the case from investigation into controlled, approval-bounded remediation.",
        next_action="Commander can generate the final audit report once remediation status is recorded.",
        payload={
            "kind": "remediation_task",
            "data": {
                "approvedScope": approved_scope,
                "excludedPendingApproval": ["External customer notification", "Incident closure"],
                "tasks": tasks,
            },
        },
    )
