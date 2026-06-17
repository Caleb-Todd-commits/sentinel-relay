"""Run a full Sentinel Relay agent flow offline (agents lane).

Drives the 18-step Commander-led @mention chain against a synthetic incident
with zero network and zero model calls. Every agent turn goes through the same
``handle_turn`` seam the real Band transport will use, and every message is
schema-validated before it is routed.

Usage:
    python agents/mock/run_mock_flow.py                         # inc-1042 transcript
    python agents/mock/run_mock_flow.py --incident-id INC-1043  # inc-1043 transcript
    python agents/mock/run_mock_flow.py --json                  # AgentMessage JSON array
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_DIR))

from typing import Any  # noqa: E402

from code_review.agent import handle_turn as code_review_turn  # noqa: E402
from commander.agent import handle_turn as commander_turn  # noqa: E402
from common.fixtures import IncidentPacket, load_incident  # noqa: E402
from common.schema import AgentTurnContext, build_message  # noqa: E402
from forensics.agent import handle_turn as forensics_turn  # noqa: E402
from mock.mock_transport import MockBandRoom  # noqa: E402
from remediation.agent import handle_turn as remediation_turn  # noqa: E402
from risk_compliance.agent import handle_turn as risk_turn  # noqa: E402
from threat_intel.agent import handle_turn as threat_intel_turn  # noqa: E402

EXPECTED_STEPS = 18

HANDLES = {
    "agent-commander": "band-leader",
    "agent-forensics": "forensics",
    "agent-threat-intel": "threat-intel",
    "agent-code-review": "code-review",
    "agent-risk-compliance": "risk-compliance",
    "agent-remediation": "remediation",
    "agent-human-approver": "security-lead",
}


def _human_approval_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    """The human approval gate (not one of the six AI agents)."""
    approved_scope = _approved_scope(ctx)
    approval_request_id = ctx.task.get("approvalRequestId") or _approval_request_id(ctx.case["id"])
    summary = (
        "Approved immediate containment: revoke federated sessions, tighten the OIDC trust policy, "
        "and patch export scope. External customer notification remains held until record-access "
        "scope is verified with Legal."
        if _is_oidc_policy(ctx)
        else (
            "Approved immediate containment: rotate the fallback token, disable the "
            "fallback path, and patch config. External customer notification remains "
            "held until record-access scope is verified with Legal."
        )
    )
    return build_message(
        sequence=ctx.sequence,
        agent_id="agent-human-approver",
        agent_name="Human Security Lead",
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="approval_decision",
        title="Containment approved, customer notification held",
        summary=summary,
        confidence=1.0,
        severity="high",
        evidence_ids=["ev-incident-policy"],
        target_agent_ids=["agent-commander", "agent-risk-compliance"],
        decision_impact="Unlocks remediation while keeping disclosure decisions under human control.",
        next_action="Remediation should execute the approved scope only.",
        payload={
            "kind": "approval_decision",
            "data": {
                "approvalRequestId": approval_request_id,
                "decision": "approved",
                "decidedBy": "Human Security Lead",
                "approvedScope": approved_scope,
                "explicitlyNotApproved": ["External customer notification", "Incident closure"],
            },
        },
    )


def _context(packet: IncidentPacket, room: MockBandRoom, actor_id: str, task: dict[str, Any], sequence: int) -> AgentTurnContext:
    return AgentTurnContext(
        case=packet.case,
        room_id=room.room_id,
        agent_profile=packet.agents[actor_id],
        recent_messages=list(room.transcript),
        evidence=packet.evidence,
        current_state=packet.state,
        task=task,
        sequence=sequence,
    )


def run_flow(
    *,
    incident_id: str | None = None,
    incident_dir: Path | str | None = None,
) -> MockBandRoom:
    packet = load_incident(incident_dir=incident_dir, incident_id=incident_id)
    room = MockBandRoom(room_id=packet.case["roomId"])
    for agent_id, handle in HANDLES.items():
        room.register(agent_id, handle)

    policy_id = str(packet.policy.get("policyId") or "SEC-IR-API-KEY-001")
    approved_scope = _approved_scope_for_policy(policy_id)
    approval_request_id = _approval_request_id(packet.case["id"])

    # (actor_id, handle_turn, task) for each of the 18 ordered turns.
    steps = [
        ("agent-commander", commander_turn, {"kind": "open_case"}),
        ("agent-commander", commander_turn, {"kind": "assign", "assignee": "agent-forensics", "assigneeName": "Forensics", "objective": "Quantify exposure from gateway, auth, and CloudTrail logs."}),
        ("agent-commander", commander_turn, {"kind": "assign", "assignee": "agent-code-review", "assigneeName": "Code Review", "objective": "Identify the deploy change that introduced the exposure path."}),
        ("agent-commander", commander_turn, {"kind": "assign", "assignee": "agent-threat-intel", "assigneeName": "Threat Intel", "objective": "Assess the external source IPs without overstating attribution."}),
        ("agent-forensics", forensics_turn, {"kind": "report"}),
        ("agent-code-review", code_review_turn, {"kind": "report"}),
        ("agent-threat-intel", threat_intel_turn, {"kind": "report"}),
        ("agent-commander", commander_turn, {"kind": "request_cross_review"}),
        ("agent-forensics", forensics_turn, {"kind": "cross_review", "reviewRoundId": f"review-{packet.case['id'].lower()}-1"}),
        ("agent-code-review", code_review_turn, {"kind": "cross_review", "reviewRoundId": f"review-{packet.case['id'].lower()}-1"}),
        ("agent-threat-intel", threat_intel_turn, {"kind": "cross_review", "reviewRoundId": f"review-{packet.case['id'].lower()}-1"}),
        ("agent-commander", commander_turn, {"kind": "assign", "assignee": "agent-risk-compliance", "assigneeName": "Risk & Compliance", "objective": "Rule on severity and required approvals per the incident policy.", "policyId": policy_id}),
        ("agent-risk-compliance", risk_turn, {"kind": "assess", "policyId": policy_id}),
        ("agent-commander", commander_turn, {"kind": "request_approval"}),
        ("agent-human-approver", _human_approval_turn, {"kind": "decide", "policyId": policy_id, "approvalRequestId": approval_request_id, "approvedScope": approved_scope}),
        ("agent-commander", commander_turn, {"kind": "assign", "assignee": "agent-remediation", "assigneeName": "Remediation", "objective": "Execute the approved containment scope only.", "approvedScope": approved_scope}),
        ("agent-remediation", remediation_turn, {"kind": "remediate", "approvedScope": approved_scope}),
        ("agent-commander", commander_turn, {"kind": "generate_report"}),
    ]

    for sequence, (actor_id, handle_turn, task) in enumerate(steps, start=1):
        ctx = _context(packet, room, actor_id, task, sequence)
        room.post(handle_turn, ctx)

    return room


def _print_transcript(room: MockBandRoom) -> None:
    case_id = room.transcript[0]["caseId"] if room.transcript else "unknown"
    print(f"\nSentinel Relay — {case_id} mock flow (offline, zero network/model)\n{'=' * 70}")
    for record, message in zip(room.routing_log, room.transcript):
        mentions = room.mention_string(record.target_agent_ids)
        sender = room.handles.get(message["agentId"], message["agentId"])
        print(
            f"[{record.sequence:>2}] @{sender:<14} {message['type']:<16} -> {mentions}\n"
            f"      {message['title']}"
        )
    print("=" * 70)


def _approved_scope(ctx: AgentTurnContext) -> list[str]:
    scope = ctx.task.get("approvedScope")
    if isinstance(scope, list):
        return [str(item) for item in scope if str(item).strip()]
    return _approved_scope_for_policy(str(ctx.task.get("policyId") or ""))


def _approved_scope_for_policy(policy_id: str) -> list[str]:
    if policy_id == "SEC-IR-OIDC-002":
        return ["Revoke federated sessions", "Tighten OIDC trust policy", "Patch export scope"]
    return ["Rotate fallback token", "Disable fallback token path", "Patch config"]


def _is_oidc_policy(ctx: AgentTurnContext) -> bool:
    return str(ctx.task.get("policyId")) == "SEC-IR-OIDC-002"


def _approval_request_id(case_id: str) -> str:
    return f"appr-{case_id.lower().replace('inc-', '')}-1"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Sentinel Relay mock agent flow.")
    parser.add_argument("--incident-id", help="Synthetic incident id, e.g. INC-1042 or INC-1043.")
    parser.add_argument("--incident-dir", help="Path to a synthetic incident fixture directory.")
    parser.add_argument("--json", action="store_true", help="Print full AgentMessage JSON transcript.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    room = run_flow(incident_id=args.incident_id, incident_dir=args.incident_dir)

    if args.json:
        print(json.dumps(room.transcript, indent=2))
        return 0

    _print_transcript(room)

    # End-to-end self-checks (all messages were already schema-validated on post).
    assert len(room.transcript) == EXPECTED_STEPS, f"expected {EXPECTED_STEPS} messages, got {len(room.transcript)}"
    forensics_record = room.routing_log[4]  # seq 5: Forensics -> Commander only
    assert forensics_record.delivered_to == ["agent-commander"], "mention routing leaked beyond Commander"
    assert room.transcript[7]["type"] == "handoff", "cross-agent review handoff missing at step 8"
    assert [message["type"] for message in room.transcript[8:11]] == [
        "verification",
        "verification",
        "verification",
    ], "peer verification round missing before risk gate"
    assert room.transcript[14]["type"] == "approval_decision", "human approval gate missing at step 15"
    assert room.transcript[-1]["type"] == "report_section", "final audit report missing"
    print(
        f"\nOK: {EXPECTED_STEPS}/{EXPECTED_STEPS} messages schema-valid, "
        "@mention routing verified, human approval gate present, final report generated."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
