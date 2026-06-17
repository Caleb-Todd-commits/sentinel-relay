"""Translate Band room turns into validated Sentinel Relay agent messages.

The web app owns Band room creation and message posting. Live Python workers
only need to answer one routed turn: read the room snapshot/inbound message,
assemble ``AgentTurnContext``, call the target agent's ``handle_turn``, then
post the returned ``AgentMessage`` through ``/api/collaboration/messages``.

This module is intentionally standard-library only so it can be verified offline
and reused by SDK/WebSocket workers without pulling frontend code into agents.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Mapping

from common.fixtures import IncidentPacket, load_incident, resolve_incident_dir
from common.interface import HandleTurn, run_agent_turn
from common.schema import AgentTurnContext

AGENT_MODULES: dict[str, str] = {
    "agent-commander": "commander.agent",
    "agent-forensics": "forensics.agent",
    "agent-threat-intel": "threat_intel.agent",
    "agent-code-review": "code_review.agent",
    "agent-risk-compliance": "risk_compliance.agent",
    "agent-remediation": "remediation.agent",
}

REPORTING_AGENT_IDS = {
    "agent-forensics",
    "agent-threat-intel",
    "agent-code-review",
}
REVIEW_AGENT_IDS = [
    "agent-forensics",
    "agent-code-review",
    "agent-threat-intel",
]
REPORTING_AGENT_FINDING_TYPES = {"finding"}

DEFAULT_REMEDIATION_SCOPE = [
    "Rotate fallback token",
    "Disable fallback token path",
]
DEFAULT_OIDC_REMEDIATION_SCOPE = [
    "Revoke federated sessions",
    "Tighten OIDC trust policy",
    "Patch export scope",
]


@dataclass(frozen=True)
class AgentTurnRequest:
    """One inbound Band-routed turn for one Sentinel Relay agent."""

    target_agent_id: str
    room_snapshot: Mapping[str, Any] | None = None
    inbound_message: Mapping[str, Any] | None = None
    task: Mapping[str, Any] | None = None
    sequence: int | None = None
    incident_id: str | None = None
    incident_dir: Path | str | None = None


@dataclass(frozen=True)
class AgentTurnResult:
    """Validated agent output plus the body expected by the web API route."""

    context: AgentTurnContext
    message: dict[str, Any]
    post_body: dict[str, Any]


def run_turn(
    request: AgentTurnRequest,
    *,
    handles: Mapping[str, HandleTurn] | None = None,
) -> AgentTurnResult:
    """Execute one target agent turn from a Band-style snapshot.

    ``handles`` is injectable for tests, but production code normally lets the
    adapter lazily import the target agent by Sentinel Relay agent id.
    """

    snapshot = normalize_room_snapshot(request.room_snapshot)
    inbound_message = normalize_inbound_message(request.inbound_message)
    packet = load_incident(
        resolve_incident_dir(
            incident_id=request.incident_id or case_id_from_inputs(snapshot, inbound_message, request.task),
            incident_dir=request.incident_dir,
        )
    )
    recent_messages = recent_messages_from_snapshot(snapshot, inbound_message)
    sequence = request.sequence or next_sequence(snapshot, inbound_message)
    task = dict(request.task) if request.task is not None else task_from_inbound_message(
        inbound_message,
        request.target_agent_id,
        recent_messages=recent_messages,
        packet=packet,
    )
    context = build_turn_context(
        packet=packet,
        snapshot=snapshot,
        target_agent_id=request.target_agent_id,
        task=task,
        sequence=sequence,
        recent_messages=recent_messages,
    )
    handle_turn = (handles or {}).get(request.target_agent_id) or resolve_handle_turn(
        request.target_agent_id
    )
    message = run_agent_turn(handle_turn, context)
    return AgentTurnResult(
        context=context,
        message=message,
        post_body=build_collaboration_post_body(context.room_id, message),
    )


def build_turn_context(
    *,
    packet: IncidentPacket,
    snapshot: Mapping[str, Any] | None,
    target_agent_id: str,
    task: Mapping[str, Any],
    sequence: int,
    recent_messages: list[dict[str, Any]] | None = None,
) -> AgentTurnContext:
    """Assemble the business-logic context from fixture evidence + room state."""

    if target_agent_id not in packet.agents:
        known = ", ".join(sorted(packet.agents))
        raise ValueError(f"Unknown target agent {target_agent_id!r}. Known agents: {known}")

    snapshot = normalize_room_snapshot(snapshot)
    room_id = room_id_from_snapshot(snapshot, packet)
    case = case_from_snapshot(packet, snapshot, room_id)

    return AgentTurnContext(
        case=case,
        room_id=room_id,
        agent_profile=agent_profile_from_snapshot(packet, snapshot, target_agent_id),
        recent_messages=recent_messages
        if recent_messages is not None
        else recent_messages_from_snapshot(snapshot),
        evidence=[dict(item) for item in packet.evidence],
        current_state=state_from_snapshot(packet, snapshot, room_id, case["id"]),
        task=dict(task),
        sequence=sequence,
    )


def resolve_handle_turn(agent_id: str) -> HandleTurn:
    """Return the local ``handle_turn`` callable for a Sentinel Relay agent id."""

    module_name = AGENT_MODULES.get(agent_id)
    if not module_name:
        known = ", ".join(sorted(AGENT_MODULES))
        raise ValueError(f"No handle_turn is registered for {agent_id!r}. Known agents: {known}")

    module = import_module(module_name)
    handle_turn = getattr(module, "handle_turn", None)
    if not callable(handle_turn):
        raise TypeError(f"{module_name} does not expose a callable handle_turn")
    return handle_turn


def build_collaboration_post_body(room_id: str, message: Mapping[str, Any]) -> dict[str, Any]:
    """Build the JSON body for POST /api/collaboration/messages."""

    return {
        "action": "sendMessage",
        "roomId": room_id,
        "message": dict(message),
    }


def case_id_from_inputs(
    snapshot: Mapping[str, Any] | None,
    inbound_message: Mapping[str, Any] | None = None,
    task: Mapping[str, Any] | None = None,
) -> str | None:
    """Infer a case id from the room snapshot, inbound message, or explicit task."""

    snapshot = normalize_room_snapshot(snapshot)
    room = _room_from_snapshot(snapshot)
    candidates = (
        room.get("caseId"),
        snapshot.get("caseId"),
        (inbound_message or {}).get("caseId") if isinstance(inbound_message, Mapping) else None,
        (task or {}).get("caseId") if isinstance(task, Mapping) else None,
        (task or {}).get("incidentId") if isinstance(task, Mapping) else None,
    )
    for candidate in candidates:
        if candidate:
            return str(candidate)
    return None


def policy_id_from_packet(packet: IncidentPacket | None) -> str:
    if packet and packet.policy.get("policyId"):
        return str(packet.policy["policyId"])
    return "SEC-IR-API-KEY-001"


def default_remediation_scope(packet: IncidentPacket | None) -> list[str]:
    if policy_id_from_packet(packet) == "SEC-IR-OIDC-002":
        return list(DEFAULT_OIDC_REMEDIATION_SCOPE)
    return list(DEFAULT_REMEDIATION_SCOPE)


def normalize_room_snapshot(snapshot: Mapping[str, Any] | None) -> dict[str, Any]:
    """Accept either a CollaborationRoomSnapshot or ``{ snapshot: ... }`` body."""

    if not snapshot:
        return {}
    if isinstance(snapshot.get("snapshot"), Mapping):
        return dict(snapshot["snapshot"])
    return dict(snapshot)


def normalize_inbound_message(message: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Extract a canonical AgentMessage from a Band event wrapper when present."""

    if not message:
        return None
    if message.get("schemaVersion"):
        return dict(message)

    metadata = _metadata_from_event(message)
    payload = metadata.get("payload")
    if isinstance(payload, Mapping) and payload.get("schemaVersion"):
        return dict(payload)

    nested_event = message.get("event")
    if isinstance(nested_event, Mapping):
        return normalize_inbound_message(nested_event)

    return dict(message)


def messages_from_snapshot(snapshot: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    """Return canonical messages from the known room snapshot shapes."""

    snapshot = normalize_room_snapshot(snapshot)
    candidates = (
        snapshot.get("messages"),
        snapshot.get("transcript"),
        _room_from_snapshot(snapshot).get("messages"),
    )
    for candidate in candidates:
        if isinstance(candidate, list):
            messages = [
                normalize_inbound_message(item) or dict(item)
                for item in candidate
                if isinstance(item, Mapping)
            ]
            return sorted(messages, key=_message_sort_key)
    return []


def recent_messages_from_snapshot(
    snapshot: Mapping[str, Any] | None,
    inbound_message: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Include the inbound message even if the caller has not mirrored it yet."""

    messages = messages_from_snapshot(snapshot)
    inbound = normalize_inbound_message(inbound_message)
    if not inbound:
        return messages

    inbound_id = inbound.get("id")
    if inbound_id and any(message.get("id") == inbound_id for message in messages):
        return messages
    return sorted([*messages, inbound], key=_message_sort_key)


def next_sequence(
    snapshot: Mapping[str, Any] | None,
    inbound_message: Mapping[str, Any] | None = None,
) -> int:
    """Return the next room-local AgentMessage sequence number."""

    sequences = [
        sequence
        for message in recent_messages_from_snapshot(snapshot, inbound_message)
        if isinstance((sequence := message.get("sequence")), int)
        and not isinstance(sequence, bool)
    ]
    return max(sequences, default=0) + 1


def task_from_inbound_message(
    inbound_message: Mapping[str, Any] | None,
    target_agent_id: str,
    *,
    recent_messages: list[Mapping[str, Any]] | None = None,
    packet: IncidentPacket | None = None,
) -> dict[str, Any]:
    """Infer the local agent task from a routed AgentMessage.

    Explicit tasks should still be supplied for Commander planning turns. This
    inference covers the common Band-routed turns: assignments to specialists,
    human approval decisions back to the Band Leader, and approved remediation.
    """

    inbound = normalize_inbound_message(inbound_message)
    if not inbound:
        return default_task_for_agent(target_agent_id, recent_messages=recent_messages, packet=packet)

    message_type = inbound.get("type")
    payload = inbound.get("payload") if isinstance(inbound.get("payload"), Mapping) else {}
    payload_kind = payload.get("kind")
    data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
    source = {"sourceMessageId": inbound.get("id")}

    if message_type == "task_assignment" or payload_kind == "task_assignment":
        assigned_to = data.get("assignedToAgentId") or data.get("assigned_to_agent_id")
        if assigned_to and assigned_to != target_agent_id:
            raise ValueError(
                f"Inbound task {inbound.get('id')!r} is assigned to {assigned_to!r}, "
                f"not {target_agent_id!r}."
            )
        return _task_for_assignment(target_agent_id, data, recent_messages, source, packet)

    if target_agent_id in REPORTING_AGENT_IDS and (
        message_type == "handoff" or payload_kind == "cross_review"
    ):
        review_round_id = data.get("reviewRoundId") or f"review-{(inbound.get('caseId') or 'incident').lower()}-1"
        return {
            **source,
            "kind": "cross_review",
            "reviewRoundId": review_round_id,
            "sourceFindingMessageIds": _string_list(data.get("sourceFindingMessageIds")),
        }

    if target_agent_id == "agent-commander" and (
        message_type == "approval_decision" or payload_kind == "approval_decision"
    ):
        approved_scope = _approved_scope_from_data(data) or default_remediation_scope(packet)
        return {
            **source,
            "kind": "assign",
            "assignee": "agent-remediation",
            "assigneeName": "Remediation",
            "objective": "Execute the approved containment scope only.",
            "approvedScope": approved_scope,
        }

    if target_agent_id == "agent-commander" and _should_request_cross_review(inbound, recent_messages):
        return {**source, "kind": "request_cross_review"}

    if target_agent_id == "agent-commander" and _should_assign_risk(inbound, recent_messages):
        return {
            **source,
            "kind": "assign",
            "assignee": "agent-risk-compliance",
            "assigneeName": "Risk & Compliance",
            "objective": "Rule on severity and required approvals per the incident policy.",
            "policyId": policy_id_from_packet(packet),
        }

    if target_agent_id == "agent-commander" and _should_request_approval(inbound, recent_messages):
        return {**source, "kind": "request_approval"}

    if target_agent_id == "agent-commander" and _should_generate_report(inbound, recent_messages):
        return {**source, "kind": "generate_report"}

    return default_task_for_agent(
        target_agent_id,
        recent_messages=recent_messages,
        source=source,
        packet=packet,
    )


def default_task_for_agent(
    target_agent_id: str,
    *,
    recent_messages: list[Mapping[str, Any]] | None = None,
    source: Mapping[str, Any] | None = None,
    packet: IncidentPacket | None = None,
) -> dict[str, Any]:
    """Fallback task when a live worker gets a generic @mention."""

    base = dict(source or {})
    if target_agent_id == "agent-commander":
        return {**base, "kind": "open_case"}
    if target_agent_id in REPORTING_AGENT_IDS:
        return {**base, "kind": "report"}
    if target_agent_id == "agent-risk-compliance":
        return {**base, "kind": "assess", "policyId": policy_id_from_packet(packet)}
    if target_agent_id == "agent-remediation":
        return {
            **base,
            "kind": "remediate",
            "approvedScope": _latest_approved_scope(recent_messages) or default_remediation_scope(packet),
        }

    known = ", ".join(sorted(AGENT_MODULES))
    raise ValueError(f"No default task is known for {target_agent_id!r}. Known agents: {known}")


def room_id_from_snapshot(snapshot: Mapping[str, Any] | None, packet: IncidentPacket) -> str:
    snapshot = normalize_room_snapshot(snapshot)
    room = _room_from_snapshot(snapshot)
    return str(
        room.get("id")
        or room.get("roomId")
        or snapshot.get("roomId")
        or snapshot.get("id")
        or packet.case["roomId"]
    )


def case_from_snapshot(
    packet: IncidentPacket,
    snapshot: Mapping[str, Any] | None,
    room_id: str,
) -> dict[str, Any]:
    snapshot = normalize_room_snapshot(snapshot)
    room = _room_from_snapshot(snapshot)
    case = dict(packet.case)
    if room.get("caseId"):
        case["id"] = room["caseId"]
    if room.get("title"):
        case["title"] = room["title"]
    case["roomId"] = room_id
    return case


def state_from_snapshot(
    packet: IncidentPacket,
    snapshot: Mapping[str, Any] | None,
    room_id: str,
    case_id: str,
) -> dict[str, Any]:
    snapshot = normalize_room_snapshot(snapshot)
    state = (
        dict(snapshot["state"])
        if isinstance(snapshot.get("state"), Mapping)
        else dict(packet.state)
    )
    state["roomId"] = room_id
    state["caseId"] = case_id

    registered_agents = snapshot.get("registeredAgents")
    if isinstance(registered_agents, list):
        state["activeAgentIds"] = [
            agent["id"]
            for agent in registered_agents
            if isinstance(agent, Mapping) and isinstance(agent.get("id"), str)
        ] or state.get("activeAgentIds", [])

    return state


def agent_profile_from_snapshot(
    packet: IncidentPacket,
    snapshot: Mapping[str, Any] | None,
    target_agent_id: str,
) -> dict[str, Any]:
    snapshot = normalize_room_snapshot(snapshot)
    registered_agents = snapshot.get("registeredAgents")
    if isinstance(registered_agents, list):
        for agent in registered_agents:
            if isinstance(agent, Mapping) and agent.get("id") == target_agent_id:
                return dict(agent)
    return dict(packet.agents[target_agent_id])


def _task_for_assignment(
    target_agent_id: str,
    data: Mapping[str, Any],
    recent_messages: list[Mapping[str, Any]] | None,
    source: Mapping[str, Any],
    packet: IncidentPacket | None,
) -> dict[str, Any]:
    objective = data.get("objective")
    base = {
        **dict(source),
        "objective": objective,
        "taskId": data.get("taskId"),
    }

    if target_agent_id in REPORTING_AGENT_IDS:
        return _without_none({**base, "kind": "report"})
    if target_agent_id == "agent-risk-compliance":
        return _without_none(
            {
                **base,
                "kind": "assess",
                "policyId": data.get("policyId") or policy_id_from_packet(packet),
            }
        )
    if target_agent_id == "agent-remediation":
        return _without_none(
            {
                **base,
                "kind": "remediate",
                "approvedScope": _approved_scope_from_data(data)
                or _latest_approved_scope(recent_messages)
                or default_remediation_scope(packet),
            }
        )
    if target_agent_id == "agent-commander":
        return _without_none({**base, "kind": "open_case"})

    return default_task_for_agent(
        target_agent_id,
        recent_messages=recent_messages,
        source=source,
        packet=packet,
    )


def _latest_approved_scope(
    recent_messages: list[Mapping[str, Any]] | None,
) -> list[str] | None:
    for message in reversed(recent_messages or []):
        inbound = normalize_inbound_message(message)
        if not inbound:
            continue
        payload = inbound.get("payload") if isinstance(inbound.get("payload"), Mapping) else {}
        data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
        approved_scope = _approved_scope_from_data(data)
        if approved_scope:
            return approved_scope
    return None


def _should_assign_risk(
    inbound: Mapping[str, Any],
    recent_messages: list[Mapping[str, Any]] | None,
) -> bool:
    if inbound.get("type") != "verification" or inbound.get("agentId") not in REPORTING_AGENT_IDS:
        return False
    messages = recent_messages or []
    if _assignment_exists(messages, "agent-risk-compliance"):
        return False
    return _all_review_verifications_present(messages)


def _should_request_cross_review(
    inbound: Mapping[str, Any],
    recent_messages: list[Mapping[str, Any]] | None,
) -> bool:
    if inbound.get("type") not in REPORTING_AGENT_FINDING_TYPES:
        return False
    if inbound.get("agentId") not in REPORTING_AGENT_IDS:
        return False
    messages = recent_messages or []
    if _cross_review_handoff_exists(messages):
        return False
    if _assignment_exists(messages, "agent-risk-compliance"):
        return False
    reporting_agents_with_findings = {
        message.get("agentId")
        for message in messages
        if message.get("type") in REPORTING_AGENT_FINDING_TYPES
        and message.get("agentId") in REPORTING_AGENT_IDS
    }
    return REPORTING_AGENT_IDS.issubset(reporting_agents_with_findings)


def _all_review_verifications_present(messages: list[Mapping[str, Any]]) -> bool:
    reviewers = {
        message.get("agentId")
        for message in messages
        if message.get("type") == "verification" and message.get("agentId") in REPORTING_AGENT_IDS
    }
    return set(REVIEW_AGENT_IDS).issubset(reviewers)


def _cross_review_handoff_exists(messages: list[Mapping[str, Any]]) -> bool:
    for message in messages:
        if message.get("type") != "handoff":
            continue
        payload = message.get("payload") if isinstance(message.get("payload"), Mapping) else {}
        if payload.get("kind") == "cross_review":
            return True
    return False


def _should_request_approval(
    inbound: Mapping[str, Any],
    recent_messages: list[Mapping[str, Any]] | None,
) -> bool:
    payload = inbound.get("payload") if isinstance(inbound.get("payload"), Mapping) else {}
    payload_kind = payload.get("kind")
    if inbound.get("agentId") != "agent-risk-compliance":
        return False
    if inbound.get("type") not in {"challenge", "risk_assessment"} and payload_kind != "risk_assessment":
        return False
    return not _message_type_exists(recent_messages, "approval_request")


def _should_generate_report(
    inbound: Mapping[str, Any],
    recent_messages: list[Mapping[str, Any]] | None,
) -> bool:
    if inbound.get("agentId") != "agent-remediation" or inbound.get("type") != "remediation_task":
        return False
    return not _message_type_exists(recent_messages, "report_section")


def _assignment_exists(
    messages: list[Mapping[str, Any]] | None,
    assigned_to_agent_id: str,
) -> bool:
    for message in messages or []:
        if message.get("type") != "task_assignment":
            continue
        payload = message.get("payload") if isinstance(message.get("payload"), Mapping) else {}
        data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
        if data.get("assignedToAgentId") == assigned_to_agent_id:
            return True
    return False


def _message_type_exists(
    messages: list[Mapping[str, Any]] | None,
    message_type: str,
) -> bool:
    return any(message.get("type") == message_type for message in messages or [])


def _approved_scope_from_data(data: Mapping[str, Any]) -> list[str] | None:
    candidates = (
        data.get("approvedScope"),
        data.get("approved_action_scope"),
        data.get("approvedActions"),
        data.get("approved_actions"),
    )
    for candidate in candidates:
        if isinstance(candidate, list):
            scope = [str(item) for item in candidate if str(item).strip()]
            if scope:
                return scope
    return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _metadata_from_event(message: Mapping[str, Any]) -> dict[str, Any]:
    metadata = message.get("metadata")
    if isinstance(metadata, Mapping):
        return dict(metadata)

    event = message.get("event")
    if isinstance(event, Mapping) and isinstance(event.get("metadata"), Mapping):
        return dict(event["metadata"])

    return {}


def _room_from_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    room = snapshot.get("room")
    return dict(room) if isinstance(room, Mapping) else {}


def _message_sort_key(message: Mapping[str, Any]) -> tuple[int, str, str]:
    sequence = message.get("sequence")
    safe_sequence = sequence if isinstance(sequence, int) and not isinstance(sequence, bool) else 0
    return safe_sequence, str(message.get("createdAt", "")), str(message.get("id", ""))


def _without_none(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if item is not None}
