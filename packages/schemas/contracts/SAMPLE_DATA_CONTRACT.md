# Sample Data Contract

The canonical demo incident is stored in:

```txt
packages/sample-data/demo_incident.json
```

That file should stay in sync with:

```txt
apps/web/src/lib/demo/sentinelRelayDemo.ts
packages/schemas/examples/demo_incident.json
```

## Required demo proof points

The sample incident must include:

1. At least three AI agents.
2. A Commander agent.
3. A Forensics agent.
4. A Risk & Compliance agent.
5. At least one `finding` message.
6. At least one `challenge` message.
7. At least one `approval_request` message.
8. At least one `approval_decision` message.
9. At least one `remediation_task` message.
10. A final report with audit trail message IDs.

If any of these are missing, the demo no longer proves the hackathon thesis.
