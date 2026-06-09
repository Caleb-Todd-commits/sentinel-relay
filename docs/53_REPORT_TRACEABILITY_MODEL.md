# Report Traceability Model

## Why this exists

In a normal AI app, the final report can become an ungrounded summary. Sentinel Relay should avoid that. The final report must be a structured view over the collaboration record.

## Canonical inputs

The report is derived from the canonical demo incident:

```txt
sentinelRelayDemo
```

The important fields are:

- `case`
- `agents`
- `messages`
- `evidence`
- `timeline`
- `approvalDecision`
- `remediationTasks`
- `finalReport`

## Report provenance

Each report section contains:

```txt
evidenceIds
sourceMessageIds
```

The report model verifies that these IDs resolve against known evidence and messages.

## Audit trail construction

The audit trail is built from:

```txt
finalReport.auditTrailMessageIds
```

Those IDs are looked up in the message stream, sorted by sequence, and rendered as `AuditTrailRecord` rows.

Each row includes:

- Event sequence
- Actor
- Action type
- Decision impact
- Evidence titles
- Target agents
- Trace ID

## Evidence usage

The evidence matrix cross-links each evidence item to:

- Report sections that cite it
- Agent messages that cite it
- Known limitations

This helps reviewers see whether conclusions are backed by relevant evidence.

## Approval scope

The approval record is intentionally scoped:

- Approved containment actions
- Explicitly not-approved customer/external notification actions

A major demo point is that approval is not treated as blanket permission.

## Integrity checks

The report model produces checks for:

1. Evidence references resolving
2. Audit messages resolving
3. Agent challenge being recorded
4. Human approval being recorded
5. Report-generation event being recorded

Any missing record should be treated as a product issue, not hidden from the judge.

## Future production expansion

In a live deployment, this model can expand to include:

- Signed event hashes
- Band room IDs
- Participant IDs
- Raw artifact storage references
- Exported PDF/JSON package
- Legal/comms review status
- Closure approval

For the hackathon baseline, the current model is deliberately lightweight and demo-reliable.
