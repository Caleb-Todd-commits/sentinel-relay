# 06 — Decision Log

This file records major product and architecture decisions so the team does not keep reopening settled questions.

---

## Decision 001 — Primary Track

**Decision:** Sentinel Relay will target Track 3: Regulated & High-Stakes Workflows.

**Reason:** Cybersecurity incident response naturally requires review, traceability, escalation, and careful decision-making.

**Secondary benefit:** The project can still include Track 2 qualities through code review and remediation agents.

---

## Decision 002 — Main Scenario

**Decision:** The primary demo scenario is “Possible API Key Exposure After Friday Deploy.”

**Reason:** It is easy to understand, technically credible, high-stakes, and allows multiple agent roles to contribute.

**Rejected alternative:** Multiple incident scenarios.

**Reason rejected:** Multiple scenarios increase scope and reduce polish.

---

## Decision 003 — Build One Polished Vertical Slice First

**Decision:** Build one complete flow before adding extra features.

**Reason:** A polished, stable demo is more valuable than broad but unfinished functionality.

---

## Decision 004 — Use Mock Mode First

**Decision:** Build a working mock collaboration flow before full Band integration.

**Reason:** This keeps the project demoable and lets frontend, schemas, and report generation stabilize early.

**Important:** Mock Mode is not the final product. It is a safety layer and development accelerator.

---

## Decision 005 — Band Must Be Central

**Decision:** Band must handle collaboration during the workflow, not only final notifications.

**Reason:** The hackathon challenge is specifically about cross-agent collaboration through Band.

---

## Decision 006 — Use Structured Messages

**Decision:** Agent outputs should use structured message types instead of generic paragraphs.

**Reason:** Structured messages make evidence, handoffs, approval, and audit replay possible.

---

## Decision 007 — Human Approval Required

**Decision:** High-impact actions require human approval.

**Reason:** This strengthens the Track 3 story and makes the system feel safe and enterprise-ready.

---

## Decision 008 — No Real Sensitive Data

**Decision:** The demo uses fake sample data only.

**Reason:** Safety, reliability, and ease of public submission.

---

## Decision 009 — Frontend Is Judge-Facing

**Decision:** The War Room UI is a primary product surface, not a debug tool.

**Reason:** Judges need to understand the system quickly. Visual clarity matters.

---

## Decision 010 — Avoid Full Auth and Complex Infrastructure First

**Decision:** Do not build full authentication, multi-tenant support, or enterprise database architecture in the first version.

**Reason:** These are not central to the Band collaboration proof and can consume too much time.
## Decision 014 — Step 3 frontend baseline completed

Status: Accepted

Decision: The project now uses a stable mock-first Next.js baseline with route pages for `/`, `/demo`, `/war-room`, `/report`, and `/status`. The frontend renders a structured incident flow from local TypeScript demo data instead of requiring live Band credentials.

Rationale: This protects demo reliability while giving the team a real product surface to build on. Real Band integration should later satisfy the existing message/provider contract rather than force a UI rewrite.

Implication: Mock Mode is a required reliability layer, not temporary junk code. The War Room must remain demoable even while live Band work is under development.



## Decision 006 — War Room becomes the primary judging surface

**Status:** Accepted

**Decision:** The War Room UI is now the core product surface for judges. It must show the incident state, specialized agent roles, structured Band-style messages, handoffs, challenges, approval gates, evidence, remediation, and audit trail in one coherent command center.

**Reason:** A technically good multi-agent project can still lose if judges cannot understand the coordination quickly. The War Room now explains the project visually and makes the Band coordination proof visible without requiring code inspection.

**Consequences:** Future work should preserve the War Room layout and connect real Band communication through the provider layer instead of replacing UI components directly.

## Decision 007 — Provider-backed collaboration boundary

**Date:** 2026-06-07  
**Status:** Accepted  
**Step:** 7 — Add the Collaboration Provider Layer

### Decision

The War Room will consume collaboration events through a formal `CollaborationProvider` interface rather than reading only from local mock arrays.

### Rationale

Sentinel Relay must eventually prove real Band coordination. Adding the provider boundary before live Band integration prevents a late-stage rewrite and keeps the UI stable.

### Implementation

- `MockCollaborationProvider` is the default runtime.
- `BandCollaborationProvider` is scaffolded behind server-side API routes.
- The browser never receives Band secrets.
- `useIncidentCollaborationWorkflow` replaces direct use of the old mock workflow hook in the War Room.
- `ProviderStatusPanel` makes provider mode, sync state, registered agents, and audit events visible.

### Consequence

The app remains demoable without external services, while Step 8 has a specific integration seam for live Band rooms/messages.

---

## Decision 008 — Live Band communication stays server-side and opt-in

**Date:** 2026-06-07  
**Status:** Accepted  
**Step:** 8 — Connect Real Band Agent Communication

### Decision

Live Band communication is implemented behind server-side Next.js API routes. The browser never holds Band API keys. Mock Mode remains the default mode, while Band Mode is enabled only with explicit environment values.

### Rationale

Band uses API keys for Agent/Human API access. Those keys must not be exposed through client-side code. A server-side adapter also gives us a stable local mirror for the War Room, which protects the judge demo if live Band credentials, Human API access, or remote agents are not available.

### Implementation

- `apps/web/src/lib/band/` contains the Band runtime config, REST client, mappers, local room store, and route response helpers.
- `/api/collaboration/rooms` creates Band chats and registers participants.
- `/api/collaboration/messages` posts Sentinel Relay messages as structured Band events and routed text messages when target mentions are configured.
- `/api/collaboration/approvals` posts approval requests and decisions as structured events.
- `/api/collaboration/health` exposes safe configuration and optional live identity checks.
- `/api/collaboration/stream` streams the local room mirror to the War Room dashboard.
- `agents/*/main.py` now contains remote agent worker entrypoints based on the Band/Thenvoi SDK pattern.

### Consequence

The project now has a realistic live Band path without sacrificing reliability. The final demo can use Mock Mode, Band dry-run mode, or live Band Mode depending on credential readiness.


---

## Decision 009 — Final report derives from structured collaboration records

**Date:** 2026-06-07  
**Status:** Accepted  
**Step:** 9 — Build the Final Report and Audit Replay

### Decision

The final report page will be generated from the canonical incident record, including agent messages, evidence references, approval decisions, remediation tasks, and final report section metadata.

### Rationale

A high-stakes workflow project should not end with an ungrounded AI summary. The report must show how conclusions were reached, what evidence was used, where the risk challenge happened, which human decision was approved, and what actions remain outside the approved scope.

### Implementation

- `apps/web/src/lib/report/auditReportModel.ts` derives report metrics, audit trail rows, evidence matrix rows, remediation rows, integrity checks, approval narrative, limitations, and export checklist.
- `/report` renders a dedicated report experience using focused report components.
- `scripts/report/verify-report-layer.py` verifies that required files exist and that the sample incident includes audit events, report sections, a challenge message, approval decision, evidence, and remediation tasks.

### Consequence

The project now has a stronger Track 3 proof: the workflow is traceable, approval-scoped, evidence-backed, and judge-readable even in Mock Mode.
