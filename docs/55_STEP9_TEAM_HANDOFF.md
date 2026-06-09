# Step 9 Team Handoff

## What changed

The final report is now much stronger and more judge-ready. It is no longer just a basic summary page. It now behaves like an audit artifact generated from structured collaboration records.

## Files to review first

```txt
apps/web/src/app/report/page.tsx
apps/web/src/lib/report/auditReportModel.ts
apps/web/src/components/report/
docs/51_FINAL_REPORT_AND_AUDIT_REPLAY.md
```

## What frontend should check

- `/report` layout at desktop width
- `/report` layout at mobile width
- Button links back to `/war-room` and `/demo`
- Report cards do not feel too dense
- Audit trail table remains readable
- Evidence matrix cards wrap correctly

## What agent/Band team should check

- The final report expects message IDs to remain stable.
- The report expects evidence IDs to remain stable.
- Real Band messages should preserve correlation/trace IDs when possible.
- Report generation should eventually use the same IDs that flow through Band.

## What demo/story team should emphasize

The report proves three key points:

1. Agents coordinated through a shared record.
2. Risk challenged an unsupported conclusion.
3. Human approval scoped what could and could not happen.

## Demo script addition

After showing the War Room, say:

> “Now the important part is that this does not disappear into a black-box summary. The final report is built from the same collaboration stream. Every section maps back to evidence IDs and message IDs, so leadership can see not just what the agents concluded, but how they got there.”

Then open `/report` and show:

- Metrics
- Integrity checks
- Human approval record
- Audit replay table
- Evidence matrix

## Next step

Step 10 is final polish and submission packaging.

That should include:

- README judge polish
- Architecture diagram
- Final demo script
- Submission description
- Cover image plan
- Video script
- Final verification checklist
- Backup demo instructions
