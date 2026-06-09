# Collaboration Provider Contract

## Contract Philosophy

The provider is the boundary between Sentinel Relay product logic and the collaboration transport.

The UI should not care whether messages came from:

- local deterministic replay
- Band room messages
- server-side event streaming
- future persistent storage

The provider gives the War Room one stable interface.

## Core Interface

```ts
interface CollaborationProvider {
  readonly mode: "mock" | "band";
  readonly capabilities: readonly CollaborationCapability[];

  getHealth(): CollaborationProviderHealth;

  createIncidentRoom(input): Promise<CollaborationRoom>;
  registerAgent(roomId, agent): Promise<void>;
  sendMessage(roomId, message): Promise<void>;
  getMessages(roomId): Promise<AgentMessage[]>;
  subscribeToMessages(roomId, callback): () => void;

  updateTaskStatus(roomId, taskId, status): Promise<void>;
  requestHumanApproval(roomId, request): Promise<void>;
  submitHumanDecision(roomId, decision): Promise<void>;

  getRoomSnapshot(roomId): Promise<CollaborationRoomSnapshot | undefined>;
  subscribeToRoomSnapshot(roomId, callback): () => void;

  resetRoom(roomId): Promise<void>;
  hydrateRoomSnapshot(roomId, snapshot): Promise<void>;
}
```

## Required Behavior

### createIncidentRoom

Creates a room for one incident case.

In Mock Mode, this creates an in-memory room.

In Band Mode, this should create or locate a Band room/thread/channel for the incident.

### registerAgent

Adds an agent to the room roster.

In Mock Mode, this updates the in-memory participant list.

In Band Mode, this should map to whatever Band requires to associate an agent identity with a room.

### sendMessage

Sends a structured `AgentMessage`.

This is the most important method because the project should prove that Band carries structured agent-to-agent collaboration state, not just final summaries.

### getMessages / subscribeToMessages

Reads room messages.

Mock Mode supports immediate in-memory subscription.

Band Mode should eventually subscribe through a server-side WebSocket/SSE proxy or polling adapter.

### requestHumanApproval / submitHumanDecision

Records human-in-the-loop control points.

For this hackathon, approval is one of the strongest enterprise-readiness signals.

### getRoomSnapshot

Returns the room-level state needed for debugging, UI status, and audit replay.

## Snapshot Fields

```ts
CollaborationRoomSnapshot = {
  room;
  messages;
  registeredAgents;
  approvalRequests;
  approvalDecisions;
  taskStatuses;
  auditEvents;
}
```

## Extension Rules

Do not add provider-specific fields directly to UI components.

Preferred pattern:

```txt
Provider-specific response
  ↓ normalize
Sentinel Relay provider contract
  ↓ consume
War Room UI
```

## What Not To Do

Do not:

- import Band SDK directly inside React components
- put Band secrets in client env vars
- make Mock Mode diverge from Band Mode schemas
- make the UI depend on provider-specific message shapes
- remove Mock Mode after Band Mode works

Mock Mode remains the emergency demo fallback.
