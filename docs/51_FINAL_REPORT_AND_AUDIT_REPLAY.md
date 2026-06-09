# Step 9 — Final Report and Audit Replay

## Purpose

Step 9 turns the Sentinel Relay output from a demo summary into a judge-readable incident report. The goal is not to pretend the product is a finished GRC platform. The goal is to prove the enterprise pattern clearly:

> Specialized agents coordinate through Band, preserve structured evidence, challenge unsupported claims, obtain human approval, and generate a traceable report from the same collaboration record.

The report page should be strong enough that a judge can open it after the War Room and understand the full case without hearing another explanation.

## What changed

The `/report` route now uses a dedicated report model and component system instead of rendering a few static cards. The final report is derived from the same canonical demo incident that powers the War Room.

The report now includes:

- Final report hero
- Report posture and metadata
- Report metrics
- Report sections with evidence and source-message IDs
- Integrity checks
- Human approval record
- Audit replay table
- Evidence matrix
- Remediation control plan
- Open questions and limitations
- Enterprise export checklist

## Judge-facing message

The report should communicate four things immediately:

1. **The system did not hallucinate a final answer.** It cites message IDs, evidence IDs, and decision records.
2. **The system did not let agents blindly agree.** Risk & Compliance challenged the customer-impact claim.
3. **The system did not take unsafe actions automatically.** Human approval separated containment from customer notification.
4. **Band is central.** The report is built from the collaboration timeline that agents created through the shared coordination layer.

## Important files

```txt
apps/web/src/app/report/page.tsx
apps/web/src/lib/report/auditReportModel.ts
apps/web/src/components/report/
scripts/report/verify-report-layer.py
```

## Report model

The report model builds these derived views:

- `ReportMetric[]`
- `AuditTrailRecord[]`
- `EvidenceMatrixRow[]`
- `RemediationReportRow[]`
- `ReportIntegrityCheck[]`
- `ApprovalNarrative`

This keeps the page simple and prevents component-level duplication.

## Audit replay

The audit replay table uses `finalReport.auditTrailMessageIds` to select ordered messages from the incident collaboration stream. Each row includes:

- Sequence number
- Message ID
- Timestamp
- Actor
- Action type
- Title
- Decision impact
- Evidence titles
- Target agents
- Trace ID

The key point is that the final report is not detached from the workflow. It is a structured view over the same agent-to-agent coordination records.

## Evidence matrix

The evidence matrix answers:

- Which evidence item is this?
- Where did it come from?
- What confidence is assigned?
- What report sections cite it?
- What agent messages cite it?
- What limitations are known?

This is important for Track 3 because regulated/high-stakes workflows need traceability and clear boundaries.

## Human approval record

The report separates:

- Approved containment scope
- Explicitly not-approved actions

This is not cosmetic. It proves the workflow understands that approval decisions are scoped. In the demo, token revocation and secret rotation are approved, but customer notification remains deferred pending scope verification.

## Remediation control plan

The remediation section links every task to:

- Owner
- Status
- Severity
- Evidence
- Acceptance criteria
- Test plan
- Rollback plan

This gives the report a practical engineering handoff instead of ending with a vague recommendation.

## Stability principle

The report must remain fully demoable in Mock Mode. Live Band integration can enrich the records later, but the final report must never depend on credentials being present during judging.
