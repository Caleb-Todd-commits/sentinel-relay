# Sentinel Relay

**Sentinel Relay** is a Band-powered multi-agent cybersecurity incident command center for the lablab Band hackathon.

The project demonstrates a high-stakes enterprise workflow where specialized agents coordinate through Band to investigate evidence, challenge weak conclusions, request human approval, create remediation tasks, and generate an audit-ready final report.

## Current Build Status

Completed baseline steps:

1. **Project vision locked** — full product charter, judge positioning, non-goals, terminology, and coding-agent context.
2. **GitHub repo rules planned** — branch strategy, issue templates, PR template, CODEOWNERS, quality gates, and first sprint board.
3. **Next.js baseline running** — product-shaped frontend with landing, demo, War Room, report, status page, typed mock data, and provider scaffolding.
4. **Shared schemas defined** — canonical TypeScript, JSON Schema, Python-style models, Band envelopes, and validation contracts.
5. **Mock incident flow built** — staged War Room workflow with evidence unlocks, agent handoffs, Risk challenge, human approval gate, remediation tasks, and report unlock.
6. **War Room UI built** — judge-facing dashboard with command bar, briefing panel, critical moment spotlight, collaboration map, evidence board, audit replay rail, and report preview.
7. **Collaboration provider layer added** — Mock and Band providers share a stable provider contract, with server-side route scaffolds protecting secrets.
8. **Real Band communication layer connected** — server-side Band REST adapter, room/message/approval routes, local dashboard mirror, SSE stream, Band health/smoke scripts, and Python remote agent scaffolds.
9. **Final report and audit replay built** — enterprise-style report page, audit replay table, evidence matrix, approval record, remediation control plan, integrity checks, and report verification script.
10. **Evidence-driven AI/ML API workflow added** — realistic incident evidence packet, Band-posted specialist findings, AI/ML API policy gate, AI/ML API Band Leader synthesis, and static evidence verification.

Current mode:

```txt
Mock Mode first, Band Mode opt-in, stable provider architecture.
```

The app is intentionally runnable without Band credentials so the team always has a stable demo surface. Live Band Mode is now wired behind server-side API routes and remains opt-in until credentials, participants, and remote agent workers are configured.

Prize-path live rehearsal:

```bash
corepack pnpm workflow:evidence:live
```

Run this after starting the app with the root `.env` loaded. It posts an evidence-driven multi-agent workflow through the Band app routes and requires AI/ML API to perform the policy gate and Band Leader synthesis.

## Primary Track

**Track 3: Regulated & High-Stakes Workflows**

Secondary angle:

**Track 2 influence** through code review and remediation agents.

## Core Demo Scenario

**Possible API Key Exposure After Friday Deploy**

A SaaS company detects suspicious API activity shortly after a Friday deployment. Agents investigate whether an API token was exposed, whether customer data may have been accessed, what actions require human approval, and what remediation should happen next.

## Agent Team

- Band Leader
- Forensics Agent
- Threat Intel Agent
- Code Review Agent
- Risk & Compliance Agent
- Remediation Agent
- Human Security Lead approval gate

## Why Band Matters

Band is intended to be the actual coordination layer, not a final notification channel.

The workflow is designed around:

- Shared incident room
- Structured agent messages
- Evidence handoffs
- Agent-to-agent challenges
- Human approval request and decision
- Remediation task handoff
- Audit-ready final report

## Repository Structure

```txt
sentinel-relay/
  apps/
    web/                    # Next.js frontend baseline
  agents/                   # Python remote agent workers
  data/incidents/            # Safe evidence packets for live prize workflows
  packages/
    sample-data/            # Safe sample incident files
    schemas/                # Message/schema notes
  docs/                     # Project, repo, frontend, and demo docs
  scripts/                  # GitHub and dev helper scripts
  .github/                  # Issue templates, PR template, CI scaffold
```

## Run the Web App

From the repository root:

```bash
corepack pnpm install
corepack pnpm dev
```

Open:

```txt
http://localhost:3000
```

Useful commands:

```bash
corepack pnpm typecheck
corepack pnpm build
corepack pnpm verify
corepack pnpm workflow:evidence:verify
corepack pnpm workflow:evidence:live
corepack pnpm report:verify
```

`packageManager` pins the repo to pnpm 10.11.0. If your machine already has a working `pnpm` command, `pnpm install` and `pnpm verify` are fine too. Corepack is the safest shared path because it uses the pinned package manager version.

## Team Branching Baseline

Before starting feature branches, read:

```txt
docs/56_TEAM_BRANCHING_BASELINE.md
```

Current shared repo:

```txt
https://github.com/Caleb-Todd-commits/sentinel-relay
```

Keep Mock Mode working on every branch. Live Band credentials belong only in local `.env` files and deployment secret stores, never in git.

## Current Routes

| Route | Purpose |
|---|---|
| `/` | Product landing page |
| `/demo` | Sample incident setup |
| `/war-room` | Main incident command dashboard |
| `/report` | Final audit report |
| `/status` | Baseline readiness page |

## Important Docs

Start here:

```txt
docs/TEAM_START_HERE.md
docs/01_BIGGEST_10_FIRST.md
docs/28_MOCK_INCIDENT_FLOW.md
docs/30_MOCK_FLOW_DEMO_SCRIPT.md
docs/45_REAL_BAND_INTEGRATION.md
docs/46_BAND_ENVIRONMENT_SETUP.md
docs/47_REMOTE_AGENT_RUNBOOK.md
docs/51_FINAL_REPORT_AND_AUDIT_REPLAY.md
docs/53_REPORT_TRACEABILITY_MODEL.md
docs/57_EVIDENCE_DRIVEN_AI_ML_API_WORKFLOW.md
```

Step 1 docs:

```txt
docs/01_PROJECT_VISION_LOCK.md
docs/02_PROJECT_CHARTER.md
docs/03_JUDGE_PITCH_AND_POSITIONING.md
docs/04_PRODUCT_BOUNDARIES_AND_NON_GOALS.md
docs/05_TERMINOLOGY.md
docs/06_DECISION_LOG.md
docs/07_TEAM_ONBOARDING_CHECKLIST.md
docs/CODING_AGENT_CONTEXT.md
```

Step 2 docs:

```txt
docs/08_GITHUB_REPO_AND_BRANCH_RULES.md
docs/09_ISSUES_MILESTONES_AND_LABELS.md
docs/10_TEAM_EXECUTION_PROTOCOL.md
docs/11_BRANCH_PROTECTION_AND_REVIEW_RULES.md
docs/12_FIRST_SPRINT_ISSUE_BOARD.md
docs/13_REPO_QUALITY_GATES.md
docs/14_HANDOFF_AND_STATUS_REPORTING.md
```

Step 3 docs:

```txt
docs/15_NEXTJS_BASELINE_RUNNING.md
docs/16_FRONTEND_ARCHITECTURE.md
docs/17_LOCAL_DEV_TROUBLESHOOTING.md
docs/18_UI_COMPONENT_INVENTORY.md
```

## Stability Rules

- Do not commit secrets.
- Do not use real customer/security data.
- Keep Mock Mode working.
- Keep the War Room demoable at every stage.
- Build real Band integration behind the provider contract.
- Prefer one polished scenario over many weak scenarios.
- Make collaboration visible, structured, and evidence-backed.
- Do not remove the Risk challenge or human approval gate; those are the strongest proof moments.

## Current Build Step

Step 10 is now complete:

```txt
Evidence-driven AI/ML API workflow.
```

The War Room can still run in reliable Mock Mode, and Band Mode now routes through secure server-side API routes for room creation, participant registration, structured events, routed messages, approvals, and a local dashboard mirror. The evidence workflow is the strongest live path for judging because it shows agents deriving findings from realistic artifacts and AI/ML API performing real cross-agent reasoning.

## Step 4 Schema Baseline

The project includes a canonical shared schema package at:

```txt
packages/schemas
```

This package defines the shared contracts for:

- frontend TypeScript types,
- Python agent models,
- Band message envelopes,
- sample incident data,
- approval gates,
- remediation tasks,
- final audit reports.

The web app keeps a stable import path through `apps/web/src/lib/types.ts`, which re-exports `@sentinel-relay/schemas`.

Useful schema commands:

```bash
corepack pnpm schemas:validate
corepack pnpm schemas:typecheck
corepack pnpm schemas:contract
```

## Step 5 Mock Workflow Baseline

The mock workflow is implemented in:

```txt
apps/web/src/lib/workflow/
```

The most important files are:

```txt
apps/web/src/lib/workflow/mockWorkflowScript.ts
apps/web/src/lib/workflow/deriveWorkflowState.ts
apps/web/src/lib/workflow/useMockIncidentWorkflow.ts
apps/web/src/app/war-room/page.tsx
```

The workflow demonstrates:

- staged incident replay,
- dynamic agent status changes,
- evidence unlocking,
- visible handoffs,
- visible decision board,
- Risk & Compliance challenge,
- human approval gate,
- remediation unlock after approval,
- final report unlock.

Useful workflow command:

```bash
corepack pnpm workflow:verify
```

The most important Step 5 docs are:

```txt
docs/28_MOCK_INCIDENT_FLOW.md
docs/29_MOCK_WORKFLOW_STATE_MACHINE.md
docs/30_MOCK_FLOW_DEMO_SCRIPT.md
docs/31_STEP5_VERIFICATION_REPORT.md
docs/32_STEP5_TEAM_HANDOFF.md
```

## Step 6 War Room UI Completion

The War Room is now the primary demo surface. It includes:

- sticky command bar,
- incident header,
- judge briefing panel,
- workflow controls,
- critical moment spotlight,
- agent collaboration map,
- state and agent rail,
- structured Band-style message stream,
- human approval gate,
- evidence and timeline panels,
- remediation tasks,
- audit replay trail,
- report preview.

The UI is designed to prove the hackathon thesis quickly: Sentinel Relay is not a single chatbot. It is a coordinated, high-stakes, multi-agent workflow with visible handoffs, challenges, scoped human approval, and an audit-ready output.


## Next Build Step

Step 7 is:

```txt
Add the Collaboration Provider Layer.
```

The UI is now ready for the provider boundary. The next build should make `MockCollaborationProvider` and `BandCollaborationProvider` the formal source of collaboration events so real Band integration can be connected without rewriting the War Room components.

## Step 7: Collaboration Provider Layer

The War Room now uses a provider-backed workflow.

Default runtime:

```env
NEXT_PUBLIC_COLLABORATION_MODE="mock"
NEXT_PUBLIC_ENABLE_BAND_MODE="false"
```

Provider files:

```txt
apps/web/src/lib/collaboration/CollaborationProvider.ts
apps/web/src/lib/collaboration/MockCollaborationProvider.ts
apps/web/src/lib/collaboration/BandCollaborationProvider.ts
apps/web/src/lib/workflow/useIncidentCollaborationWorkflow.ts
```

Mock Mode is fully functional and keeps the demo reliable. Band Mode is scaffolded through server-side API routes so secrets stay out of client code.

Provider verification:

```bash
corepack pnpm provider:verify
```

Full baseline verification:

```bash
corepack pnpm verify
corepack pnpm report:verify
```


## Step 8 Band Integration

The real Band adapter is implemented behind server-side Next.js routes:

```txt
apps/web/src/lib/band/
apps/web/src/app/api/collaboration/
agents/
scripts/band/
```

Useful Band commands:

```bash
corepack pnpm band:env
corepack pnpm band:verify
corepack pnpm band:smoke
```

Band Mode is opt-in:

```env
NEXT_PUBLIC_COLLABORATION_MODE="band"
NEXT_PUBLIC_ENABLE_BAND_MODE="true"
BAND_PROVIDER_ENABLED="true"
BAND_LEADER_AGENT_API_KEY="..."
```

Keep Mock Mode as the final-demo fallback.
