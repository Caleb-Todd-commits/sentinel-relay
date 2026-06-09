# Step 7 — Collaboration Provider Layer

## Purpose

Step 7 moves Sentinel Relay from a static mocked workflow into a provider-backed workflow.

The War Room now consumes collaboration activity through a formal provider abstraction instead of assuming that messages only come from local demo state. This matters because the hackathon requires Band to be the real coordination layer, and the codebase needs a clean seam where Mock Mode can be replaced with Band Mode without rewriting the UI.

## Design Goal

The provider layer must satisfy two competing goals:

1. **Reliable demo now** — the project must still run without Band credentials, internet setup, or live agent infrastructure.
2. **Clean Band handoff later** — the provider contract must be close enough to real Band collaboration that Step 8 can wire live rooms/messages without a frontend rewrite.

## Provider Modes

### Mock Mode

Mock Mode is the current default.

It uses an in-memory provider that supports:

- incident room creation
- agent registration
- structured message send/read
- message subscription
- room snapshot subscription
- approval request recording
- human decision recording
- task status updates
- audit event generation
- deterministic replay reset

This is not a fake UI-only mock. The War Room pushes the current staged workflow into the provider and reads back provider messages/snapshots.

### Band Mode Scaffold

Band Mode exists behind the same interface, but it is intentionally routed through server-side API scaffolds.

The browser does **not** hold Band API keys.

Current scaffold routes:

```txt
apps/web/src/app/api/collaboration/rooms/route.ts
apps/web/src/app/api/collaboration/messages/route.ts
apps/web/src/app/api/collaboration/approvals/route.ts
```

These routes currently return clear `501` responses explaining that live Band calls belong in Step 8.

## Why This Architecture Wins

A weak project would build the UI directly around mock arrays and then panic near the end trying to bolt Band on.

This project now has a durable seam:

```txt
War Room UI
  ↓
useIncidentCollaborationWorkflow
  ↓
CollaborationProvider interface
  ↓
MockCollaborationProvider today
  ↓
BandCollaborationProvider through server routes in Step 8
```

This means the demo is stable, but the integration path is not vague.

## Main Files

```txt
apps/web/src/lib/collaboration/CollaborationProvider.ts
apps/web/src/lib/collaboration/types.ts
apps/web/src/lib/collaboration/MockCollaborationProvider.ts
apps/web/src/lib/collaboration/BandCollaborationProvider.ts
apps/web/src/lib/collaboration/getCollaborationProvider.ts
apps/web/src/lib/collaboration/browserConfig.ts
apps/web/src/lib/collaboration/syncMockWorkflowToProvider.ts
apps/web/src/lib/workflow/useIncidentCollaborationWorkflow.ts
apps/web/src/components/war-room/ProviderStatusPanel.tsx
```

## Provider Contract

The provider supports:

```ts
getHealth()
createIncidentRoom(input)
registerAgent(roomId, agent)
sendMessage(roomId, message)
getMessages(roomId)
subscribeToMessages(roomId, callback)
updateTaskStatus(roomId, taskId, status)
requestHumanApproval(roomId, request)
submitHumanDecision(roomId, decision)
getRoomSnapshot(roomId)
subscribeToRoomSnapshot(roomId, callback)
resetRoom(roomId)
hydrateRoomSnapshot(roomId, snapshot)
```

## Room Snapshot

A room snapshot contains:

- room metadata
- messages
- registered agents
- approval requests
- approval decisions
- task statuses
- provider audit events

This lets the UI display not only the incident messages, but also whether the provider itself is behaving correctly.

## Provider Health

The provider reports:

- mode
- status
- label
- summary
- room/message/approval capability status
- warnings
- next steps

The War Room displays this through `ProviderStatusPanel`.

## Security Rule

Band credentials must remain server-side.

Allowed public variables:

```env
NEXT_PUBLIC_COLLABORATION_MODE="mock"
NEXT_PUBLIC_ENABLE_BAND_MODE="false"
NEXT_PUBLIC_COLLABORATION_API_BASE_PATH="/api/collaboration"
```

Server-only variables:

```env
BAND_API_BASE_URL=""
BAND_HUMAN_API_KEY=""
BAND_WORKSPACE_ID=""
BAND_ORG_ID=""
```

Never expose a Band API key through `NEXT_PUBLIC_*`.

## Step 7 Completion Standard

Step 7 is complete when:

- the War Room uses `useIncidentCollaborationWorkflow`
- provider status is visible in the UI
- Mock Mode creates a room
- Mock Mode registers agents
- Mock Mode syncs step messages
- Mock Mode records approvals and task statuses
- provider audit events are visible
- Band Mode is safely scaffolded behind server routes
- no secrets are required for the default demo
