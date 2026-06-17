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
        title="INC-1042 opened: treat as active credential compromise (svc-payments-api fallback token)",
        summary=(
            "Opened the Band room for INC-1042 and framing it as an active credential compromise until proven "
            "otherwise: a suspicious Customer Records API spike after the Friday deploy, consistent with an "
            "exposed service token. Registered forensics, threat intel, code review, risk/compliance, and "
            "remediation. Working hypothesis to confirm/refute: the introduced fallback token path leaked a "
            "credential for subject svc-payments-api and it is being used from external sources."
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
                    "detectionSource": "Customer Records API usage spike after the Friday deploy",
                    "secretType": "application service bearer token (fallback for subject svc-payments-api) — NOT an AWS/GCP/Entra cloud key",
                    "affectedIdentity": "svc-payments-api (reaches customer summary, bulk export, payment-methods)",
                    "repoBranch": "to confirm with repo owner (not in evidence packet)",
                    "introducingCommitSha": "to confirm — diff blobs 61bf8b2->e248d7a; new file .env.release",
                    "deployImageId": "release-9814 (ci-release-role) / Lambda customer-records-api",
                    "owner": "Human Security Lead",
                    "earliestExposureTime": "2026-06-12T20:47:11Z (deploy enabled ALLOW_FALLBACK_TOKEN)",
                    "stillLive": "to be answered by forensics at the issuer (do not assume rotation == dead)",
                    "logsToPreserve": [
                        "ev-api-gateway-logs", "ev-auth-events", "ev-cloudtrail-events",
                        "ev-secret-scan", "ev-code-diff", "Lambda config history",
                    ],
                },
                "containmentDoctrine": "Issuer-first: revoke/rotate at the provider before code/history cleanup, which can recontaminate from old clones.",
            },
        },
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
        summary=f"Assigning {assignee_name} to: {objective} Cite evidence IDs, name the affected identity and its reach, and assign a confidence.",
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
                "acceptanceCriteria": [
                    "Cite evidence IDs",
                    "Name the affected identity and its permissions/reach",
                    "Assign confidence",
                    "State limitations",
                ],
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
        title="Human approval requested for issuer-first containment",
        summary=(
            "Requesting Security Lead approval for issuer-first containment in order: (1) confirm the exposed "
            "fallback token is revoked/dead at its issuer, (2) two-key rotate the sibling Secrets Manager "
            "primary, (3) disable the ALLOW_FALLBACK_TOKEN path and remove .env.release. External customer "
            "notification and incident closure are explicitly NOT requested — those are irreversible/disclosure "
            "decisions held for the human and Legal pending verified scope."
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
                "approvalRequestId": "appr-1042-1",
                "requiredApprover": "Security Lead",
                "containmentSequence": [
                    "Verify exposed fallback token revoked at issuer",
                    "Two-key rotate sibling Secrets Manager primary (svc-payments-prod-v2)",
                    "Disable ALLOW_FALLBACK_TOKEN path and remove .env.release",
                ],
                "requestedActions": ["Rotate fallback token", "Disable fallback token path", "Patch config"],
                "notRequestedActions": ["External customer notification", "Incident closure"],
                "routedToHumanBecauseIrreversible": ["External customer notification", "Incident closure"],
                "riskIfApproved": "May briefly disrupt the service depending on the credential, but stops ongoing exposure.",
                "riskIfRejected": "Exposed fallback token and its sibling may remain usable while investigation continues.",
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
        title="Audit-ready report for INC-1042 (with surfaced agent disagreement)",
        summary=(
            "Compiled the exposure-window timeline, evidence references, the risk challenge, the human approval "
            "decision, and remediation status into the final audit report. Deliberately preserves the tension "
            "between agents rather than smoothing it: Forensics quantifies unauthorized access to 10,227 records, "
            "Risk holds the policy classification at suspected_exposure while flagging the GDPR clock as likely "
            "triggered, and Code Review/Remediation stress that a sibling credential must be rotated before "
            "containment is complete. Open questions on record mapping and downstream reuse remain for follow-up."
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
                    "Agents coordinated through Band to investigate an exposed fallback service token for "
                    "svc-payments-api introduced by the Friday deploy. Forensics confirmed 10,227 customer records "
                    "were read by two external IPs across a window that opened at the 20:47:11Z deploy and is "
                    "issuer-verified closed at 21:12:02Z. Risk & Compliance challenged the breach framing down to "
                    "suspected_exposure under policy while flagging the GDPR personal-data-breach threshold as "
                    "likely met. Human approval authorised issuer-first containment; notification was held for Legal."
                ),
                "rootCause": "Friday deploy added an ALLOW_FALLBACK_TOKEN fail-open path plus a token-bearing .env.release (also enabling CUSTOMER_EXPORT_ENABLED); a Secrets Manager throttle triggered fallback use.",
                "exposureWindow": {"openedAt": "2026-06-12T20:47:11Z", "issuerVerifiedClosedAt": "2026-06-12T21:12:02Z", "closedBy": "issuer deny, not code deletion"},
                "riskAssessment": "High severity, suspected_exposure under policy; unauthorised access to personal data is confirmed, downstream exfiltration/misuse is not.",
                "surfacedDisagreements": [
                    "Forensics shows records WERE returned to unauthorized IPs (reads toward breach); Risk keeps policy classification at suspected_exposure because actor identity is unresolved — both are recorded, not merged.",
                    "Threat Intel rates likelihood-of-exploitation HIGH (active abuse + post-rotation retry); Risk still blocks any 'confirmed exfiltration' claim absent downstream evidence.",
                    "Remediation marks the fallback token dead, but Code Review/Remediation insist containment is incomplete until the sibling Secrets Manager primary is independently rotated.",
                ],
                "approvedActions": ["Rotate fallback token", "Disable fallback path", "Patch config"],
                "heldActions": ["External customer notification", "Incident closure"],
                "openQuestions": [
                    "Which exact customer records (and residencies) map to the exported rows?",
                    "Did any downstream system cache or forward the exported records?",
                    "Is the sibling Secrets Manager primary fully rotated and the fallback purged from CI/images?",
                    "Does Legal require customer notification once scope is verified?",
                ],
                "auditTrailMessageIds": audit_trail,
            },
        },
    )
