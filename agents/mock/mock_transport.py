"""In-process mock of the Band coordination layer (agents lane, offline).

This stands in for Person 2's real Band transport so the agent flow can run with
zero network or model calls. It mirrors Band's two load-bearing facts:

  * each agent turn is an isolated execution that returns one AgentMessage, and
  * routing is by @mention only: a posted message is delivered to the inboxes of
    the agents named in ``targetAgentIds`` and to no one else.

Every posted message is schema-validated (with retry) before it is "sent", so
off-schema output never reaches the room — exactly as the real provider must behave.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from common.interface import run_agent_turn
from common.schema import AgentTurnContext


@dataclass
class DeliveryRecord:
    sequence: int
    from_agent_id: str
    message_type: str
    target_agent_ids: list[str]
    delivered_to: list[str]


@dataclass
class MockBandRoom:
    """A single mock Band room with mention-based routing and a transcript."""

    room_id: str
    handles: dict[str, str] = field(default_factory=dict)
    transcript: list[dict[str, Any]] = field(default_factory=list)
    inboxes: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    routing_log: list[DeliveryRecord] = field(default_factory=list)

    def register(self, agent_id: str, handle: str) -> None:
        self.handles[agent_id] = handle
        self.inboxes.setdefault(agent_id, [])

    def mention_string(self, target_agent_ids: list[str]) -> str:
        return " ".join(f"@{self.handles.get(t, t)}" for t in target_agent_ids) or "(room broadcast)"

    def post(
        self,
        handle_turn: Callable[[AgentTurnContext], dict[str, Any]],
        ctx: AgentTurnContext,
    ) -> dict[str, Any]:
        """Validate, record, and mention-route one agent turn's output."""
        message = run_agent_turn(handle_turn, ctx)
        self.transcript.append(message)

        targets = message.get("targetAgentIds") or []
        # Empty targets == room broadcast: every registered agent can read it.
        delivered_to = targets if targets else list(self.handles)
        for agent_id in delivered_to:
            self.inboxes.setdefault(agent_id, []).append(message)

        self.routing_log.append(
            DeliveryRecord(
                sequence=message["sequence"],
                from_agent_id=message["agentId"],
                message_type=message["type"],
                target_agent_ids=targets,
                delivered_to=delivered_to,
            )
        )
        return message

    def inbox(self, agent_id: str) -> list[dict[str, Any]]:
        return self.inboxes.get(agent_id, [])
