# 24 — Sample Data and Report Schema

The sample data is the demo's safety net. Even when live APIs are not ready, the project should still show the full product shape.

## Canonical sample incident

The canonical sample incident is:

```txt
packages/sample-data/demo_incident.json
```

It is mirrored in:

```txt
packages/schemas/examples/demo_incident.json
apps/web/src/lib/demo/sentinelRelayDemo.ts
```

## Why include JSON sample data

The TypeScript demo file is convenient for the Next.js app. The JSON file is useful for:

- Python agents,
- validation scripts,
- future Band seeding,
- tests,
- docs,
- replay mode.

## Required demo data objects

The demo incident includes:

- `case`
- `state`
- `agents`
- `messages`
- `evidence`
- `timeline`
- `approvalRequest`
- `approvalDecision`
- `remediationTasks`
- `finalReport`

## Report schema expectations

The final report should not be a detached AI summary. It must point back to the workflow.

Required linkage:

- `sections[].evidenceIds`
- `sections[].sourceMessageIds`
- `auditTrailMessageIds`

This allows the UI to explain where each report conclusion came from.

## The report should answer

1. What happened?
2. What evidence supports that?
3. What evidence is weak or incomplete?
4. Which agent challenged the conclusion?
5. What did the human approve?
6. What was explicitly not approved?
7. What remediation tasks were created?
8. What questions remain open?

## Why this matters for judging

The final report is where Sentinel Relay proves enterprise readiness. It shows that Band coordination produced a traceable decision path instead of a one-shot AI answer.
