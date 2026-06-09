#!/usr/bin/env python3
"""Verify that the Step 5 mock workflow references valid demo message and evidence IDs."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO_PATH = ROOT / "packages" / "sample-data" / "demo_incident.json"
WORKFLOW_PATH = ROOT / "apps" / "web" / "src" / "lib" / "workflow" / "mockWorkflowScript.ts"


def main() -> int:
    demo = json.loads(DEMO_PATH.read_text())
    workflow_source = WORKFLOW_PATH.read_text()

    message_ids = {message["id"] for message in demo["messages"]}
    evidence_ids = {evidence["id"] for evidence in demo["evidence"]}
    task_ids = {task["id"] for task in demo["remediationTasks"]}

    referenced_messages = set(re.findall(r'messageId:\s*"([^"]+)"', workflow_source))
    referenced_evidence = set(re.findall(r'"(ev-[^"]+)"', workflow_source))
    referenced_tasks = set(re.findall(r'"(rem-[^"]+)"', workflow_source))

    missing_messages = sorted(referenced_messages - message_ids)
    missing_evidence = sorted(referenced_evidence - evidence_ids)
    missing_tasks = sorted(referenced_tasks - task_ids)

    if missing_messages or missing_evidence or missing_tasks:
        print("Mock workflow verification failed.")
        if missing_messages:
            print(f"Missing message IDs: {', '.join(missing_messages)}")
        if missing_evidence:
            print(f"Missing evidence IDs: {', '.join(missing_evidence)}")
        if missing_tasks:
            print(f"Missing task IDs: {', '.join(missing_tasks)}")
        return 1

    step_count = len(re.findall(r'stepIndex:\s*\d+', workflow_source))
    if step_count < 11:
        print(f"Mock workflow verification failed: expected at least 11 step definitions, found {step_count}.")
        return 1

    print("Mock workflow verification passed.")
    print(f"Workflow steps: {step_count}")
    print(f"Referenced messages: {len(referenced_messages)}")
    print(f"Referenced evidence IDs: {len(referenced_evidence)}")
    print(f"Referenced remediation task IDs: {len(referenced_tasks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
