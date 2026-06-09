# Step 9 Verification Report

## Step completed

Step 9, **Build the Final Report and Audit Replay**, has been completed.

## Verification scope

This step verifies that the final report layer exists, uses the canonical demo incident, and preserves traceability back to messages, evidence, approvals, and remediation tasks.

## Static verification command

Run:

```bash
python scripts/report/verify-report-layer.py
```

Expected result:

```txt
Step 9 report layer verification passed.
Report sections: 5
Audit events: 10
Evidence items: 6
Remediation tasks: 4
```

## Checks included

The verification script checks:

- Report route exists
- Report model exists
- Report components exist
- Report docs exist
- Final report has enough sections
- Audit trail has enough messages
- Challenge message exists
- Approval decision message exists
- Evidence set is present
- Remediation task set is present

## Additional checks to run locally

After installing dependencies:

```bash
pnpm install
pnpm report:verify
pnpm schemas:validate
pnpm workflow:verify
pnpm provider:verify
pnpm typecheck
pnpm build
```

## Known limitation

The local environment used to build this package does not have the full Next.js dependency tree installed, so the package includes static verification and schema checks. The team should run the full `pnpm typecheck` and `pnpm build` locally after extracting the zip.

## Acceptance criteria

Step 9 is accepted when:

- `/report` renders the final report page.
- The audit trail table shows ordered message records.
- The evidence matrix maps evidence to report sections and messages.
- The approval record separates approved actions from deferred/not-approved actions.
- The remediation section includes evidence, test plans, and rollback plans.
- The report clearly communicates what is known, what is unresolved, and what decision was approved.
