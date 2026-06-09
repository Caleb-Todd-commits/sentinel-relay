# Remediation Agent

## Role

Creates containment/fix checklist, acceptance criteria, tests, and rollback plan after approval.

## Capability

```txt
remediation
```

## Output Contract

This agent must output `AgentMessage` objects from the shared schema package.

Canonical schema files:

```txt
packages/schemas/src/messages.ts
packages/schemas/contracts/AGENT_OUTPUT_CONTRACT.md
packages/schemas/contracts/BAND_MESSAGE_CONTRACT.md
```

## Current Status

Placeholder agent folder. Connect to Band after the mock workflow and collaboration provider are stable.

## Files

- `main.py` — agent entrypoint placeholder
- `prompt.md` — role and structured output prompt
- `.env.example` — local environment template

## First Implementation Goal

Return a valid structured message for the sample incident in `packages/sample-data/demo_incident.json`.
