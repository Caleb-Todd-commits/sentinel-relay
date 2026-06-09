# Band Route Contracts

## GET `/api/collaboration/health`

Returns static server-side configuration status without revealing secrets.

Use live check:

```txt
/api/collaboration/health?live=true
```

## POST `/api/collaboration/rooms`

Actions:

```txt
createIncidentRoom
registerAgent
resetRoom
hydrateRoomSnapshot
```

## GET `/api/collaboration/rooms?roomId=...`

Returns the current local dashboard snapshot for a Band room.

## POST `/api/collaboration/messages`

Actions:

```txt
sendMessage
updateTaskStatus
```

`sendMessage` posts the canonical Sentinel Relay `AgentMessage` as a Band event and optionally as a routed text message when target mentions are configured.

## GET `/api/collaboration/messages?roomId=...`

Returns local mirror messages for the room.

## POST `/api/collaboration/approvals`

Actions:

```txt
requestHumanApproval
submitHumanDecision
```

Approval records are stored in the local mirror and posted as Band task events.

## GET `/api/collaboration/stream?roomId=...`

Server-Sent Events stream of the local room mirror.

Events:

```txt
snapshot
heartbeat
error
```

## Error Contract

All recoverable Band configuration/runtime failures return:

```json
{
  "code": "BAND_MISSING_REQUIRED_ENV",
  "error": "Human readable error",
  "recoverable": true,
  "missing": [],
  "warnings": []
}
```

The browser provider turns those into `CollaborationProviderError` objects.
