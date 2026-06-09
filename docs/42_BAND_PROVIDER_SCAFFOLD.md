# Band Provider Scaffold

## Current Status

Band Mode is scaffolded but not connected.

This is intentional.

The goal of Step 7 is to make the provider boundary correct before Step 8 adds the real Band API or SDK calls.

## Why It Uses Server Routes

The frontend should never contain Band secrets.

Instead, `BandCollaborationProvider` calls Sentinel Relay's own Next.js routes:

```txt
/api/collaboration/rooms
/api/collaboration/messages
/api/collaboration/approvals
```

Those routes are where Step 8 should add server-side Band logic.

## Current Route Behavior

The routes return `501` with clear error codes:

```txt
BAND_ADAPTER_NOT_CONNECTED
```

This is better than silent fake success because it prevents the team from thinking live Band is connected when it is not.

## Step 8 Implementation Path

Step 8 should replace the placeholder route logic with real calls:

### Rooms Route

Responsibilities:

- create or locate a Band room for the incident
- register or invite agent identities
- return normalized `CollaborationRoom`
- return normalized `CollaborationRoomSnapshot`

### Messages Route

Responsibilities:

- send Sentinel Relay `AgentMessage` payloads through Band
- read Band room messages
- normalize Band messages back to Sentinel Relay `AgentMessage`
- preserve trace IDs and timestamps

### Approvals Route

Responsibilities:

- post approval requests into the Band room
- record human decisions
- mirror approvals into Sentinel Relay's audit model

### Subscription Strategy

Preferred options:

1. Band WebSocket to server-side proxy, then SSE to browser
2. server-side polling fallback
3. manual refresh fallback

Do not put direct Band socket credentials in browser code unless the Band docs explicitly support a safe public-token model.

## Band Mode Activation

Default env:

```env
NEXT_PUBLIC_COLLABORATION_MODE="mock"
NEXT_PUBLIC_ENABLE_BAND_MODE="false"
```

Future test env:

```env
NEXT_PUBLIC_COLLABORATION_MODE="band"
NEXT_PUBLIC_ENABLE_BAND_MODE="true"
BAND_API_BASE_URL="..."
BAND_HUMAN_API_KEY="..."
```

## Demo Safety Rule

Even after live Band works, keep Mock Mode available.

The final video can show live Band if stable, but the in-person demo should have a deterministic fallback.
