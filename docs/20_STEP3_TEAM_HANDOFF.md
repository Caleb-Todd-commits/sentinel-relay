# Step 3 Team Handoff

## What the team can do now

The team can now start working from a stable frontend baseline instead of a blank project. The app has enough structure for frontend, Band integration, schemas, agents, and demo polish to move in parallel.

## Frontend lead next actions

1. Run the app locally.
2. Verify `/`, `/demo`, `/war-room`, `/report`, and `/status`.
3. Improve responsive spacing and visual polish only after confirming the baseline runs.
4. Do not replace the data contract unless the schema lead agrees.
5. Add small UI improvements behind the existing components.

Recommended files:

```txt
apps/web/src/app/war-room/page.tsx
apps/web/src/components/
apps/web/src/app/globals.css
```

## Schema/data lead next actions

1. Review `apps/web/src/lib/types.ts`.
2. Compare it against `packages/schemas/message-contract.md`.
3. Decide which fields must be shared with Python agents.
4. Create JSON Schema or Pydantic-compatible structures in Step 4.
5. Keep frontend and agent schemas aligned.

Recommended files:

```txt
apps/web/src/lib/types.ts
apps/web/src/lib/demo/sentinelRelayDemo.ts
packages/schemas/message-contract.md
```

## Band/backend lead next actions

1. Review the provider contract.
2. Confirm which methods map cleanly to Band API/SDK calls.
3. Do not break mock mode.
4. Add real Band integration behind `BandCollaborationProvider` later.
5. Plan how live messages will be normalized into `AgentMessage` objects.

Recommended files:

```txt
apps/web/src/lib/collaboration/CollaborationProvider.ts
apps/web/src/lib/collaboration/MockCollaborationProvider.ts
apps/web/src/lib/collaboration/BandCollaborationProvider.ts
```

## Agent lead next actions

1. Review the mock incident messages.
2. Convert each message into the expected output format for the relevant agent.
3. Make each agent output structured JSON, not loose prose.
4. Preserve the challenge moment where Risk & Compliance pushes back.
5. Avoid making the agents too autonomous around containment/customer notification.

Recommended files:

```txt
agents/*/prompt.md
apps/web/src/lib/demo/sentinelRelayDemo.ts
```

## Demo/pitch lead next actions

1. Walk through the UI as if presenting to judges.
2. Make sure the story is explainable in under 3 minutes.
3. Use `/war-room` as the main demo surface.
4. Use `/report` as the final proof artifact.
5. Keep the language focused on Band coordination.

Recommended files:

```txt
docs/demo-script.md
docs/03_JUDGE_PITCH_AND_POSITIONING.md
docs/15_NEXTJS_BASELINE_RUNNING.md
```

## What not to do immediately

- Do not add auth.
- Do not add a database yet.
- Do not add real external security tools.
- Do not create five different incident scenarios.
- Do not rewrite the UI around a different data shape without team agreement.

## The next official step

Step 4 is to formalize the shared data schemas across:

- frontend TypeScript
- Python agents
- sample data
- Band message payloads
- final report output
