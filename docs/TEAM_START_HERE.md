# Team Start Here — Sentinel Relay

This is the first file every teammate should read.

Sentinel Relay is a **Band-powered multi-agent cybersecurity incident command center**. A company receives a suspicious security alert, and specialized agents coordinate through Band to investigate evidence, challenge weak conclusions, request human approval, create remediation tasks, and generate an audit-ready report.

---

## Current Locked Direction

- **Primary track:** Track 3 — Regulated & High-Stakes Workflows
- **Secondary influence:** Track 2 — Multi-Agent Software Development
- **Main scenario:** Possible API Key Exposure After Friday Deploy
- **Core demo surface:** War Room dashboard
- **Core technical proof:** Agents coordinate through Band using structured messages, handoffs, challenges, approvals, and audit trail events.

---

## Read These in Order

1. `docs/01_PROJECT_VISION_LOCK.md`
2. `docs/02_PROJECT_CHARTER.md`
3. `docs/03_JUDGE_PITCH_AND_POSITIONING.md`
4. `docs/04_PRODUCT_BOUNDARIES_AND_NON_GOALS.md`
5. `docs/05_TERMINOLOGY.md`
6. `docs/06_DECISION_LOG.md`
7. `docs/07_TEAM_ONBOARDING_CHECKLIST.md`
8. `docs/01_BIGGEST_10_FIRST.md`
9. `docs/56_TEAM_BRANCHING_BASELINE.md`

---

## Short Team Explanation

Sentinel Relay is a cybersecurity incident war room where multiple specialized agents coordinate through Band. The agents investigate logs, review code changes, assess threat indicators, challenge unsupported claims, request human approval, and generate a final audit-ready report.

The point is not just that agents talk. The point is that they coordinate serious enterprise work through Band.

---

## Main Demo Scenario

**Possible API Key Exposure After Friday Deploy**

A suspicious API token is used from an unusual region after a Friday deployment. The system must determine what happened, what evidence supports the claim, whether customer exposure is confirmed, what actions require approval, and what remediation steps should be taken.

---

## Agent Roles

1. **Incident Commander Agent** — opens the case, assigns tasks, coordinates the workflow, requests approval.
2. **Forensics Agent** — reviews logs and builds the timeline.
3. **Threat Intel Agent** — assesses suspicious indicators and confidence.
4. **Code Review Agent** — checks recent code/config changes for exposed secrets or unsafe changes.
5. **Risk & Compliance Agent** — applies policy, challenges unsupported claims, recommends escalation.
6. **Remediation Agent** — creates fix tasks, mock PR summary, and validation steps.

---

## Non-Negotiables

- Band must be central to the workflow.
- The UI must make agent coordination visible.
- The demo must include at least one agent challenge/disagreement.
- High-impact actions require human approval.
- The final report must be traceable to the agent workflow.
- Use safe sample data only.
- Do not commit secrets.
- One polished scenario beats many unfinished scenarios.

---

## First Build Target

Build a stable vertical slice:

1. Start sample incident.
2. Show War Room dashboard.
3. Display agent roster.
4. Simulate or receive Band messages.
5. Show evidence cards.
6. Show a challenge from Risk & Compliance.
7. Request human approval.
8. Show remediation tasks.
9. Generate final report.
10. Replay the audit trail.

---

## Team Rule

When deciding what to build, choose the option that makes the final demo more reliable, clearer, more Band-native, and easier for judges to understand.

## Current Baseline Progress

Completed so far:

1. Project vision locked.
2. GitHub repo and branch rules planned.
3. Next.js frontend baseline created.
4. Shared schemas defined.
5. Mock incident flow built.

The app now has a product-shaped frontend with `/`, `/demo`, `/war-room`, `/report`, and `/status`. The War Room now runs a deterministic 10-step incident workflow with evidence unlocks, agent handoffs, a Risk challenge, a human approval gate, remediation task unlocks, and final report readiness.

Run from the repo root:

```bash
corepack pnpm install
corepack pnpm dev
```

Open:

```txt
http://localhost:3000
```

Useful verification commands:

```bash
corepack pnpm schemas:validate
corepack pnpm schemas:typecheck
corepack pnpm workflow:verify
corepack pnpm typecheck
corepack pnpm build
corepack pnpm verify
```

## Step 5 Update — Mock Incident Flow Baseline

The mock workflow now lives in:

```txt
apps/web/src/lib/workflow/
```

Important rule going forward:

> Mock Mode is not disposable. It is the fallback demo path and the contract the real Band integration should satisfy.

Do not remove the challenge message, approval request, approval decision, remediation unlock, or final report unlock. Those are the main proof that this is a high-stakes, traceable, multi-agent workflow.

The next major task is Step 6: polish the War Room UI so the demo is visually stronger and easier for judges to understand in under three minutes.


## Step 6 Update — War Room UI Is Now the Main Demo Surface

The War Room has been upgraded into the main judge-facing command center. It now includes:

- command summary,
- judge briefing panel,
- workflow progress controls,
- critical challenge/approval spotlight,
- collaboration map,
- structured Band-style message stream,
- approval gate,
- evidence board,
- decision board,
- remediation list,
- audit replay trail,
- report preview.

Future work should not replace this page unless there is a major reason. Step 7 should connect the collaboration provider layer behind the existing UI.

## Step 7 Update — Collaboration Provider Layer

The War Room now runs through a provider abstraction.

Default mode is still Mock Mode, but it is no longer just a static UI mock. The staged workflow is pushed through `MockCollaborationProvider`, which creates an incident room, registers agents, stores structured messages, records approvals, tracks task statuses, and exposes provider audit events.

Band Mode is scaffolded behind server-side API routes:

```txt
/api/collaboration/rooms
/api/collaboration/messages
/api/collaboration/approvals
```

Do not put Band secrets in browser code. Step 8 should connect these server routes to the real Band SDK/API.

New War Room hook:

```ts
useIncidentCollaborationWorkflow()
```

Do not build new War Room features against direct mock arrays. Build against the workflow/provider state.


## Step 8 Live Band Notes

Read these before testing live mode:

```txt
docs/45_REAL_BAND_INTEGRATION.md
docs/46_BAND_ENVIRONMENT_SETUP.md
docs/47_REMOTE_AGENT_RUNBOOK.md
docs/48_BAND_ROUTE_CONTRACTS.md
```

Useful commands:

```bash
corepack pnpm band:verify
corepack pnpm band:env
corepack pnpm band:smoke
```

Live Band Mode requires:

- `NEXT_PUBLIC_COLLABORATION_MODE="band"`
- `NEXT_PUBLIC_ENABLE_BAND_MODE="true"`
- `BAND_PROVIDER_ENABLED="true"`
- `BAND_COMMANDER_AGENT_API_KEY`
- specialist participant IDs for routed @mentioned messages

Keep the app in Mock Mode when preparing the final backup demo.

## Step 9 Update — Final Report and Audit Replay

The final report is now an enterprise-style audit artifact. It is not just a paragraph summary. It includes evidence traceability, audit replay, human approval scope, remediation control plan, open questions, and integrity checks.

For demo purposes, after showing the War Room, open `/report` and explain that the final report is built from the same collaboration stream instead of being a black-box summary.

Key files:

```txt
apps/web/src/app/report/page.tsx
apps/web/src/lib/report/auditReportModel.ts
apps/web/src/components/report/
docs/51_FINAL_REPORT_AND_AUDIT_REPLAY.md
```
