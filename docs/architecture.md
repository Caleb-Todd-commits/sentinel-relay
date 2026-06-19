# Architecture

## Deployed system

```text
Browser workspace
├── Seeded scenario flow ──> POST /api/agent_run
│   ├── live Band room and remote-agent messages
│   └── verified evidence replay when live execution degrades
└── Open-ended problem ───> POST /api/custom-incident
    └── server-side AI/ML API calls across six specialist roles

Shared foundations
├── AgentMessage and report schemas
├── synthetic evidence packets for INC-1042 and INC-1043
├── Band collaboration adapters and routes
└── Python evidence-driven agents and verification runners
```

## Browser workspace

The root page renders three primary panels:

- **Incident** selects a seeded scenario and exposes progress and execution mode.
- **Agents** shows the roster and expands the currently active contribution.
- **Decision / Result** shows the unresolved risk, approval gate, and final Summary/Evidence/Audit tabs.

The open-ended scenario section sits below those panels and reuses the same specialist roles without adding modal or popup surfaces.

## Seeded scenario path

`POST /api/agent_run` accepts an investigation start or approval continuation and streams NDJSON. The server attempts Band-backed execution first. If no live workflow completes, it emits a verified replay from evidence-backed scenario transcripts. The client exposes the resulting mode instead of hiding integration degradation.

The seeded flow has 14 pre-approval events and four post-approval events. Remediation and final reporting cannot appear before the human approval action.

## Open-ended path

`POST /api/custom-incident` accepts a sanitized description of up to 2,000 characters and streams agent-thinking, response, skip, clarification, completion, or error events.

The Band Leader frames the incident first. Forensics, Code Review, and Threat Intel run from the same framing. Risk & Compliance and Remediation then receive the accumulated findings so they can challenge or act on shared context rather than repeat it.

This route uses server-side AI/ML API credentials. It is a model-orchestration path and does not claim to create a Band room.
The route bounds request bodies, limits descriptions to 2,000 characters, and applies a best-effort six-requests-per-minute application cap per forwarded IP.

## Preserved components

- `agents/` contains the evidence-driven Python implementations.
- `data/incidents/` contains synthetic incident packets.
- `packages/schemas/` defines shared contracts.
- `/api/collaboration/*` preserves Band collaboration APIs.
- `.env.example` documents server-side configuration.

## Safety boundaries

- No visitor credentials.
- No destructive production actions.
- Synthetic seeded evidence only.
- Human approval before seeded high-impact remediation.
- Public custom descriptions must contain no real sensitive data.
