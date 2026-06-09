# Step 7 Team Handoff

## What Changed

The War Room now runs through a collaboration provider boundary.

Previously, the demo workflow was purely derived from local step state. Now the current step is synchronized into a provider room, then provider messages/snapshots are surfaced in the UI.

## What Teammates Should Know

### Frontend Teammate

Use this hook for the War Room:

```ts
useIncidentCollaborationWorkflow()
```

Do not go back to directly importing the mock workflow hook unless debugging.

### Band/Backend Teammate

Your next work lives here:

```txt
apps/web/src/app/api/collaboration/rooms/route.ts
apps/web/src/app/api/collaboration/messages/route.ts
apps/web/src/app/api/collaboration/approvals/route.ts
```

Do not put Band secrets in React components.

### Agent Teammate

Agent outputs should still produce `AgentMessage` payloads that match the shared schemas.

The provider layer expects structured messages, not free-form text.

### Demo Teammate

The default demo path remains Mock Mode.

This means the app should still work if no one has Band credentials configured.

## How To Run

```bash
pnpm install
pnpm dev
```

Open:

```txt
http://localhost:3000/war-room
```

You should see a provider status panel near the top of the War Room.

## Environment

Keep the default:

```env
NEXT_PUBLIC_COLLABORATION_MODE="mock"
NEXT_PUBLIC_ENABLE_BAND_MODE="false"
```

Do not switch to Band Mode until Step 8 begins.

## Next Step

Step 8 is:

**Connect real Band agent communication.**

That should include:

- exact Band API/SDK mapping
- server-side room creation
- server-side message send/read
- agent registration
- trace IDs
- error handling
- mock fallback toggle
- a live Band smoke test
