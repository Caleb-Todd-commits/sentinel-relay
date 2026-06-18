# Band Environment Setup

## Normal Demo Mode

Keep the app in Mock Mode unless you are testing live Band.

```env
NEXT_PUBLIC_COLLABORATION_MODE="mock"
NEXT_PUBLIC_ENABLE_BAND_MODE="false"
BAND_PROVIDER_ENABLED="false"
```

## Live Band Mode

Use this only after creating/registering remote agents in Band.

```env
NEXT_PUBLIC_COLLABORATION_MODE="band"
NEXT_PUBLIC_ENABLE_BAND_MODE="true"
BAND_PROVIDER_ENABLED="true"
BAND_API_BASE_URL="https://app.band.ai/api/v1"
BAND_WS_URL="wss://app.band.ai/api/v1/socket/websocket"
BAND_LEADER_AGENT_API_KEY="paste-band-leader-agent-api-key"
BAND_LEADER_AGENT_ID="paste-band-leader-agent-id"
```

## Participant IDs

To allow routed agent-to-agent messages, configure participant IDs for each specialist.

```env
BAND_FORENSICS_PARTICIPANT_ID=""
BAND_THREAT_INTEL_PARTICIPANT_ID=""
BAND_CODE_REVIEW_PARTICIPANT_ID=""
BAND_RISK_COMPLIANCE_PARTICIPANT_ID=""
BAND_REMEDIATION_PARTICIPANT_ID=""
```

Handles and names help form readable @mentions:

```env
BAND_FORENSICS_HANDLE="forensics"
BAND_FORENSICS_NAME="Forensics Agent"
```

## Optional Human API Key

```env
BAND_HUMAN_API_KEY=""
```

This is optional. Without it, the dashboard uses the local server mirror for full incident history.

## Dry Run Mode

Dry run mode lets you test the server adapter without hitting Band.

```env
BAND_PROVIDER_ENABLED="true"
NEXT_PUBLIC_COLLABORATION_MODE="band"
NEXT_PUBLIC_ENABLE_BAND_MODE="true"
BAND_DRY_RUN="true"
BAND_LEADER_AGENT_API_KEY="dry-run"
```

## Python Agent Worker Mode

To run the real Python `handle_turn` agents against the room created by the app,
start the workers in collaboration API mode:

```env
SENTINEL_RELAY_AGENT_RUNTIME="collaboration-api"
SENTINEL_RELAY_APP_URL="http://127.0.0.1:3000"
SENTINEL_RELAY_AGENT_ROOM_ID="paste-room-id-from-war-room"
SENTINEL_RELAY_AGENT_POLL_SECONDS="2"
```

Use this with Band Mode or Band dry run. The workers poll the app mirror and post
back through `/api/collaboration/messages`, so the app server still owns Band
credentials and Band publishing.

## Checks

```bash
pnpm band:env
pnpm band:verify
pnpm band:smoke
```

`band:smoke` calls live Band identity endpoints and requires real credentials. It does not create a chat room.

## Recommended Team Testing Order

1. Keep Mock Mode working.
2. Run `pnpm band:verify`.
3. Configure Band dry run.
4. Start web app in Band Mode dry run.
5. Confirm `/war-room` creates a dry-run room and local mirror.
6. Add real Band Leader key.
7. Run `pnpm band:smoke`.
8. Add participant IDs.
9. Start remote agent workers.
10. Run one live incident replay.
