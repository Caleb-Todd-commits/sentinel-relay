# 21 — Shared Schema System

Step 4 is complete when Sentinel Relay has one shared language across the frontend, agents, Band messages, sample data, and report generation.

The purpose of this step is not only to create TypeScript types. It is to prevent the project from becoming five separate systems that accidentally call the same fields different names.

## What is now canonical

The canonical schema package is:

```txt
packages/schemas/
```

This package contains:

```txt
src/                  TypeScript contracts
json-schema/          JSON Schema files for payload validation
python/               Pydantic-style models for agents
examples/             Valid example payloads
contracts/            Human-readable contract docs
```

The web app keeps its existing import path:

```ts
import type { AgentMessage } from "@/lib/types";
```

But `apps/web/src/lib/types.ts` now re-exports the canonical package:

```ts
export type { AgentMessage } from "@sentinel-relay/schemas";
```

That gives the frontend stability while making `packages/schemas` the source of truth.

## Why this matters

Sentinel Relay is trying to prove a multi-agent enterprise workflow. That only works if every agent agrees on the shape of shared context.

Without this step, the project risks these problems:

- the Forensics Agent sends `evidence` while the UI expects `evidenceIds`,
- the Risk Agent writes `confidence_score` while the report generator expects `confidence`,
- the Band provider sends unstructured text that cannot be replayed,
- the final report becomes disconnected from the actual agent decisions,
- the demo looks like a chatbot transcript instead of an audit-ready workflow.

The schema package prevents that.

## Core data objects

### IncidentCase

Represents the active security incident.

Used by:

- War Room header
- Band room creation
- state updates
- final report

Critical fields:

- `id`
- `roomId`
- `title`
- `severity`
- `status`
- `phase`
- `decisionGate`

### AgentProfile

Represents a participant in the incident room.

Used by:

- agent roster UI
- Band registration
- assignment routing
- audit report

Important fields:

- `id`
- `name`
- `kind`
- `capability`
- `status`
- `allowedDecisions`
- `requiresHumanApprovalFor`

### AgentMessage

The most important schema in the project.

Every meaningful collaboration event should become an `AgentMessage`.

Used by:

- Band payloads
- message stream UI
- replay mode
- audit trail
- report source linkage

Critical fields:

- `type`
- `summary`
- `confidence`
- `severity`
- `evidenceIds`
- `decisionImpact`
- `nextAction`
- `payload`

### EvidenceReference

Represents the evidence an agent used to support or challenge a claim.

Used by:

- evidence board
- findings
- challenges
- final report

Critical fields:

- `id`
- `kind`
- `source`
- `summary`
- `location`
- `excerpt`
- `confidence`
- `limitations`

### ApprovalRequest and ApprovalDecision

These represent the human-in-the-loop part of the workflow.

They prove that the system does not blindly automate high-impact security actions.

Critical rule:

> Agents can recommend high-impact actions. Only a human approval message can approve them.

### RemediationTask

Represents a fix or containment task.

Used by:

- remediation panel
- mock PR story
- final report

Critical fields:

- `title`
- `ownerAgentId`
- `status`
- `acceptanceCriteria`
- `rollbackPlan`
- `testPlan`

### FinalReport

The final report is an audit artifact, not just a summary.

It must reference:

- evidence IDs,
- source message IDs,
- audit trail message IDs.

## Schema design principles

### 1. Stable IDs over fuzzy references

Agents should pass IDs, not vague phrases.

Good:

```json
"evidenceIds": ["ev-code-diff"]
```

Weak:

```json
"evidence": "the code diff thing"
```

### 2. Confidence must be explicit

Every meaningful agent message has:

```json
"confidence": 0.84
```

This helps the Risk Agent challenge unsupported claims.

### 3. Limitations must be visible

Evidence can be strong but still incomplete. The schema supports `limitations` so the system can say:

- token exposure is likely,
- customer impact is not fully verified,
- IP reputation alone is not enough.

This is one of the strongest parts of the demo.

### 4. Human approval is separate from agent recommendation

An agent can request approval, but cannot approve its own high-impact action.

### 5. Reports should link back to messages and evidence

The report must prove where its conclusions came from.

## Validation levels

The project now has three validation levels.

### Level 1 — Lightweight stdlib validation

```bash
pnpm schemas:validate
```

This runs:

```bash
python scripts/schema/validate-sample-data.py
```

It does not require Python dependencies.

### Level 2 — TypeScript type checking

```bash
pnpm schemas:typecheck
```

This checks the schema package TypeScript types.

### Level 3 — Python agent model validation

The Pydantic models in `packages/schemas/python` are prepared for agent-side validation once Python dependencies are installed.

## Current schema version

```txt
0.4.0
```

The version is stored in:

```txt
packages/schemas/src/enums.ts
```

## Step 4 completion definition

Step 4 is complete because the project now has:

- canonical TypeScript schema exports,
- JSON Schema files,
- Python model contracts,
- Band envelope contract,
- sample demo JSON,
- validation scripts,
- updated frontend imports,
- documentation for agent outputs and report traceability.
