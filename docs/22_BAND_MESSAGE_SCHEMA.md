# 22 — Band Message Schema

Band is the collaboration layer for Sentinel Relay. That means messages sent through Band need to be structured enough for agents, the UI, replay mode, and the final report to understand them.

## Core rule

Every meaningful Band interaction should use this shape:

```txt
BandEnvelope
  └── AgentMessage
        └── optional typed payload
```

## BandEnvelope

The envelope wraps a Sentinel Relay message before it moves through Band.

Required fields:

| Field | Purpose |
|---|---|
| `schemaVersion` | Allows future schema evolution |
| `envelopeType` | Always `sentinel_relay.agent_message` |
| `caseId` | Connects message to incident |
| `roomId` | Connects message to Band room |
| `senderAgentId` | Agent or human sending the message |
| `messageId` | Stable audit reference |
| `sentAt` | ISO timestamp |
| `traceId` | Debugging and replay correlation |
| `payload` | The actual `AgentMessage` |

## AgentMessage

This is the main event object.

Required fields:

| Field | Purpose |
|---|---|
| `id` | Stable message ID |
| `schemaVersion` | Schema version |
| `caseId` | Incident ID |
| `roomId` | Band room ID |
| `sequence` | Replay order |
| `agentId` | Sender ID |
| `agentName` | Display name |
| `type` | Message category |
| `title` | Short visible title |
| `summary` | Human-readable explanation |
| `confidence` | 0 to 1 confidence score |
| `severity` | Security impact level |
| `evidenceIds` | Supporting evidence references |
| `createdAt` | ISO timestamp |
| `visibility` | Demo/internal/security-only visibility |

Recommended fields:

| Field | Purpose |
|---|---|
| `targetAgentIds` | Shows handoff/delegation |
| `decisionImpact` | Explains why message matters |
| `nextAction` | Shows workflow movement |
| `payload` | Type-specific structured data |

## Message types

Current allowed values:

```txt
case_opened
room_created
agent_joined
task_assignment
finding
challenge
verification
risk_assessment
approval_request
approval_decision
remediation_task
report_section
state_update
handoff
watchdog_alert
```

## How to make Band visible in the UI

The War Room should show each message card with:

- sending agent,
- message type,
- title,
- confidence,
- severity,
- evidence IDs,
- target agents,
- decision impact,
- next action.

This is how the demo proves actual coordination rather than hidden orchestration.

## Required collaboration sequence for the demo

The sample incident should include this minimum sequence:

1. Commander opens the case.
2. Commander assigns work.
3. Forensics submits a finding.
4. Threat Intel verifies or qualifies confidence.
5. Code Review submits a finding.
6. Risk & Compliance challenges a conclusion.
7. Commander requests human approval.
8. Human approves limited containment.
9. Remediation creates fix tasks.
10. Commander generates the final report.

## Strongest judge-facing moment

The best Band proof is the challenge message:

> The Risk & Compliance Agent challenges the breach classification because token exposure is likely, but customer impact is not fully proven.

This shows:

- agents are not blindly agreeing,
- evidence matters,
- humans are involved for high-impact decisions,
- Band carries the traceable context.
