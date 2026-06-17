"""The thin seam between Band transport and agent business logic.

Person 2's Band provider is expected to:
  1. assemble an :class:`AgentTurnContext` from an inbound @mention,
  2. call the target agent's ``handle_turn(ctx) -> AgentMessage`` (a plain dict),
  3. post the returned message back to Band, routed by ``targetAgentIds``.

``run_agent_turn`` wraps ``handle_turn`` with schema validation and a bounded
retry so an off-schema response is repaired or rejected before it ever reaches
the wire. This keeps agent logic fully decoupled from Band and from the LLM.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol

from common.schema import (
    AgentTurnContext,
    SchemaError,
    validate_agent_message,
)

# An agent is any callable that turns a context into one AgentMessage dict.
HandleTurn = Callable[[AgentTurnContext], dict[str, Any]]

DEFAULT_MAX_ATTEMPTS = 3


class Agent(Protocol):
    """Structural type for a Sentinel Relay agent definition."""

    agent_id: str
    agent_name: str

    def handle_turn(self, ctx: AgentTurnContext) -> dict[str, Any]: ...


def run_agent_turn(
    handle_turn: HandleTurn,
    ctx: AgentTurnContext,
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> dict[str, Any]:
    """Call ``handle_turn`` and return a schema-valid AgentMessage.

    Retries up to ``max_attempts`` times on off-schema output. The context's
    task carries a ``_schema_errors`` hint on retries so an LLM-backed agent can
    self-correct; deterministic mock agents simply produce valid output first try.
    """
    last_errors: list[str] = []
    for attempt in range(1, max_attempts + 1):
        if last_errors:
            ctx.task = {**ctx.task, "_schema_errors": last_errors, "_attempt": attempt}
        message = handle_turn(ctx)
        errors = validate_agent_message(message)
        if not errors:
            return message
        last_errors = errors

    raise SchemaError(
        f"agent output failed schema validation after {max_attempts} attempts: "
        f"{last_errors}"
    )
