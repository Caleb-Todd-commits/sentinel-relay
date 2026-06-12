# Step 8 — Real Band Integration

## Goal

Step 8 moves Sentinel Relay from a provider scaffold to a real Band-ready integration layer while preserving Mock Mode as the safe demo fallback.

The implementation now includes:

- Server-side Band REST client
- Server-side room/message/approval routes
- Local room mirror for the dashboard
- Structured Band event payloads
- Routed Band text messages with `@mention` metadata when participant IDs are configured
- Health endpoint for credential checks
- Server-sent event stream for the War Room dashboard mirror
- Python remote agent worker scaffolds using the Band/Thenvoi SDK pattern
- Env and smoke-test scripts

## Why the Integration Is Split

The browser must not hold Band secrets. The app uses this flow:

```txt
War Room UI
  -> BandCollaborationProvider in browser
    -> /api/collaboration/* Next.js server routes
      -> Band REST API using server-side X-API-Key
      -> local Sentinel Relay mirror for judge dashboard state
```

The remote agents use a separate flow:

```txt
Remote Python agent worker
  -> Band/Thenvoi Python SDK
    -> REST for actions
    -> WebSocket for incoming @mentions and room events
```

This gives us a reliable dashboard and the proper live agent model.

## What the Server Adapter Does

### Room creation

`POST /api/collaboration/rooms` with `action=createIncidentRoom` calls:

```txt
POST /api/v1/agent/chats
```

using the Band Leader API key.

It then stores a local dashboard mirror keyed by the returned Band chat ID.

### Agent registration

`POST /api/collaboration/rooms` with `action=registerAgent` stores the agent in the local mirror and, when a participant ID is configured, calls:

```txt
POST /api/v1/agent/chats/{chat_id}/participants
```

### Message sending

`POST /api/collaboration/messages` with `action=sendMessage` does two things:

1. Stores the canonical `AgentMessage` in the local mirror.
2. Posts a structured Band event:

```txt
POST /api/v1/agent/chats/{chat_id}/events
```

If `targetAgentIds` are configured with Band participant IDs, it also sends a routed Band text message:

```txt
POST /api/v1/agent/chats/{chat_id}/messages
```

Text messages require mentions, so messages without configured targets are recorded as events only.

### Approval requests and decisions

`POST /api/collaboration/approvals` records approval requests and decisions in the local mirror and posts them to Band as structured task events.

### Dashboard subscription

`GET /api/collaboration/stream?roomId=...` streams the local mirror to the War Room through Server-Sent Events. This is not a replacement for Band agent WebSockets; it is the judge-facing dashboard sync path.

## Why a Local Mirror Exists

The local mirror exists because the War Room needs a full, judge-readable view of the incident timeline. Band agents have scoped views based on @mentions. The optional Human API can read all room messages, but the local mirror guarantees the dashboard stays stable even when live credentials are missing or the Human API is not available.

## Files Added

```txt
apps/web/src/lib/band/
apps/web/src/app/api/collaboration/health/route.ts
apps/web/src/app/api/collaboration/stream/route.ts
scripts/band/
agents/common/sentinel_agent_runtime.py
agents/pyproject.toml
agents/agent_config.yaml.example
```

## Safety Rules

- Never put Band API keys in `NEXT_PUBLIC_*` variables.
- Keep Mock Mode working.
- Do not delete the local mirror.
- Do not make live Band credentials required for local development.
- Every production-impacting action stays behind an approval object.
- If Band posting fails, store a provider warning instead of crashing the demo.
