# Report UI Components

## Overview

Step 9 adds a focused report component set under:

```txt
apps/web/src/components/report/
```

The goal is to keep `/report/page.tsx` readable while making each part of the final report independently improvable.

## Components

### `ReportHero`

Displays:

- Case ID
- Affected system
- Audit-ready status
- Final report title
- Executive summary
- Generated timestamp
- Severity
- Human approval posture

This is the top of the judge-facing report.

### `ReportMetricsGrid`

Displays compact operational metrics:

- Audit event count
- Evidence coverage
- Integrity checks
- Challenge control
- Remediation state
- Severity

This gives judges a fast read before they scan the details.

### `ReportSectionCard`

Displays one final report section with:

- Section type
- Title
- Content
- Evidence IDs
- Source message IDs

This reinforces that every section has structured provenance.

### `ReportIntegrityPanel`

Shows whether the report references resolve correctly:

- Evidence references resolve
- Audit messages resolve
- Challenge recorded
- Human approval recorded
- Report-generation event recorded

This is the anti-hallucination proof for the final output.

### `ApprovalDecisionRecord`

Shows:

- Decision
- Decision maker
- Timestamp
- Rationale
- Approved scope
- Explicitly not-approved scope

This is the high-stakes workflow proof.

### `AuditTrailTable`

Shows ordered audit events built from the collaboration stream. This table is intentionally more formal than the War Room stream because the report page should feel like a compliance artifact.

### `EvidenceMatrix`

Shows how evidence is used across sections and messages. This matters because the project should not simply state conclusions; it should show the path from evidence to decision.

### `RemediationReportCard`

Shows remediation tasks with owner, status, evidence, acceptance criteria, tests, and rollback plan.

### `OpenQuestionsCard`

Shows what is unresolved. This keeps the report honest and improves trust.

### `ReportExportPanel`

Shows what a production export would need before being used as a real incident artifact.

## Component design rules

1. Components should not directly import demo data.
2. Components receive already-derived model data.
3. Components should be readable without knowing Band internals.
4. Components should emphasize traceability, scope, and approval.
5. Components must remain static-render friendly.
