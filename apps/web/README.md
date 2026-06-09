# Sentinel Relay Web App

This is the judge-facing dashboard for Sentinel Relay.

## What should run now

The web app should run as a fully mocked baseline with these routes:

- `/` — product landing page
- `/demo` — sample incident setup
- `/war-room` — main demo surface
- `/report` — final audit report
- `/status` — local readiness page

## Local commands

From the repository root:

```bash
pnpm install
pnpm dev
```

From this folder:

```bash
pnpm install
pnpm dev
```

## Baseline rules

- Keep the app demoable at all times.
- Do not require Band credentials to load the UI.
- Do not commit real secrets.
- Use `src/lib/types.ts` as the shared contract for the UI.
- Use `src/lib/demo/sentinelRelayDemo.ts` as the canonical demo data.
- Use `src/lib/workflow/` as the canonical mock flow engine.
- Keep the Risk challenge and human approval gate visible.
- Do not let remediation appear before approval.

## Mock workflow files

```txt
src/lib/workflow/mockWorkflowScript.ts
src/lib/workflow/deriveWorkflowState.ts
src/lib/workflow/useMockIncidentWorkflow.ts
src/components/war-room/WorkflowControls.tsx
src/components/war-room/StateMachinePanel.tsx
src/components/war-room/HandoffPanel.tsx
src/components/war-room/DecisionPanel.tsx
```

## When adding real Band

The real Band provider should satisfy the same message contract used by the mock data and workflow view model. The UI should not need a major rewrite when live messages are connected. Mock Mode should remain available as the fallback demo path.
