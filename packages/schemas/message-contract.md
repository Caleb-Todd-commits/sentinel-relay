# Message Contract

All agents should produce structured messages.

## AgentMessage

```json
{
  "id": "msg_001",
  "caseId": "inc_api_key_exposure",
  "agentId": "forensics",
  "agentName": "Forensics Agent",
  "type": "finding",
  "title": "Suspicious token usage detected",
  "summary": "Token tok_live_7f3a was used from an unusual region after deployment.",
  "confidence": 0.82,
  "severity": "high",
  "evidence": ["ev_api_002"],
  "createdAt": "2026-06-12T22:45:00Z"
}
```

## Required Message Types

- task_assignment
- finding
- challenge
- risk_assessment
- approval_request
- approval_decision
- remediation_task
- report_section
