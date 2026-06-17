"""LLM enrichment layer for live mode (agents lane).

This is the "optional LLM enrichment layer" the agent modules anticipate:
``make_live_handle_turn`` returns a ``handle_turn(ctx) -> AgentMessage`` with the
exact same signature the canned agents use, so the existing seam
(``common.interface.run_agent_turn``) drives it unchanged — including its bounded
retry on off-schema output. Nothing here re-implements the schema validator, the
fixtures loader, or the transport; it only wires the AI/ML API into the seam.

What the model owns vs what the harness owns:
  * The model owns the analytic content: ``type``, ``title``, ``summary``,
    ``confidence``, ``severity``, ``evidenceIds``, ``targetAgentIds``,
    ``decisionImpact``, ``nextAction``, and ``payload`` (same ``payload.kind`` set).
  * The harness stamps the identity/envelope fields (``id``, ``sequence``,
    ``agentId``, ``createdAt``, ...) deterministically — these describe the turn,
    not the reasoning, and stamping them keeps routing/ordering stable so schema
    retries are spent on real content problems, not envelope noise.

Hard rule honored here: on any API/timeout/parse failure this RAISES. It never
returns the canned message in place of a failed live call. The canned output is
used only as a *structural exemplar* inside the prompt (so the model emits the
right shape and ``payload.kind``); it is never the fallback answer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from common.aimlapi_client import AimlapiClient
from common.schema import (
    SCHEMA_VERSION,
    AgentTurnContext,
    deterministic_timestamp,
)

HandleTurn = Callable[[AgentTurnContext], dict[str, Any]]

_RESPONSE_INSTRUCTION = (
    "Return ONLY one JSON object: a single Sentinel Relay AgentMessage v0.4.0. "
    "No markdown, no code fences, no prose before or after. Produce YOUR OWN "
    "analysis of the evidence for this turn — do not copy the reference example, "
    "use it only to match the exact field layout and payload.kind. Keep "
    "schemaVersion exactly \"0.4.0\". Set targetAgentIds to the agent ids this "
    "message should be routed to. The summary must be at least 20 characters and "
    "audit-readable. confidence must be between 0 and 1."
)


def _trim_evidence(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": item.get("id"),
            "kind": item.get("kind"),
            "title": item.get("title"),
            "summary": item.get("summary"),
            "excerpt": item.get("excerpt"),
            "source": item.get("source"),
        }
        for item in evidence
    ]


def _trim_recent(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": m.get("id"),
            "agentId": m.get("agentId"),
            "agentName": m.get("agentName"),
            "type": m.get("type"),
            "title": m.get("title"),
            "summary": m.get("summary"),
            "targetAgentIds": m.get("targetAgentIds"),
        }
        for m in messages
    ]


def _build_user_prompt(ctx: AgentTurnContext, exemplar: dict[str, Any]) -> str:
    """Assemble the user-turn content from the existing turn context."""
    context = {
        "case": ctx.case,
        "roomId": ctx.room_id,
        "yourAgentProfile": ctx.agent_profile,
        "task": {k: v for k, v in ctx.task.items() if not k.startswith("_")},
        "evidence": _trim_evidence(ctx.evidence),
        "recentMessages": _trim_recent(ctx.recent_messages),
        "currentState": ctx.current_state,
        "sequence": ctx.sequence,
    }
    parts = [
        _RESPONSE_INSTRUCTION,
        "",
        "TURN CONTEXT (JSON):",
        json.dumps(context, indent=2, default=str),
        "",
        "REFERENCE EXAMPLE — same shape and payload.kind your discipline emits "
        "for this turn (content is illustrative; write your own):",
        json.dumps(exemplar, indent=2, default=str),
    ]
    # Schema-retry hint: the existing seam puts validation errors on the task so
    # the model can self-correct on the next attempt.
    schema_errors = ctx.task.get("_schema_errors")
    if schema_errors:
        parts += [
            "",
            "YOUR PREVIOUS REPLY FAILED SCHEMA VALIDATION. Fix exactly these and "
            "return corrected JSON only:",
            json.dumps(schema_errors, indent=2),
        ]
    return "\n".join(parts)


def _extract_json(text: str) -> dict[str, Any]:
    """Parse the model's reply into a dict, tolerating stray code fences.

    Raises ``ValueError`` (with the raw text) on failure — the offending output
    is preserved so the runner can log it. This is robustness in parsing, not
    error hiding: a genuinely unparseable reply still raises.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Drop the opening fence (``` or ```json) and the trailing fence.
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        if cleaned.rstrip().endswith("```"):
            cleaned = cleaned.rstrip()[:-3]
    cleaned = cleaned.strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError(f"model reply was not JSON: {text[:1000]!r}")
        try:
            parsed = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError(f"model reply was not JSON ({exc}): {text[:1000]!r}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"model reply was not a JSON object: {text[:500]!r}")
    return parsed


def _stamp_envelope(
    message: dict[str, Any],
    ctx: AgentTurnContext,
    agent_id: str,
    agent_name: str,
) -> dict[str, Any]:
    """Force the turn-identity fields the harness owns (not the model)."""
    case_id = ctx.case["id"]
    message["schemaVersion"] = SCHEMA_VERSION
    message["id"] = f"msg-{case_id.lower()}-{ctx.sequence:03d}"
    message["caseId"] = case_id
    message["roomId"] = ctx.room_id
    message["sequence"] = ctx.sequence
    message["agentId"] = agent_id
    message["agentName"] = agent_name
    message["createdAt"] = deterministic_timestamp(ctx.sequence)
    message["correlationId"] = f"trace-{case_id.lower()}-{ctx.sequence:03d}"
    return message


def make_live_handle_turn(
    *,
    agent_id: str,
    agent_name: str,
    prompt_path: Path | str,
    canned_handle_turn: HandleTurn,
    client: AimlapiClient,
) -> HandleTurn:
    """Build a live ``handle_turn`` for one agent, driven by the AI/ML API.

    ``canned_handle_turn`` is the agent's existing deterministic turn; it is
    called only to produce a structural exemplar for the prompt and is never
    returned as a fallback. The returned callable plugs straight into
    ``run_agent_turn`` so schema validation and retry are reused as-is.
    """
    system_prompt = Path(prompt_path).read_text(encoding="utf-8")

    def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
        exemplar = canned_handle_turn(ctx)  # deterministic; shape reference only
        user_prompt = _build_user_prompt(ctx, exemplar)
        content = client.chat(system=system_prompt, user=user_prompt)  # raises on failure
        message = _extract_json(content)  # raises on parse failure (keeps raw text)
        return _stamp_envelope(message, ctx, agent_id, agent_name)

    return handle_turn
