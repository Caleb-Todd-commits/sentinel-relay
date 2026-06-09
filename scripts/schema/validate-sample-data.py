#!/usr/bin/env python3
"""Validate Sentinel Relay sample data using only Python stdlib.

This is intentionally lightweight so teammates can run it before Python dependencies
or Band credentials are configured. It does not replace TypeScript/Pydantic checks;
it catches the schema mistakes most likely to break the demo.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEMO_FILE = ROOT / "packages" / "sample-data" / "demo_incident.json"

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


def is_iso(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_demo(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for key in [
        "schemaVersion",
        "case",
        "state",
        "agents",
        "messages",
        "evidence",
        "timeline",
        "approvalRequest",
        "approvalDecision",
        "remediationTasks",
        "finalReport",
    ]:
        require(key in data, f"Missing top-level field: {key}", errors)

    case = data.get("case", {})
    require(case.get("id"), "case.id is required", errors)
    require(case.get("roomId"), "case.roomId is required", errors)
    require(case.get("severity") in SEVERITIES, "case.severity is invalid", errors)
    require(is_iso(case.get("openedAt", "")), "case.openedAt must be ISO date-time", errors)
    require(is_iso(case.get("updatedAt", "")), "case.updatedAt must be ISO date-time", errors)

    agents = data.get("agents", [])
    require(isinstance(agents, list) and len(agents) >= 3, "At least three agents are required", errors)
    agent_ids = {agent.get("id") for agent in agents if isinstance(agent, dict)}
    required_agents = {"agent-commander", "agent-forensics", "agent-code-review", "agent-risk-compliance"}
    missing_agents = sorted(required_agents - agent_ids)
    require(not missing_agents, f"Missing required agents: {missing_agents}", errors)

    evidence = data.get("evidence", [])
    evidence_ids = {item.get("id") for item in evidence if isinstance(item, dict)}
    require(bool(evidence_ids), "At least one evidence reference is required", errors)

    messages = data.get("messages", [])
    require(isinstance(messages, list) and messages, "At least one agent message is required", errors)

    seen_sequences: list[int] = []
    has_challenge = False
    has_approval = False
    has_remediation = False
    for index, message in enumerate(messages):
        path = f"messages[{index}]"
        require(message.get("id"), f"{path}.id is required", errors)
        require(message.get("schemaVersion"), f"{path}.schemaVersion is required", errors)
        require(message.get("caseId") == case.get("id"), f"{path}.caseId must match case.id", errors)
        require(message.get("roomId") == case.get("roomId"), f"{path}.roomId must match case.roomId", errors)
        require(message.get("agentId") in agent_ids, f"{path}.agentId must reference a known agent", errors)
        require(message.get("type") in MESSAGE_TYPES, f"{path}.type is invalid", errors)
        require(message.get("severity") in SEVERITIES, f"{path}.severity is invalid", errors)
        require(isinstance(message.get("confidence"), (int, float)) and 0 <= message.get("confidence") <= 1, f"{path}.confidence must be 0..1", errors)
        require(is_iso(message.get("createdAt", "")), f"{path}.createdAt must be ISO date-time", errors)
        require(isinstance(message.get("evidenceIds"), list), f"{path}.evidenceIds must be a list", errors)
        for evidence_id in message.get("evidenceIds", []):
            require(evidence_id in evidence_ids, f"{path}.evidenceIds references unknown evidence: {evidence_id}", errors)
        if isinstance(message.get("sequence"), int):
            seen_sequences.append(message["sequence"])
        has_challenge = has_challenge or message.get("type") == "challenge"
        has_approval = has_approval or message.get("type") == "approval_decision"
        has_remediation = has_remediation or message.get("type") == "remediation_task"

    require(seen_sequences == list(range(1, len(messages) + 1)), "message sequences must be contiguous starting at 1", errors)
    require(has_challenge, "Demo must include at least one challenge message", errors)
    require(has_approval, "Demo must include at least one approval decision", errors)
    require(has_remediation, "Demo must include at least one remediation task message", errors)

    final_report = data.get("finalReport", {})
    audit_ids = final_report.get("auditTrailMessageIds", [])
    message_ids = {message.get("id") for message in messages if isinstance(message, dict)}
    require(set(audit_ids).issubset(message_ids), "finalReport.auditTrailMessageIds must reference known messages", errors)

    return errors


def main() -> int:
    if not DEMO_FILE.exists():
        print(f"Missing demo data file: {DEMO_FILE}", file=sys.stderr)
        return 1

    data = json.loads(DEMO_FILE.read_text())
    errors = validate_demo(data)
    if errors:
        print("Schema validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Schema validation passed: {DEMO_FILE.relative_to(ROOT)}")
    print(f"Messages: {len(data['messages'])}; Evidence items: {len(data['evidence'])}; Agents: {len(data['agents'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
