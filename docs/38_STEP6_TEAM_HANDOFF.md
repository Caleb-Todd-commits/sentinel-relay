# Step 6 Team Handoff

## What teammates should know

The War Room is now the strongest visual surface in the project. Future work should protect this flow instead of replacing it.

## Where to start

Open:

```txt
apps/web/src/app/war-room/page.tsx
```

This file shows the full page layout and all major UI zones.

## Most important components

```txt
WarRoomCommandBar
JudgeBriefingPanel
WorkflowControls
CriticalMomentCard
CollaborationMap
MessageStream
ApprovalGate
AuditReplayPanel
EvidenceBoard
ReportPreview
```

## Rules for future UI changes

1. Do not bury the Risk challenge.
2. Do not remove the approval gate.
3. Do not make messages look like plain chat.
4. Do not add unrelated dashboard widgets.
5. Do not make the demo depend on random live AI behavior.
6. Keep the page understandable at a glance.
7. Keep mock mode working until Band mode is fully stable.

## Recommended next UI improvements

These are optional and should happen only after Step 7 begins:

- Add a room-mode switcher showing Mock Mode versus Band Mode.
- Add a small filter to the message stream by agent or message type.
- Add a focused “3-minute demo mode” route.
- Add report export/download later.
- Add a simple architecture diagram page.

## Next major project step

Step 7 is the Collaboration Provider Layer.

The UI is now ready for the provider abstraction to become the boundary between:

```txt
MockCollaborationProvider
BandCollaborationProvider
```

Do not connect Band directly into UI components. Keep the provider boundary clean.
