"""Verify the Band room snapshot -> agent turn adapter offline.

This is the Person 2 contract test: a live worker can receive a Band-style room
snapshot plus one routed message, derive the right local agent task, produce a
schema-valid AgentMessage, and build the body the web API route expects.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_DIR))

from common.fixtures import load_incident  # noqa: E402
from common.schema import build_message, validate_agent_message  # noqa: E402
from common.turn_adapter import (  # noqa: E402
    AgentTurnRequest,
    build_collaboration_post_body,
    next_sequence,
    run_turn,
    task_from_inbound_message,
)


def _room_snapshot(incident_id: str | None = None) -> dict[str, Any]:
    packet = load_incident(incident_id=incident_id)
    return {
        "room": {
            "id": "band-room-adapter-test",
            "caseId": packet.case["id"],
            "title": packet.case["title"],
            "createdAt": packet.case["openedAt"],
            "updatedAt": packet.case["updatedAt"],
            "mode": "band",
            "participantAgentIds": list(packet.agents),
        },
        "messages": [],
        "registeredAgents": list(packet.agents.values()),
        "approvalRequests": [],
        "approvalDecisions": [],
        "taskStatuses": [],
        "auditEvents": [],
    }


def _assert_valid(message: dict[str, Any]) -> None:
    errors = validate_agent_message(message)
    if errors:
        raise AssertionError(f"{message.get('id')} failed schema validation: {errors}")


def _append(snapshot: dict[str, Any], message: dict[str, Any]) -> dict[str, Any]:
    _assert_valid(message)
    snapshot["messages"].append(message)
    return message


def _human_approval(sequence: int, room_id: str) -> dict[str, Any]:
    return build_message(
        sequence=sequence,
        agent_id="agent-human-approver",
        agent_name="Human Security Lead",
        case_id="INC-1042",
        room_id=room_id,
        message_type="approval_decision",
        title="Containment approved for issuer-first response",
        summary=(
            "Approved the immediate containment scope: rotate the fallback token, "
            "disable the fallback token path, and patch config. Customer notification "
            "and incident closure remain held for Legal."
        ),
        confidence=1.0,
        severity="high",
        evidence_ids=["ev-incident-policy"],
        target_agent_ids=["agent-commander"],
        payload={
            "kind": "approval_decision",
            "data": {
                "approvalRequestId": "appr-1042-1",
                "decision": "approved",
                "approvedScope": [
                    "Rotate fallback token",
                    "Disable fallback token path",
                    "Patch config",
                ],
                "explicitlyNotApproved": [
                    "External customer notification",
                    "Incident closure",
                ],
            },
        },
    )


def _specialist_finding(sequence: int, room_id: str, agent_id: str, title: str) -> dict[str, Any]:
    return build_message(
        sequence=sequence,
        agent_id=agent_id,
        agent_name=agent_id.replace("agent-", "").replace("-", " ").title(),
        case_id="INC-1042",
        room_id=room_id,
        message_type="finding",
        title=title,
        summary=f"{title} with enough evidence-grounded detail for the adapter contract test.",
        confidence=0.82,
        severity="high",
        evidence_ids=["ev-api-gateway-logs"],
        target_agent_ids=["agent-commander"],
        payload={"kind": "finding", "data": {"claim": title}},
    )


def _assert_cross_review_inference() -> None:
    snapshot = _room_snapshot()
    room_id = snapshot["room"]["id"]
    findings = [
        _append(snapshot, _specialist_finding(1, room_id, "agent-forensics", "Forensics finding")),
        _append(snapshot, _specialist_finding(2, room_id, "agent-code-review", "Code Review finding")),
        _append(snapshot, _specialist_finding(3, room_id, "agent-threat-intel", "Threat Intel finding")),
    ]

    cross_review = _append(
        snapshot,
        run_turn(
            AgentTurnRequest(
                target_agent_id="agent-commander",
                room_snapshot=snapshot,
                inbound_message=findings[-1],
            )
        ).message,
    )
    assert cross_review["type"] == "handoff"
    assert cross_review["targetAgentIds"] == [
        "agent-forensics",
        "agent-code-review",
        "agent-threat-intel",
    ]

    derived_task = task_from_inbound_message(
        cross_review,
        "agent-forensics",
        recent_messages=snapshot["messages"],
    )
    assert derived_task["kind"] == "cross_review"
    assert derived_task["reviewRoundId"] == "review-inc-1042-1"

    for agent_id in ["agent-forensics", "agent-code-review", "agent-threat-intel"]:
        review = run_turn(
            AgentTurnRequest(
                target_agent_id=agent_id,
                room_snapshot=snapshot,
                inbound_message=cross_review,
            )
        ).message
        assert review["type"] == "verification"
        _append(snapshot, review)

    risk_assignment = run_turn(
        AgentTurnRequest(
            target_agent_id="agent-commander",
            room_snapshot=snapshot,
            inbound_message=snapshot["messages"][-1],
        )
    ).message
    assert risk_assignment["type"] == "task_assignment"
    assert risk_assignment["targetAgentIds"] == ["agent-risk-compliance"]


def _assert_inc_1043_snapshot_inference() -> None:
    snapshot = _room_snapshot("INC-1043")
    room_id = snapshot["room"]["id"]

    opened = run_turn(
        AgentTurnRequest(
            target_agent_id="agent-commander",
            room_snapshot=snapshot,
            task={"kind": "open_case"},
        )
    ).message
    assert opened["caseId"] == "INC-1043"
    assert opened["roomId"] == room_id
    assert "OIDC" in opened["summary"]

    assignment = run_turn(
        AgentTurnRequest(
            target_agent_id="agent-commander",
            room_snapshot=snapshot,
            task={
                "kind": "assign",
                "assignee": "agent-forensics",
                "assigneeName": "Forensics",
                "objective": "Quantify exposure from gateway, auth, and CloudTrail logs.",
            },
            sequence=2,
        )
    ).message
    _append(snapshot, opened)
    _append(snapshot, assignment)

    forensics = run_turn(
        AgentTurnRequest(
            target_agent_id="agent-forensics",
            room_snapshot=snapshot,
            inbound_message=assignment,
        )
    ).message
    assert forensics["caseId"] == "INC-1043"
    assert forensics["roomId"] == room_id
    assert "federated token" in forensics["title"].lower()
    assert "3,636" in forensics["summary"]


def main() -> int:
    snapshot = _room_snapshot()
    room_id = snapshot["room"]["id"]

    opened = _append(
        snapshot,
        run_turn(
            AgentTurnRequest(
                target_agent_id="agent-commander",
                room_snapshot=snapshot,
                task={"kind": "open_case"},
            )
        ).message,
    )
    assert opened["sequence"] == 1
    assert opened["roomId"] == room_id

    assignment = _append(
        snapshot,
        run_turn(
            AgentTurnRequest(
                target_agent_id="agent-commander",
                room_snapshot=snapshot,
                task={
                    "kind": "assign",
                    "assignee": "agent-forensics",
                    "assigneeName": "Forensics",
                    "objective": "Quantify exposure from gateway, auth, and CloudTrail logs.",
                },
            )
        ).message,
    )
    assert assignment["sequence"] == 2
    assert assignment["targetAgentIds"] == ["agent-forensics"]

    wrapped_assignment = {"event": {"metadata": {"payload": assignment}}}
    derived_task = task_from_inbound_message(
        wrapped_assignment,
        "agent-forensics",
        recent_messages=snapshot["messages"],
    )
    assert derived_task["kind"] == "report"
    assert derived_task["sourceMessageId"] == assignment["id"]

    forensics_result = run_turn(
        AgentTurnRequest(
            target_agent_id="agent-forensics",
            room_snapshot=snapshot,
            inbound_message=wrapped_assignment,
        )
    )
    forensics = _append(snapshot, forensics_result.message)
    assert forensics["sequence"] == 3
    assert forensics["roomId"] == room_id
    assert forensics["targetAgentIds"] == ["agent-commander"]
    assert forensics_result.post_body == build_collaboration_post_body(room_id, forensics)
    assert forensics_result.post_body["action"] == "sendMessage"

    approval = _append(snapshot, _human_approval(next_sequence(snapshot), room_id))
    commander_after_approval = _append(
        snapshot,
        run_turn(
            AgentTurnRequest(
                target_agent_id="agent-commander",
                room_snapshot=snapshot,
                inbound_message=approval,
            )
        ).message,
    )
    assert commander_after_approval["type"] == "task_assignment"
    assert commander_after_approval["targetAgentIds"] == ["agent-remediation"]
    assert commander_after_approval["payload"]["data"]["approvedScope"] == [
        "Rotate fallback token",
        "Disable fallback token path",
        "Patch config",
    ]

    remediation_result = run_turn(
        AgentTurnRequest(
            target_agent_id="agent-remediation",
            room_snapshot=snapshot,
            inbound_message=commander_after_approval,
        )
    )
    remediation = _append(snapshot, remediation_result.message)
    assert remediation["sequence"] == 6
    assert remediation["payload"]["data"]["approvedScope"] == [
        "Rotate fallback token",
        "Disable fallback token path",
        "Patch config",
    ]

    assert [message["sequence"] for message in snapshot["messages"]] == [1, 2, 3, 4, 5, 6]
    _assert_cross_review_inference()
    _assert_inc_1043_snapshot_inference()
    print(
        "OK: Band turn adapter derived routed specialist tasks, preserved live room IDs, "
        "validated AgentMessage output, and built /api/collaboration/messages payloads."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
