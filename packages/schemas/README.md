# Sentinel Relay Schemas

This package is the canonical schema contract for Sentinel Relay.

It defines the shared vocabulary used by:

- the Next.js war room frontend,
- Python agents,
- Band message payloads,
- sample incident files,
- final report generation,
- validation scripts,
- demo replay data.

The goal is simple: every agent, UI component, and report generator should agree on what an incident, finding, challenge, approval, remediation task, and report section mean.

## Rule

If a value crosses a boundary between agents, Band, the frontend, sample data, or report generation, it should be represented here.

## Folder map

```txt
packages/schemas/
  src/                  TypeScript schema types and guards
  json-schema/          JSON Schema contracts for payload validation
  python/               Pydantic-compatible Python models
  examples/             Valid example payloads
  contracts/            Human-readable schema contracts
```

## Contract stability

These schemas are intentionally conservative. Add fields when useful, but avoid casual renames. Renaming fields during the hackathon will break agent handoffs and demo stability.
