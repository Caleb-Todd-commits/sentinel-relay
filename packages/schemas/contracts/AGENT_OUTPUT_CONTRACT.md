# Agent Output Contract

Each Sentinel Relay agent must output a structured message. The output should never be only a paragraph.

## Standard output shape

```json
{
  "id": "msg-003",
  "schemaVersion": "0.4.0",
  "caseId": "INC-1042",
  "roomId": "band-room-inc-1042",
  "sequence": 3,
  "agentId": "agent-forensics",
  "agentName": "Forensics Agent",
  "type": "finding",
  "title": "Suspicious API token usage identified",
  "summary": "Evidence-backed summary goes here.",
  "confidence": 0.84,
  "severity": "high",
  "evidenceIds": ["ev-api-spike"],
  "targetAgentIds": ["agent-code-review"],
  "createdAt": "2026-06-12T21:09:11Z",
  "visibility": "judge_demo",
  "decisionImpact": "Why this changes the case.",
  "nextAction": "What should happen next.",
  "payload": {
    "kind": "finding",
    "data": {}
  }
}
```

## Agent-specific notes

- Band Leader outputs `case_opened`, `task_assignment`, `approval_request`, `report_section`, and `state_update`.
- Forensics outputs `finding`, `verification`, and `handoff`.
- Threat Intel outputs `verification`, `risk_assessment`, and `challenge` when indicators are weak.
- Code Review outputs `finding`, `verification`, and `remediation_task` suggestions.
- Risk & Compliance outputs `challenge`, `risk_assessment`, and approval requirements.
- Remediation outputs `remediation_task` and post-approval fix plans.

## Human approval rule

Agents may recommend high-impact actions, but they may not mark production containment or external customer notification as approved. Those require a human approval decision message.
