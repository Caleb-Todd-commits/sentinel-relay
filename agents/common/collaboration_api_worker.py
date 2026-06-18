"""Collaboration API worker loop for Sentinel Relay agents.

This worker is the pragmatic live-demo bridge:

1. poll the app's ``/api/collaboration/rooms`` snapshot for routed messages,
2. run the addressed local agent through ``common.turn_adapter``,
3. post the validated ``AgentMessage`` back through ``/api/collaboration/messages``.

The Next.js route owns Band publishing, mention text, structured events, and the
local dashboard mirror, so Python workers do not need browser code or secrets in
the repo. The worker uses only the standard library and can be tested offline.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from common.turn_adapter import (
    AgentTurnRequest,
    AgentTurnResult,
    messages_from_snapshot,
    run_turn,
)

COMMANDER_AGENT_ID = "agent-commander"
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


class CollaborationApiError(RuntimeError):
    """Raised when the app collaboration API cannot satisfy a worker request."""


class CollaborationApiClient:
    """Small JSON client for the Sentinel Relay app collaboration routes."""

    def __init__(self, base_url: str, *, timeout_seconds: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def get_room_snapshot(self, room_id: str) -> dict[str, Any]:
        params = urllib.parse.urlencode({"roomId": room_id})
        body = self._request_json("GET", f"/api/collaboration/rooms?{params}")
        snapshot = body.get("snapshot") if isinstance(body, Mapping) else None
        if not isinstance(snapshot, Mapping):
            raise CollaborationApiError(f"No collaboration snapshot found for room {room_id!r}.")
        return dict(snapshot)

    def post_message(self, post_body: Mapping[str, Any]) -> dict[str, Any]:
        body = self._request_json("POST", "/api/collaboration/messages", post_body)
        return dict(body) if isinstance(body, Mapping) else {}

    def _request_json(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
    ) -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return _decode_json(response.read())
        except urllib.error.HTTPError as exc:
            body = _decode_json(exc.read())
            message = _extract_error_message(body) or f"HTTP {exc.code}"
            raise CollaborationApiError(f"Collaboration API {method} {path} failed: {message}") from exc
        except urllib.error.URLError as exc:
            raise CollaborationApiError(f"Unable to reach Sentinel Relay app at {self.base_url}: {exc}") from exc


@dataclass
class WorkerState:
    processed_inbound_ids: set[str] = field(default_factory=set)
    posted_message_ids: set[str] = field(default_factory=set)

    @classmethod
    def from_json(cls, value: Mapping[str, Any]) -> "WorkerState":
        return cls(
            processed_inbound_ids=set(_string_list(value.get("processedInboundIds"))),
            posted_message_ids=set(_string_list(value.get("postedMessageIds"))),
        )

    def to_json(self) -> dict[str, list[str]]:
        return {
            "processedInboundIds": sorted(self.processed_inbound_ids),
            "postedMessageIds": sorted(self.posted_message_ids),
        }


class MemoryWorkerStateStore:
    """In-memory state store used by offline verification."""

    def __init__(self, state: WorkerState | None = None) -> None:
        self.state = state or WorkerState()

    def load(self) -> WorkerState:
        return self.state

    def save(self, state: WorkerState) -> None:
        self.state = state


class JsonFileWorkerStateStore:
    """Tiny JSON store so restarted workers do not replay old inbound messages."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    @classmethod
    def default(cls, agent_id: str, room_id: str) -> "JsonFileWorkerStateStore":
        safe_key = re.sub(r"[^A-Za-z0-9_.-]+", "-", f"{agent_id}-{room_id}").strip("-")
        return cls(Path(tempfile.gettempdir()) / f"sentinel-relay-worker-{safe_key}.json")

    def load(self) -> WorkerState:
        if not self.path.exists():
            return WorkerState()
        try:
            parsed = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return WorkerState()
        return WorkerState.from_json(parsed if isinstance(parsed, Mapping) else {})

    def save(self, state: WorkerState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(state.to_json(), indent=2), encoding="utf-8")


@dataclass
class CollaborationApiWorker:
    """Poll one room for messages addressed to one Sentinel Relay agent."""

    agent_id: str
    client: CollaborationApiClient
    state_store: MemoryWorkerStateStore | JsonFileWorkerStateStore

    def run_once(self, room_id: str) -> AgentTurnResult | None:
        snapshot = self.client.get_room_snapshot(room_id)
        state = self.state_store.load()
        inbound_message = select_next_actionable_message(
            snapshot,
            self.agent_id,
            processed_inbound_ids=state.processed_inbound_ids,
        )
        if inbound_message is None:
            return None

        result = run_turn(
            AgentTurnRequest(
                target_agent_id=self.agent_id,
                room_snapshot=snapshot,
                inbound_message=inbound_message,
            )
        )
        self.client.post_message(result.post_body)

        inbound_id = str(inbound_message.get("id", ""))
        if inbound_id:
            state.processed_inbound_ids.add(inbound_id)
        state.posted_message_ids.add(result.message["id"])
        self.state_store.save(state)
        return result

    def run_forever(
        self,
        room_id: str,
        *,
        poll_seconds: float,
        once: bool = False,
        max_turns: int | None = None,
    ) -> None:
        completed_turns = 0
        print(f"Starting {self.agent_id} collaboration API worker for room {room_id}.")
        while True:
            result = self.run_once(room_id)
            if result:
                completed_turns += 1
                print(
                    f"{self.agent_id} posted {result.message['id']} "
                    f"({result.message['type']}): {result.message['title']}"
                )
            if once or (max_turns is not None and completed_turns >= max_turns):
                return
            time.sleep(poll_seconds)


def select_next_actionable_message(
    snapshot: Mapping[str, Any],
    agent_id: str,
    *,
    processed_inbound_ids: set[str] | None = None,
) -> dict[str, Any] | None:
    """Find the next routed message this worker should answer."""

    processed = processed_inbound_ids or set()
    messages = messages_from_snapshot(snapshot)
    for message in messages:
        message_id = str(message.get("id", ""))
        if message_id in processed:
            continue
        if message.get("agentId") == agent_id:
            continue
        if agent_id not in (message.get("targetAgentIds") or []):
            continue
        if is_actionable_message(messages, agent_id, message):
            return message
    return None


def is_actionable_message(
    room_messages: list[Mapping[str, Any]],
    agent_id: str,
    message: Mapping[str, Any],
) -> bool:
    """Return True when an inbound routed message should trigger one agent turn."""

    if agent_id != COMMANDER_AGENT_ID:
        if message.get("type") == "task_assignment":
            return _assigned_to(message) == agent_id
        if agent_id in REPORTING_AGENT_IDS and _is_cross_review_handoff(message):
            return True
        return False

    message_type = message.get("type")
    sender = message.get("agentId")

    if message_type == "finding" and sender in REPORTING_AGENT_IDS:
        return (
            _all_reporting_findings_present(room_messages)
            and not _cross_review_handoff_exists(room_messages)
            and not _assignment_exists(room_messages, "agent-risk-compliance")
        )

    if message_type == "verification" and sender in REPORTING_AGENT_IDS:
        return _all_review_verifications_present(room_messages) and not _assignment_exists(
            room_messages,
            "agent-risk-compliance",
        )

    if message_type in {"challenge", "risk_assessment"} and sender == "agent-risk-compliance":
        return not _message_type_exists(room_messages, "approval_request")

    if message_type == "approval_decision":
        return not _assignment_exists(room_messages, "agent-remediation")

    if message_type == "remediation_task" and sender == "agent-remediation":
        return not _message_type_exists(room_messages, "report_section")

    return False


def run_collaboration_api_worker_entrypoint(
    *,
    sentinel_agent_id: str,
    agent_name: str,
) -> None:
    room_id = _read_env("SENTINEL_RELAY_AGENT_ROOM_ID")
    if not room_id:
        raise SystemExit(
            f"{agent_name} needs SENTINEL_RELAY_AGENT_ROOM_ID when "
            "SENTINEL_RELAY_AGENT_RUNTIME=collaboration-api."
        )

    app_url = _read_env("SENTINEL_RELAY_APP_URL") or "http://127.0.0.1:3000"
    poll_seconds = _read_float_env("SENTINEL_RELAY_AGENT_POLL_SECONDS", default=2.0)
    once = (_read_env("SENTINEL_RELAY_AGENT_ONCE") or "").lower() == "true"
    max_turns_value = _read_env("SENTINEL_RELAY_AGENT_MAX_TURNS")
    max_turns = int(max_turns_value) if max_turns_value else None
    state_file = _read_env("SENTINEL_RELAY_AGENT_STATE_FILE")
    state_store = (
        JsonFileWorkerStateStore(state_file)
        if state_file
        else JsonFileWorkerStateStore.default(sentinel_agent_id, room_id)
    )

    client = CollaborationApiClient(app_url)
    worker = CollaborationApiWorker(
        agent_id=sentinel_agent_id,
        client=client,
        state_store=state_store,
    )
    worker.run_forever(
        room_id,
        poll_seconds=poll_seconds,
        once=once,
        max_turns=max_turns,
    )


def _assigned_to(message: Mapping[str, Any]) -> str | None:
    payload = message.get("payload") if isinstance(message.get("payload"), Mapping) else {}
    data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
    assigned_to = data.get("assignedToAgentId") or data.get("assigned_to_agent_id")
    return str(assigned_to) if assigned_to else None


def _all_reporting_findings_present(messages: list[Mapping[str, Any]]) -> bool:
    agents_with_findings = {
        message.get("agentId")
        for message in messages
        if message.get("type") == "finding" and message.get("agentId") in REPORTING_AGENT_IDS
    }
    return REPORTING_AGENT_IDS.issubset(agents_with_findings)


def _all_review_verifications_present(messages: list[Mapping[str, Any]]) -> bool:
    agents_with_reviews = {
        message.get("agentId")
        for message in messages
        if message.get("type") == "verification" and message.get("agentId") in REPORTING_AGENT_IDS
    }
    return set(REVIEW_AGENT_IDS).issubset(agents_with_reviews)


def _is_cross_review_handoff(message: Mapping[str, Any]) -> bool:
    if message.get("type") != "handoff":
        return False
    payload = message.get("payload") if isinstance(message.get("payload"), Mapping) else {}
    return payload.get("kind") == "cross_review"


def _cross_review_handoff_exists(messages: list[Mapping[str, Any]]) -> bool:
    return any(_is_cross_review_handoff(message) for message in messages)


def _assignment_exists(
    messages: list[Mapping[str, Any]],
    assigned_to_agent_id: str,
) -> bool:
    return any(
        message.get("type") == "task_assignment"
        and _assigned_to(message) == assigned_to_agent_id
        for message in messages
    )


def _message_type_exists(messages: list[Mapping[str, Any]], message_type: str) -> bool:
    return any(message.get("type") == message_type for message in messages)


def _decode_json(raw: bytes) -> Any:
    if not raw:
        return {}
    text = raw.decode("utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


def _extract_error_message(body: Any) -> str | None:
    if isinstance(body, Mapping):
        error = body.get("error") or body.get("message")
        if isinstance(error, str):
            return error
        if body.get("raw"):
            return str(body["raw"])
    return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _read_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


def _read_float_env(name: str, *, default: float) -> float:
    value = _read_env(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default
