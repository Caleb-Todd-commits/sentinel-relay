"""Verify the collaboration API worker loop without a live app or Band keys."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_DIR))

from common.collaboration_api_worker import (  # noqa: E402
    CollaborationApiWorker,
    MemoryWorkerStateStore,
)
from common.fixtures import load_incident  # noqa: E402
from common.schema import build_message, validate_agent_message  # noqa: E402
from common.turn_adapter import AgentTurnRequest, next_sequence, run_turn  # noqa: E402


class FakeCollaborationApiClient:
    def __init__(self, snapshot: dict[str, Any]) -> None:
        self.snapshot = snapshot
        self.posts: list[dict[str, Any]] = []

    def get_room_snapshot(self, room_id: str) -> dict[str, Any]:
        assert self.snapshot["room"]["id"] == room_id
        return self.snapshot

    def post_message(self, post_body: Mapping[str, Any]) -> dict[str, Any]:
        assert post_body["action"] == "sendMessage"
        message = dict(post_body["message"])
        _append(self.snapshot, message)
        self.posts.append(dict(post_body))
        return {"ok": True, "snapshot": self.snapshot}


def _room_snapshot() -> dict[str, Any]:
    packet = load_incident()
    return {
        "room": {
            "id": "band-room-worker-test",
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


def _append(snapshot: dict[str, Any], message: dict[str, Any]) -> dict[str, Any]:
    errors = validate_agent_message(message)
    if errors:
        raise AssertionError(f"{message.get('id')} failed schema validation: {errors}")
    snapshot["messages"].append(message)
    return message


def _direct_turn(
    snapshot: dict[str, Any],
    agent_id: str,
    task: dict[str, Any],
) -> dict[str, Any]:
    message = run_turn(
        AgentTurnRequest(
            target_agent_id=agent_id,
            room_snapshot=snapshot,
            task=task,
        )
    ).message
    return _append(snapshot, message)


def _worker(agent_id: str, client: FakeCollaborationApiClient) -> CollaborationApiWorker:
    return CollaborationApiWorker(
        agent_id=agent_id,
        client=client,  # type: ignore[arg-type]
        state_store=MemoryWorkerStateStore(),
    )


def _human_approval(sequence: int, room_id: str) -> dict[str, Any]:
    return build_message(
        sequence=sequence,
        agent_id="agent-human-approver",
        agent_name="Human Security Lead",
        case_id="INC-1042",
        room_id=room_id,
        message_type="approval_decision",
        title="Containment approved, customer notification held",
        summary=(
            "Approved immediate containment: rotate the fallback token, disable the "
            "fallback path, and patch config. External customer notification remains "
            "held until record-access scope is verified with Legal."
        ),
        confidence=1.0,
        severity="high",
        evidence_ids=["ev-incident-policy"],
        target_agent_ids=["agent-commander", "agent-risk-compliance"],
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


def main() -> int:
    snapshot = _room_snapshot()
    room_id = snapshot["room"]["id"]
    client = FakeCollaborationApiClient(snapshot)

    commander = _worker("agent-commander", client)
    forensics = _worker("agent-forensics", client)
    code_review = _worker("agent-code-review", client)
    threat_intel = _worker("agent-threat-intel", client)
    risk = _worker("agent-risk-compliance", client)
    remediation = _worker("agent-remediation", client)

    _direct_turn(snapshot, "agent-commander", {"kind": "open_case"})
    _direct_turn(
        snapshot,
        "agent-commander",
        {
            "kind": "assign",
            "assignee": "agent-forensics",
            "assigneeName": "Forensics",
            "objective": "Quantify exposure from gateway, auth, and CloudTrail logs.",
        },
    )
    assert forensics.run_once(room_id).message["type"] == "finding"
    assert commander.run_once(room_id) is None, "Commander should wait for all specialist findings."

    _direct_turn(
        snapshot,
        "agent-commander",
        {
            "kind": "assign",
            "assignee": "agent-code-review",
            "assigneeName": "Code Review",
            "objective": "Identify the deploy change that introduced the exposure path.",
        },
    )
    assert code_review.run_once(room_id).message["type"] == "finding"

    _direct_turn(
        snapshot,
        "agent-commander",
        {
            "kind": "assign",
            "assignee": "agent-threat-intel",
            "assigneeName": "Threat Intel",
            "objective": "Assess the external source IPs without overstating attribution.",
        },
    )
    assert threat_intel.run_once(room_id).message["type"] == "finding"

    cross_review = commander.run_once(room_id).message
    assert cross_review["type"] == "handoff"
    assert cross_review["targetAgentIds"] == [
        "agent-forensics",
        "agent-code-review",
        "agent-threat-intel",
    ]
    assert commander.run_once(room_id) is None, "Commander should wait for peer-review verifications."

    forensics_review = forensics.run_once(room_id).message
    assert forensics_review["type"] == "verification"
    assert commander.run_once(room_id) is None, "Commander should wait for all peer reviews."

    code_review_message = code_review.run_once(room_id).message
    assert code_review_message["type"] == "verification"
    assert commander.run_once(room_id) is None, "Commander should wait for the final peer review."

    threat_review = threat_intel.run_once(room_id).message
    assert threat_review["type"] == "verification"

    risk_assignment = commander.run_once(room_id).message
    assert risk_assignment["type"] == "task_assignment"
    assert risk_assignment["targetAgentIds"] == ["agent-risk-compliance"]

    risk_challenge = risk.run_once(room_id).message
    assert risk_challenge["type"] == "challenge"

    approval_request = commander.run_once(room_id).message
    assert approval_request["type"] == "approval_request"

    _append(snapshot, _human_approval(next_sequence(snapshot), room_id))

    remediation_assignment = commander.run_once(room_id).message
    assert remediation_assignment["type"] == "task_assignment"
    assert remediation_assignment["targetAgentIds"] == ["agent-remediation"]
    assert remediation_assignment["payload"]["data"]["approvedScope"] == [
        "Rotate fallback token",
        "Disable fallback token path",
        "Patch config",
    ]

    remediation_task = remediation.run_once(room_id).message
    assert remediation_task["type"] == "remediation_task"

    report = commander.run_once(room_id).message
    assert report["type"] == "report_section"
    assert commander.run_once(room_id) is None, "Commander should not duplicate the final report."

    worker_post_types = [post["message"]["type"] for post in client.posts]
    assert worker_post_types == [
        "finding",
        "finding",
        "finding",
        "handoff",
        "verification",
        "verification",
        "verification",
        "task_assignment",
        "challenge",
        "approval_request",
        "task_assignment",
        "remediation_task",
        "report_section",
    ]
    assert [message["sequence"] for message in snapshot["messages"]] == list(range(1, 19))

    print(
        "OK: collaboration API workers consumed routed messages, advanced Band Leader orchestration, "
        "posted validated responses, and avoided duplicate turns."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
