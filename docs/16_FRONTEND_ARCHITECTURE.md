# Frontend Architecture

## Purpose

The frontend is the judge-facing command center for Sentinel Relay. It is designed to make multi-agent coordination visible. The app should never feel like a hidden backend process with a final answer pasted into a UI.

The frontend must answer four questions quickly:

1. What happened?
2. Which agents worked on it?
3. What did they pass through Band?
4. Why did the final decision happen?

## Route Architecture

```txt
/
  Product story and main entry point

/demo
  Sample incident setup and demo launch

/war-room
  Main incident command surface

/report
  Final audit-ready report

/status
  Local readiness and baseline check page
```

## Component Architecture

```txt
components/
  SiteHeader.tsx
  AgentRoster.tsx
  MessageStream.tsx
  EvidenceBoard.tsx
  TimelinePanel.tsx
  ApprovalGate.tsx
  ReportPreview.tsx

components/ui/
  Badge.tsx
  MetricCard.tsx

components/war-room/
  IncidentHeader.tsx
  RemediationList.tsx
```

### Component responsibilities

| Component | Responsibility |
|---|---|
| `SiteHeader` | Global navigation and project identity |
| `IncidentHeader` | Case title, severity, room ID, affected system, demo progress |
| `AgentRoster` | Shows specialized agents and their current state |
| `MessageStream` | Shows structured Band-style messages and handoffs |
| `EvidenceBoard` | Shows evidence references and source snippets |
| `TimelinePanel` | Shows incident sequence in a clean audit timeline |
| `ApprovalGate` | Shows human approval requirement and decision record |
| `RemediationList` | Shows approved remediation actions and status |
| `ReportPreview` | Shows whether final report is ready and links to it |
| `Badge` | Small status labels |
| `MetricCard` | Reusable summary metrics |

## Data Architecture

The current baseline uses local TypeScript data:

```txt
src/lib/demo/sentinelRelayDemo.ts
```

That data exports one complete `DemoIncident` object containing:

- `case`
- `agents`
- `messages`
- `evidence`
- `timeline`
- `approvalRequest`
- `approvalDecision`
- `remediationTasks`
- `finalReport`

The old import path still works through:

```txt
src/lib/mockIncident.ts
```

This keeps early components simple while giving the project a more scalable data location.

## Type Contract

The shared UI contract lives in:

```txt
src/lib/types.ts
```

Important types:

- `IncidentCase`
- `AgentProfile`
- `AgentMessage`
- `EvidenceReference`
- `TimelineEvent`
- `ApprovalRequest`
- `ApprovalDecision`
- `RemediationTask`
- `FinalReport`
- `DemoIncident`

The types are intentionally more detailed than the current UI strictly needs. This prevents later Band integration from needing a full contract rewrite.

## Collaboration Provider Architecture

The collaboration abstraction lives in:

```txt
src/lib/collaboration/
```

Files:

- `CollaborationProvider.ts`
- `MockCollaborationProvider.ts`
- `BandCollaborationProvider.ts`
- `getCollaborationProvider.ts`

The frontend is currently rendering from static demo data, but the provider contract is prepared for later work.

The provider needs to support:

- creating an incident room
- registering agents
- sending messages
- fetching messages
- subscribing to messages
- requesting human approval
- submitting human decision

## Design Philosophy

The visual design should feel like an incident command room, not a casual chatbot.

Rules:

- Prefer structured cards over long paragraphs.
- Surface evidence with every major finding.
- Show confidence carefully.
- Show challenges and disagreement clearly.
- Show human approval as a first-class product feature.
- Keep the final report connected to the message stream.

## What Not To Add Yet

Do not add these in the frontend until the core demo is stable:

- Authentication
- User settings
- Multiple organizations
- Complex dashboards
- Real uploaded logs
- Real-time charts
- Notification systems
- Heavy animation libraries
- State management libraries

The project wins by being clear, not by being huge.
