"""Band Leader (Commander) agent business logic (agents lane).

The Commander drives the @mention chain: it opens the case, assigns specialists,
requests human approval, and synthesizes the final report. Its turn behaviour is
selected by ``ctx.task["kind"]``. Deterministic in mock mode; in live mode the
report/synthesis turn is the natural place to route the AI/ML API call.
"""

from __future__ import annotations

from typing import Any

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


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    kind = ctx.task.get("kind", "open_case")
    handler = {
        "open_case": _open_case,
        "assign": _assign,
        "request_approval": _request_approval,
        "generate_report": _generate_report,
    }.get(kind, _open_case)
    return handler(ctx)


def _open_case(ctx: AgentTurnContext) -> dict[str, Any]:
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="case_opened",
        title="Band incident room opened for INC-1042",
        summary=(
            "Opened the shared Band room for INC-1042 (possible API key exposure after "
            "the Friday deploy) and registered the forensics, threat intel, code review, "
            "risk/compliance, and remediation agents."
        ),
        confidence=1.0,
        severity="high",
        evidence_ids=[],
        target_agent_ids=_SPECIALISTS,
        decision_impact="Creates the shared coordination space for all agent handoffs.",
        next_action="Assign evidence-review tasks to specialist agents.",
        payload={"kind": "case_opened", "data": {"roomCreated": True, "registeredAgentIds": _SPECIALISTS}},
    )


def _assign(ctx: AgentTurnContext) -> dict[str, Any]:
    assignee = ctx.task["assignee"]
    objective = ctx.task.get("objective", "Review assigned evidence and report findings.")
    assignee_name = ctx.task.get("assigneeName", assignee)
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="task_assignment",
        title=f"Task assigned to {assignee_name}",
        summary=f"Assigning {assignee_name} to: {objective} Cite evidence IDs and assign a confidence.",
        confidence=1.0,
        severity="high",
        evidence_ids=[],
        target_agent_ids=[assignee],
        decision_impact="Distributes the investigation so no single agent decides alone.",
        next_action=f"Wait for an evidence-backed report from {assignee_name}.",
        payload={
            "kind": "task_assignment",
            "data": {
                "taskId": ctx.task.get("taskId", f"task-{assignee}"),
                "assignedToAgentId": assignee,
                "objective": objective,
                "acceptanceCriteria": ["Cite evidence IDs", "Assign confidence", "State limitations"],
            },
        },
    )


def _request_approval(ctx: AgentTurnContext) -> dict[str, Any]:
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="approval_request",
        title="Human approval requested for containment",
        summary=(
            "Requesting Security Lead approval to rotate the fallback token, disable the "
            "fallback path, and patch config. External customer notification is explicitly "
            "NOT requested and is held pending Legal review of scope."
        ),
        confidence=0.94,
        severity="high",
        evidence_ids=["ev-incident-policy", "ev-code-diff"],
        target_agent_ids=["agent-human-approver"],
        decision_impact="Ensures production-impacting actions are not taken autonomously.",
        next_action="Wait for the human Security Lead decision.",
        payload={
            "kind": "approval_request",
            "data": {
                "approvalRequestId": "appr-1042-1",
                "requiredApprover": "Security Lead",
                "requestedActions": ["Rotate fallback token", "Disable fallback token path", "Patch config"],
                "notRequestedActions": ["External customer notification"],
                "riskIfApproved": "May briefly disrupt services depending on the token, but stops ongoing exposure.",
                "riskIfRejected": "Exposed fallback token may remain usable while investigation continues.",
            },
        },
    )


def _generate_report(ctx: AgentTurnContext) -> dict[str, Any]:
    audit_trail = [m["id"] for m in ctx.recent_messages]
    evidence_ids = sorted({eid for m in ctx.recent_messages for eid in m.get("evidenceIds", [])})
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="report_section",
        title="Audit-ready report generated for INC-1042",
        summary=(
            "Compiled the timeline, evidence references, the risk challenge, the human "
            "approval decision, and remediation status into the final audit report, with "
            "open questions on record mapping and downstream reuse left for follow-up."
        ),
        confidence=0.96,
        severity="high",
        evidence_ids=evidence_ids,
        target_agent_ids=[],
        decision_impact="Produces the judge-facing proof of traceable, mention-driven multi-agent coordination.",
        next_action="Use replay mode to show how the decision was reached through Band.",
        payload={
            "kind": "report_section",
            "data": {
                "reportId": "report-inc-1042",
                "severity": "high",
                "executiveSummary": (
                    "Agents coordinated through Band to investigate a fallback-token exposure "
                    "after the Friday deploy, confirmed ~10,227 records were exported, challenged "
                    "the breach classification down to suspected exposure, obtained human approval "
                    "for containment, and executed an approval-bounded remediation plan."
                ),
                "rootCause": "Friday deploy added an ALLOW_FALLBACK_TOKEN path plus a token-bearing .env.release; a secrets-manager throttle triggered fallback use.",
                "riskAssessment": "High severity, suspected exposure: record export confirmed, actor identity and downstream reuse unproven.",
                "approvedActions": ["Rotate fallback token", "Disable fallback path", "Patch config"],
                "heldActions": ["External customer notification", "Incident closure"],
                "openQuestions": [
                    "Which exact customer records map to the exported rows?",
                    "Did any downstream system cache or forward the exported records?",
                    "Does Legal require customer notification once scope is verified?",
                ],
                "auditTrailMessageIds": audit_trail,
            },
        },
    )
