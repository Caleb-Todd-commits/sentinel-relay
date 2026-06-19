# Sentinel Relay web application

This Next.js application serves the current Sentinel Relay workspace and its server-only integrations.

## Current routes

| Route | Purpose |
|---|---|
| `/` | Incident, Agents, Decision/Result, and custom-scenario workspace |
| `/api/agent_run` | Seeded investigation and approval NDJSON stream |
| `/api/custom-incident` | Open-ended multi-agent NDJSON stream |
| `/api/collaboration/*` | Preserved Band collaboration contracts |

Legacy routes (`/demo`, `/scenarios`, `/scenarios/room`, `/war-room`, `/report`, and `/status`) redirect into the workspace.

## Local development

From the repository root:

```bash
corepack pnpm install
corepack pnpm dev
```

Then open [http://localhost:3000](http://localhost:3000).

## Runtime behavior

- Seeded scenarios attempt live Band execution and use verified replay when the integration cannot complete.
- Open-ended incident descriptions use AI/ML API through a server route.
- Provider keys remain server-side.
- The UI never asks visitors to supply credentials.
- Remediation and final reporting remain blocked until explicit approval in the seeded workflow.

## Commands

```bash
corepack pnpm --filter sentinel-relay-web typecheck
corepack pnpm --filter sentinel-relay-web build
corepack pnpm verify
```

Do not add public environment variables containing Band, AI/ML API, or signing credentials.
