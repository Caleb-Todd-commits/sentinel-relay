# Architecture

## System Overview

Sentinel Relay has four main layers:

```txt
Frontend War Room UI
        |
Collaboration Provider Interface
        |
Mock Provider OR Band Provider
        |
Specialized Agents + Structured Messages
```

## Frontend

The frontend is a Next.js dashboard with pages for:

- Landing page
- Demo start page
- War Room
- Final report

The War Room is the primary judge-facing interface.

## Collaboration Provider Pattern

The UI should not directly depend on Band implementation details. It should call a provider interface.

```ts
interface CollaborationProvider {
  createIncidentRoom(caseId: string): Promise<string>;
  registerAgent(roomId: string, agentId: string): Promise<void>;
  sendMessage(roomId: string, message: AgentMessage): Promise<void>;
  getMessages(roomId: string): Promise<AgentMessage[]>;
  subscribeToMessages(roomId: string, callback: (message: AgentMessage) => void): () => void;
  requestHumanApproval(roomId: string, request: ApprovalRequest): Promise<void>;
  submitHumanDecision(roomId: string, decision: ApprovalDecision): Promise<void>;
}
```

Use two implementations:

- `MockCollaborationProvider`
- `BandCollaborationProvider`

## Message Types

The system should use structured messages:

- Finding
- EvidenceReference
- Challenge
- RiskAssessment
- ApprovalRequest
- ApprovalDecision
- RemediationTask
- FinalReportSection

## Agent Flow

```txt
Commander
  -> Forensics
  -> Code Review
  -> Threat Intel
  -> Risk & Compliance
  -> Human Approval
  -> Remediation
  -> Final Report
```

## Human Approval

Any high-impact action should require approval:

- Revoking tokens
- Notifying customers
- Declaring confirmed breach
- Closing incident

## Audit Trail

Every meaningful message should be shown in the War Room and included in the final report.
