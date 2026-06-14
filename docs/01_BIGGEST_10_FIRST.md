# The Biggest 10 Things To Do First

These are the first 10 things to build, in order. Do not skip ahead. The goal is to make the project stable, demoable, and judge-readable before adding extra complexity.

## 1. Lock the Project Vision — COMPLETED BASELINE

The project vision has been expanded into a full source-of-truth document set.

Primary source:

- `docs/01_PROJECT_VISION_LOCK.md`

Supporting documents:

- `docs/02_PROJECT_CHARTER.md`
- `docs/03_JUDGE_PITCH_AND_POSITIONING.md`
- `docs/04_PRODUCT_BOUNDARIES_AND_NON_GOALS.md`
- `docs/05_TERMINOLOGY.md`
- `docs/06_DECISION_LOG.md`
- `docs/07_TEAM_ONBOARDING_CHECKLIST.md`
- `docs/TEAM_START_HERE.md`

Locked core idea:

> Sentinel Relay is a Band-powered multi-agent cybersecurity incident command center where agents coordinate through Band to investigate evidence, challenge weak conclusions, request human approval, create remediation tasks, and generate an audit-ready incident report.

Success condition:

- Every teammate can explain the project in 30 seconds.
- Everyone knows Band is the center of the workflow, not a notification layer.
- The main scenario is locked: Possible API Key Exposure After Friday Deploy.
- The primary track is locked: Track 3, with Track 2 influence through remediation/code review.
- The team understands what is in scope and out of scope.
- The team has a shared vocabulary for agents, findings, evidence, challenges, approvals, and audit trail.

## 2. Create the GitHub Repo and Branch Rules — COMPLETED BASELINE

The GitHub repo and branch workflow have been expanded into a full repo-readiness package.

Primary source:

- `docs/08_GITHUB_REPO_AND_BRANCH_RULES.md`

Supporting documents and repo files:

- `docs/09_ISSUES_MILESTONES_AND_LABELS.md`
- `docs/10_TEAM_EXECUTION_PROTOCOL.md`
- `docs/11_BRANCH_PROTECTION_AND_REVIEW_RULES.md`
- `docs/12_FIRST_SPRINT_ISSUE_BOARD.md`
- `docs/13_REPO_QUALITY_GATES.md`
- `docs/14_HANDOFF_AND_STATUS_REPORTING.md`
- `docs/FIRST_25_ISSUES.csv`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/CODEOWNERS`
- `.github/ISSUE_TEMPLATE/`
- `.github/workflows/ci.yml`
- `scripts/github/`

Locked repo rules:

- Public GitHub repo named `sentinel-relay`.
- `main` stays demo-ready.
- Optional `dev` branch can be used if the team wants an integration branch.
- Feature branches use clear prefixes like `feature/`, `band/`, `agent/`, `demo/`, `docs/`, and `fix/`.
- GitHub Issues are used for task ownership.
- Pull requests use the included template.
- No secrets, real logs, or customer data are committed.
- Mock mode must stay functional even when Band mode is being built.

Success condition:

- Repo exists publicly.
- README is clear.
- Everyone can clone and run the project locally.
- First 25 issues are ready to create.
- Labels and milestones are defined.
- Branch protection rules are documented.
- No secrets are committed.

## 3. Get the Next.js Baseline Running — COMPLETED BASELINE

The Next.js baseline has been expanded into a stable, product-shaped frontend that the team can run and build on.

Primary source:

- `docs/15_NEXTJS_BASELINE_RUNNING.md`

Supporting documents and app files:

- `docs/16_FRONTEND_ARCHITECTURE.md`
- `docs/17_LOCAL_DEV_TROUBLESHOOTING.md`
- `docs/18_UI_COMPONENT_INVENTORY.md`
- `apps/web/README.md`
- `apps/web/src/app/`
- `apps/web/src/components/`
- `apps/web/src/lib/demo/sentinelRelayDemo.ts`
- `apps/web/src/lib/types.ts`
- `scripts/dev/verify-web-baseline.sh`

Completed route baseline:

- `/` — judge-facing product landing page.
- `/demo` — sample incident setup and launch page.
- `/war-room` — main incident command dashboard.
- `/report` — final audit report.
- `/status` — local readiness check page.

Completed UI baseline:

- Incident header
- Agent roster
- Band-style message stream
- Evidence board
- Incident timeline
- Human approval gate
- Remediation task list
- Report preview
- Replay and complete-demo controls

Success condition:

- The web app has clear run commands.
- The pages are product-shaped rather than empty placeholders.
- The mock incident flow is visible and judge-readable.
- The app is structured so real Band messages can later replace mock data without a major UI rewrite.

## 4. Define the Shared Data Schemas — COMPLETED BASELINE

The shared data schema layer is now formalized across TypeScript, JSON Schema, Python agent models, sample data, and human-readable contracts.

Primary source:

- `docs/21_SHARED_SCHEMA_SYSTEM.md`

Supporting documents and schema files:

- `docs/22_BAND_MESSAGE_SCHEMA.md`
- `docs/23_AGENT_INPUT_OUTPUT_CONTRACTS.md`
- `docs/24_SAMPLE_DATA_AND_REPORT_SCHEMA.md`
- `docs/25_SCHEMA_VALIDATION_AND_VERSIONING.md`
- `docs/26_STEP4_VERIFICATION_REPORT.md`
- `docs/27_STEP4_TEAM_HANDOFF.md`
- `packages/schemas/src/`
- `packages/schemas/json-schema/`
- `packages/schemas/python/`
- `packages/schemas/contracts/`
- `packages/sample-data/demo_incident.json`
- `scripts/schema/validate-sample-data.py`

Completed canonical objects:

- IncidentCase
- IncidentStateSnapshot
- AgentProfile
- AgentAssignment
- AgentMessage
- BandEnvelope
- FindingPayload
- ChallengePayload
- RiskAssessmentPayload
- TaskAssignmentPayload
- HandoffPayload
- EvidenceReference
- TimelineEvent
- ApprovalRequest
- ApprovalDecision
- RemediationTask
- RemediationPlan
- FinalReport
- ReportSection
- DemoIncident

Locked schema rules:

- `packages/schemas` is the source of truth.
- The web app keeps importing from `@/lib/types`, which now re-exports the schema package.
- Agents should output structured `AgentMessage` objects, not paragraphs.
- Band payloads should use a `BandEnvelope`.
- Every major claim should reference `evidenceIds`.
- Every high-impact action must go through `ApprovalRequest` and `ApprovalDecision`.
- The final report must link back to evidence and message IDs.

Success condition:

- Frontend, agents, Band payloads, sample data, and docs all use the same language.
- Messages are structured, not random text blobs.
- The demo sample data can be validated using `pnpm schemas:validate`.
- Future agent prompts have a concrete output contract.

## 5. Build the Mock Incident Flow — COMPLETED BASELINE

The mock incident flow is now a deterministic, replayable workflow with state transitions instead of a simple static page.

Primary source:

- `docs/28_MOCK_INCIDENT_FLOW.md`

Supporting documents and app files:

- `docs/29_MOCK_WORKFLOW_STATE_MACHINE.md`
- `docs/30_MOCK_FLOW_DEMO_SCRIPT.md`
- `docs/31_STEP5_VERIFICATION_REPORT.md`
- `docs/32_STEP5_TEAM_HANDOFF.md`
- `apps/web/src/lib/workflow/`
- `apps/web/src/components/war-room/WorkflowControls.tsx`
- `apps/web/src/components/war-room/StateMachinePanel.tsx`
- `apps/web/src/components/war-room/HandoffPanel.tsx`
- `apps/web/src/components/war-room/DecisionPanel.tsx`

Completed mock flow:

1. Demo staged and ready.
2. Band Leader opens the Band-style incident room.
3. Specialist review tasks are assigned.
4. Forensics identifies suspicious API token usage.
5. Threat Intel qualifies confidence without overclaiming.
6. Code Review finds possible token exposure in the recent diff.
7. Risk & Compliance challenges the customer-impact claim.
8. Band Leader requests human approval.
9. Human Security Lead approves containment and defers customer notice.
10. Remediation creates scoped fix tasks.
11. Final audit-ready report appears.

Locked behavior:

- The War Room starts at step 0 with no visible messages.
- Evidence unlocks as agent messages appear.
- Agent statuses change based on the current workflow phase.
- The Risk challenge appears before approval.
- Remediation is blocked at the approval gate.
- The user must click `Approve containment` to move past the human decision gate.
- The final report unlocks only after the full message stream is visible.

Success condition:

- The demo works without real APIs.
- The story is easy to understand.
- The approval gate visibly prevents unsafe automation.
- The mock workflow defines the contract that real Band messages must later satisfy.

## 6. Build the War Room UI — COMPLETE

Build the main page judges will see.

Required panels:

- Incident header
- Agent roster
- Band collaboration stream
- Evidence board
- Timeline
- Human approval gate
- Remediation checklist
- Report preview
- Replay button

Step 6 completion added:

- Sticky command bar
- Judge briefing panel
- Critical challenge/approval spotlight
- Collaboration map
- Upgraded structured message cards
- Evidence limitations and sensitivity display
- Audit replay trail
- Stronger approval gate
- Responsive three-zone War Room layout

Success condition:

- A judge can look at the UI and understand what happened.
- A judge can identify the Band coordination proof in less than 30 seconds.

## 7. Add the Collaboration Provider Layer — COMPLETE

Create this abstraction before connecting real Band:

```txt
CollaborationProvider
MockCollaborationProvider
BandCollaborationProvider
```

Required methods:

- createIncidentRoom(caseId)
- registerAgent(agent)
- sendMessage(roomId, message)
- getMessages(roomId)
- subscribeToMessages(roomId, callback)
- requestHumanApproval(roomId, request)
- submitHumanDecision(roomId, decision)

Success condition:

- Mock mode keeps working.
- Band mode can be added without rewriting the UI.

Step 7 completion added:

- Provider-backed War Room state.
- Strong MockCollaborationProvider.
- BandCollaborationProvider routed through server-side API scaffolds.
- Provider status panel.
- Snapshot/audit synchronization.

## 8. Connect Real Band Agent Communication — COMPLETE

Once the mock provider is stable, connect real Band rooms and agent messages.

Step 8 completion added:

- Server-side Band REST client.
- Band room creation through `/api/v1/agent/chats`.
- Participant registration through `/api/v1/agent/chats/{chat_id}/participants`.
- Structured Sentinel Relay messages posted as Band task events.
- Routed text messages posted when target Band participant IDs are configured.
- Approval requests and decisions posted as structured Band events.
- Local dashboard mirror and SSE stream for War Room state.
- Band health endpoint and smoke-test scripts.
- Python remote agent workers using the Band/Thenvoi SDK pattern.
- Live mode remains opt-in so Mock Mode is still the safest demo path.

Success condition:

- At least 3 agents can collaborate through Band when credentials and participant IDs are configured.
- Messages show in the War Room through the local dashboard mirror.
- Band is used during the workflow for rooms, participants, messages, and structured events.
- Missing credentials fail safely with recoverable errors instead of breaking Mock Mode.

Primary docs:

- `docs/45_REAL_BAND_INTEGRATION.md`
- `docs/46_BAND_ENVIRONMENT_SETUP.md`
- `docs/47_REMOTE_AGENT_RUNBOOK.md`
- `docs/48_BAND_ROUTE_CONTRACTS.md`

## 9. Build the Final Report and Audit Replay

**Status: Complete.**

Step 9 turns the final output into a judge-readable incident report generated from structured collaboration records, not a loose summary.

Included:

- Enterprise-style `/report` route
- Final report hero and report posture metadata
- Report metrics grid
- Report sections with evidence IDs and source message IDs
- Integrity checks for traceability
- Human approval record with scoped approval and explicitly not-approved actions
- Audit replay table generated from `finalReport.auditTrailMessageIds`
- Evidence matrix linking evidence to report sections and agent messages
- Remediation control plan with evidence, acceptance criteria, test plans, and rollback plans
- Open questions and limitations
- Export checklist for future production handoff

Success condition:

- The final report feels enterprise-ready.
- The report clearly proves how evidence, agent messages, challenge, approval, and remediation connect.
- The audit replay makes the collaboration obvious.
- The report remains fully demoable in Mock Mode.

Primary docs:

- `docs/51_FINAL_REPORT_AND_AUDIT_REPLAY.md`
- `docs/52_REPORT_UI_COMPONENTS.md`
- `docs/53_REPORT_TRACEABILITY_MODEL.md`
- `docs/54_STEP9_VERIFICATION_REPORT.md`
- `docs/55_STEP9_TEAM_HANDOFF.md`

Verification:

```bash
python scripts/report/verify-report-layer.py
```

## 10. Polish the Demo and Submission Package

Prepare:

- 3-minute demo video
- Slide deck
- Architecture diagram
- README
- Public repo
- Hosted app
- Clean sample data
- Backup demo path

Success condition:

- The project can be understood and judged quickly.
- The demo does not depend on fragile live randomness.


## Step 7 Completion Summary — Collaboration Provider Layer

Step 7 is complete.

The project now has a real provider boundary between the War Room UI and the collaboration transport. Mock Mode is fully functional and provider-backed. Band Mode is safely scaffolded behind server-side API routes for Step 8.

Important files:

```txt
apps/web/src/lib/collaboration/CollaborationProvider.ts
apps/web/src/lib/collaboration/MockCollaborationProvider.ts
apps/web/src/lib/collaboration/BandCollaborationProvider.ts
apps/web/src/lib/workflow/useIncidentCollaborationWorkflow.ts
apps/web/src/components/war-room/ProviderStatusPanel.tsx
```

Verification:

```bash
python scripts/provider/verify-provider-layer.py
```

Step 8 is complete.

Step 9 is complete.

Next priority: Step 10 — Polish the demo and submission package.


## Step 9 Completion Summary — Final Report and Audit Replay

Step 9 is complete.

The project now has a dedicated final report system that turns the demo incident into a traceable audit artifact. The report page now includes metrics, integrity checks, human approval scope, evidence matrix, remediation control plan, audit replay table, open questions, and export checklist.

Important files:

```txt
apps/web/src/app/report/page.tsx
apps/web/src/lib/report/auditReportModel.ts
apps/web/src/components/report/
scripts/report/verify-report-layer.py
```

Verification:

```bash
python scripts/report/verify-report-layer.py
```

Next priority: Step 10 — polish the final demo and submission package.
