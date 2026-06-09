# 27 — Step 4 Team Handoff

## What changed

The project now has a real shared schema system.

This means teammates should stop inventing field names independently. If the frontend, agents, Band payloads, or reports need a shared object, it should be added to `packages/schemas` first.

## For the frontend lead

Continue importing from:

```ts
import type { AgentMessage } from "@/lib/types";
```

That path now points to the canonical schemas.

Important UI fields:

- `message.type`
- `message.confidence`
- `message.evidenceIds`
- `message.decisionImpact`
- `message.nextAction`
- `approvalDecision.explicitlyNotApproved`
- `finalReport.auditTrailMessageIds`

## For the Band/backend lead

Use `BandEnvelope` as the intended real Band payload wrapper.

Every Band message should carry:

- case ID,
- room ID,
- sender agent ID,
- message ID,
- trace ID,
- AgentMessage payload.

Do not send unstructured text only.

## For the agent logic lead

Every agent should output an `AgentMessage`.

A finding should include:

- claim,
- evidence IDs,
- confidence,
- limitations,
- requested verification.

A challenge should include:

- challenged message ID,
- reason,
- required next step,
- whether it blocks a decision.

A remediation task should include:

- acceptance criteria,
- rollback plan,
- test plan.

## For the demo/data/docs lead

The canonical sample incident is:

```txt
packages/sample-data/demo_incident.json
```

The validation command is:

```bash
pnpm schemas:validate
```

Do not remove the challenge or human approval messages. Those are core proof points.

## Next build step

Step 5 is:

```txt
Build the mock incident flow.
```

Now that the schemas are stable, Step 5 should turn the War Room from a static full-state page into a properly staged replayable workflow driven by structured messages and state transitions.
