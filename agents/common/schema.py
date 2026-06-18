"""Schema helpers for Sentinel Relay agents (agents lane).

The authoritative schema is the shared package
``packages/schemas/python/sentinel_relay_schemas`` (Pydantic ``AgentMessage``
v0.4.0). To keep the agents lane runnable with zero installs and zero network in
mock/offline mode, this module mirrors that contract field-for-field using only
the standard library. If the shared Pydantic package happens to be importable it
is used for an extra, stricter validation pass; otherwise the stdlib validator is
authoritative.

Keep the enums and required-field lists below in sync with
``packages/schemas/python/sentinel_relay_schemas/models.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

SCHEMA_VERSION = "0.4.0"

# --- Enums mirrored from the shared Pydantic models -------------------------

SEVERITIES = {"informational", "low", "medium", "high", "critical"}
MESSAGE_TYPES = {
    "case_opened",
    "room_created",
    "agent_joined",
    "task_assignment",
    "finding",
    "challenge",
    "verification",
    "risk_assessment",
    "approval_request",
    "approval_decision",
    "remediation_task",
    "report_section",
    "state_update",
    "handoff",
    "watchdog_alert",
}
VISIBILITIES = {"judge_demo", "internal", "security_lead_only"}

# Required keys on every AgentMessage (optional keys may be omitted/None).
_REQUIRED_FIELDS = (
    "id",
    "schemaVersion",
    "caseId",
    "roomId",
    "sequence",
    "agentId",
    "agentName",
    "type",
    "title",
    "summary",
    "confidence",
    "severity",
    "evidenceIds",
    "createdAt",
    "visibility",
)

_MIN_SUMMARY_LEN = 20

# Deterministic clock base so mock output is byte-stable across runs.
_BASE_TIME = datetime(2026, 6, 12, 21, 8, 0, tzinfo=timezone.utc)


def deterministic_timestamp(sequence: int) -> str:
    """Stable ISO-8601 timestamp derived from message sequence (no wall clock)."""
    stamp = _BASE_TIME + timedelta(seconds=11 * sequence)
    return stamp.strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class AgentTurnContext:
    """Everything an agent needs to answer one turn.

    Mirrors the documented agent input contract (docs/23). The Band transport
    (Person 2's lane) is responsible for assembling this from an inbound
    @mention and for routing the returned message by ``targetAgentIds``.
    """

    case: dict[str, Any]
    room_id: str
    agent_profile: dict[str, Any]
    recent_messages: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    current_state: dict[str, Any]
    task: dict[str, Any]
    sequence: int

    def evidence_by_id(self, evidence_id: str) -> dict[str, Any] | None:
        for item in self.evidence:
            if item.get("id") == evidence_id:
                return item
        return None

    def evidence_ids(self) -> list[str]:
        return [item["id"] for item in self.evidence if "id" in item]


class SchemaError(ValueError):
    """Raised when an AgentMessage fails validation after retries."""


def validate_agent_message(message: dict[str, Any]) -> list[str]:
    """Return a list of human-readable validation errors (empty = valid)."""
    errors: list[str] = []

    for field_name in _REQUIRED_FIELDS:
        if field_name not in message or message[field_name] is None:
            errors.append(f"missing required field: {field_name}")
    if errors:
        return errors

    if message["schemaVersion"] != SCHEMA_VERSION:
        errors.append(
            f"schemaVersion must be {SCHEMA_VERSION!r}, got {message['schemaVersion']!r}"
        )
    if message["type"] not in MESSAGE_TYPES:
        errors.append(f"invalid type: {message['type']!r}")
    if message["severity"] not in SEVERITIES:
        errors.append(f"invalid severity: {message['severity']!r}")
    if message["visibility"] not in VISIBILITIES:
        errors.append(f"invalid visibility: {message['visibility']!r}")

    sequence = message["sequence"]
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        errors.append("sequence must be an integer >= 1")

    confidence = message["confidence"]
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        errors.append("confidence must be a number")
    elif not 0.0 <= float(confidence) <= 1.0:
        errors.append("confidence must be between 0 and 1")

    if not isinstance(message["evidenceIds"], list):
        errors.append("evidenceIds must be a list")
    if not isinstance(message.get("summary", ""), str):
        errors.append("summary must be a string")
    elif len(message["summary"].strip()) < _MIN_SUMMARY_LEN:
        errors.append("summary must be descriptive enough for audit replay (>=20 chars)")

    targets = message.get("targetAgentIds")
    if targets is not None and not isinstance(targets, list):
        errors.append("targetAgentIds must be a list or omitted")

    payload = message.get("payload")
    if payload is not None and not isinstance(payload, dict):
        errors.append("payload must be an object or omitted")

    errors.extend(_validate_with_pydantic_if_available(message))
    return errors


def _validate_with_pydantic_if_available(message: dict[str, Any]) -> list[str]:
    """Best-effort stricter validation against the shared Pydantic schema.

    Returns no errors if the shared package or Pydantic is not installed, so the
    agents lane stays runnable offline with zero dependencies.
    """
    try:  # pragma: no cover - depends on optional install
        from sentinel_relay_schemas.models import AgentMessage  # type: ignore
    except Exception:
        return []

    try:  # pragma: no cover - depends on optional install
        AgentMessage.model_validate(message)
        return []
    except Exception as exc:  # noqa: BLE001 - surface any schema mismatch
        return [f"shared schema rejected message: {exc}"]


def build_message(
    *,
    sequence: int,
    agent_id: str,
    agent_name: str,
    case_id: str,
    room_id: str,
    message_type: str,
    title: str,
    summary: str,
    confidence: float,
    severity: str,
    evidence_ids: list[str],
    target_agent_ids: list[str] | None = None,
    decision_impact: str | None = None,
    next_action: str | None = None,
    payload: dict[str, Any] | None = None,
    visibility: str = "judge_demo",
) -> dict[str, Any]:
    """Assemble a schema-shaped AgentMessage dict (not yet validated)."""
    return {
        "id": f"msg-{case_id.lower()}-{sequence:03d}",
        "schemaVersion": SCHEMA_VERSION,
        "caseId": case_id,
        "roomId": room_id,
        "sequence": sequence,
        "agentId": agent_id,
        "agentName": agent_name,
        "type": message_type,
        "title": title,
        "summary": summary,
        "confidence": confidence,
        "severity": severity,
        "evidenceIds": evidence_ids,
        "targetAgentIds": target_agent_ids if target_agent_ids is not None else [],
        "createdAt": deterministic_timestamp(sequence),
        "visibility": visibility,
        "decisionImpact": decision_impact,
        "nextAction": next_action,
        "correlationId": f"trace-{case_id.lower()}-{sequence:03d}",
        "payload": payload if payload is not None else {"kind": "generic", "data": {}},
    }
