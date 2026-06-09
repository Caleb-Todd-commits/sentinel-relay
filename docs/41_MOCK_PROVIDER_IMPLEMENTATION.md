# Mock Provider Implementation

## Why Mock Mode Still Matters

Mock Mode is not a shortcut. It is the controlled demonstration path.

A week-long hackathon demo needs a reliable fallback because live APIs, credentials, agent runtimes, and network calls can fail. Mock Mode lets the team present the full product story even if the live Band adapter has issues.

## What Mock Mode Does

`MockCollaborationProvider` supports:

- deterministic room creation
- duplicate-safe agent registration
- duplicate-safe message insertion
- message sorting by sequence/time/id
- approval request storage
- approval decision storage
- task status storage
- message subscribers
- room snapshot subscribers
- audit event generation
- room reset for replay
- snapshot hydration for future testing

## Current War Room Flow

The War Room uses `useIncidentCollaborationWorkflow`.

That hook:

1. gets the active provider
2. creates a room for `INC-1042`
3. registers all demo agents
4. syncs the current workflow step into the provider
5. reads provider messages back into the UI
6. exposes provider health/snapshot/audit metadata

## Why Messages Are Replayed On Step Change

The current demo is deterministic. Every step should represent a clean state, not accumulated leftovers from a prior run.

So each step sync does:

```txt
reset room
send all visible messages for the current step
record approval request if visible
record approval decision if visible
record visible remediation task statuses
read final room snapshot
```

This creates a stable replay path.

## Audit Events

The mock provider creates audit events for:

- room creation
- agent registration
- message sent
- task status updated
- approval requested
- approval decision submitted
- room reset
- room hydrated

These events help demonstrate the future Band audit story.

## Known Limits

Mock Mode is in-memory only.

It does not:

- persist across refreshes
- communicate with external agents
- prove live Band connectivity
- run autonomous LLM agents

Those belong to later steps.
