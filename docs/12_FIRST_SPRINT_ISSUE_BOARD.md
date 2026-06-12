# 12 — First Sprint Issue Board

## Purpose

This document defines the first GitHub issue board for Sentinel Relay. These are the first tasks the team should create and assign after the repo is pushed.

The goal is to move from planning to a working baseline without confusion.

## Sprint Name

```txt
M0/M1 — Repo Ready + Mock Demo Vertical Slice
```

## Sprint Outcome

By the end of this sprint, the project should have:

- Public GitHub repo.
- Clear task board.
- Stable Next.js app.
- War Room screen scaffold.
- Mock incident flow started.
- Sample data committed.
- Team roles assigned.
- First Band integration path identified.

## Board Columns

```txt
Backlog
Ready
In Progress
Needs Review
Blocked
Done
```

## Issue 1 — Repo Setup

Title:

```txt
[Repo] Create public GitHub repo and push baseline
```

Labels:

```txt
priority:P0, area:devops, type:chore, status:ready, risk:demo-critical
```

Milestone:

```txt
M0 — Repo Ready
```

Goal:

Create the public GitHub repo and push the baseline folder.

Acceptance criteria:

- [ ] Repo exists publicly.
- [ ] `main` branch exists.
- [ ] Baseline files are pushed.
- [ ] README renders correctly.
- [ ] No secrets are committed.
- [ ] All teammates have repo access or can fork/clone.

## Issue 2 — Branch Rules

Title:

```txt
[Repo] Add branch protection and PR review rules
```

Labels:

```txt
priority:P0, area:devops, type:chore, status:ready
```

Milestone:

```txt
M0 — Repo Ready
```

Acceptance criteria:

- [ ] `main` has branch protection.
- [ ] Pull requests are required before merge, unless team chooses fast mode.
- [ ] Force pushes are blocked.
- [ ] PR template appears when opening a PR.
- [ ] CODEOWNERS file exists.

## Issue 3 — Labels and Milestones

Title:

```txt
[Repo] Create GitHub labels and milestones
```

Labels:

```txt
priority:P0, area:devops, type:chore, status:ready
```

Milestone:

```txt
M0 — Repo Ready
```

Acceptance criteria:

- [ ] Priority labels exist.
- [ ] Area labels exist.
- [ ] Type labels exist.
- [ ] Status labels exist.
- [ ] Risk labels exist.
- [ ] M0–M4 milestones exist.

## Issue 4 — Team Role Assignment

Title:

```txt
[Team] Assign initial workstream owners
```

Labels:

```txt
priority:P0, area:docs, type:decision, status:ready
```

Milestone:

```txt
M0 — Repo Ready
```

Acceptance criteria:

- [ ] Frontend lead assigned.
- [ ] Band/backend lead assigned.
- [ ] Agent logic lead assigned.
- [ ] Demo/data/docs lead assigned.
- [ ] Caleb confirmed as product/cybersecurity/pitch lead.
- [ ] Each person has first issue assigned.

## Issue 5 — Local Setup Verification

Title:

```txt
[DevEx] Verify every teammate can run the app locally
```

Labels:

```txt
priority:P0, area:devops, type:chore, status:ready, risk:demo-critical
```

Milestone:

```txt
M0 — Repo Ready
```

Acceptance criteria:

- [ ] Each teammate clones repo.
- [ ] Each teammate runs install.
- [ ] Each teammate runs dev server.
- [ ] Any setup issues are documented.
- [ ] README setup instructions are corrected if needed.

## Issue 6 — War Room Layout Shell

Title:

```txt
[Frontend] Build war room layout shell
```

Labels:

```txt
priority:P0, area:frontend, type:feature, status:ready, risk:demo-critical
```

Milestone:

```txt
M1 — Mock Demo Vertical Slice
```

Acceptance criteria:

- [ ] Incident header area exists.
- [ ] Agent roster area exists.
- [ ] Message stream area exists.
- [ ] Evidence board area exists.
- [ ] Timeline area exists.
- [ ] Approval gate area exists.
- [ ] Report preview area exists.
- [ ] Layout is readable on laptop screen.

## Issue 7 — Shared TypeScript Schemas

Title:

```txt
[Schemas] Define shared incident and message types
```

Labels:

```txt
priority:P0, area:schemas, area:frontend, type:feature, status:ready, risk:demo-critical
```

Milestone:

```txt
M1 — Mock Demo Vertical Slice
```

Acceptance criteria:

- [ ] `IncidentCase` type exists.
- [ ] `AgentProfile` type exists.
- [ ] `AgentMessage` type exists.
- [ ] `Finding` type exists.
- [ ] `EvidenceReference` type exists.
- [ ] `Challenge` type exists.
- [ ] `ApprovalRequest` type exists.
- [ ] `ApprovalDecision` type exists.
- [ ] `RemediationTask` type exists.
- [ ] `FinalReport` type exists.

## Issue 8 — Mock Incident State

Title:

```txt
[Demo] Build mocked incident state for API key exposure scenario
```

Labels:

```txt
priority:P0, area:demo-data, area:frontend, type:demo, status:ready, risk:demo-critical
```

Milestone:

```txt
M1 — Mock Demo Vertical Slice
```

Acceptance criteria:

- [ ] Mock case loads.
- [ ] Agent list loads.
- [ ] Initial timeline loads.
- [ ] Message sequence exists.
- [ ] Evidence references connect to sample files.
- [ ] Final report seed exists.

## Issue 9 — Run Demo Incident Button

Title:

```txt
[Frontend] Add Run Demo Incident and replay controls
```

Labels:

```txt
priority:P0, area:frontend, type:feature, status:ready, risk:demo-critical
```

Milestone:

```txt
M1 — Mock Demo Vertical Slice
```

Acceptance criteria:

- [ ] Run button starts the sample incident sequence.
- [ ] Messages appear step by step.
- [ ] Replay resets the state.
- [ ] Final report becomes available at the end.
- [ ] Demo does not require external credentials.

## Issue 10 — Message Stream Cards

Title:

```txt
[Frontend] Build structured agent message cards
```

Labels:

```txt
priority:P0, area:frontend, type:feature, status:ready, risk:demo-critical
```

Milestone:

```txt
M1 — Mock Demo Vertical Slice
```

Acceptance criteria:

- [ ] Cards show agent name.
- [ ] Cards show message type.
- [ ] Cards show confidence when available.
- [ ] Cards show evidence references when available.
- [ ] Challenge messages are visually distinct.
- [ ] Approval requests are visually distinct.

## Issue 11 — Evidence Board

Title:

```txt
[Frontend] Build evidence board from structured findings
```

Labels:

```txt
priority:P1, area:frontend, area:reporting, type:feature, status:ready
```

Milestone:

```txt
M1 — Mock Demo Vertical Slice
```

Acceptance criteria:

- [ ] Evidence cards display source file.
- [ ] Evidence cards display claim.
- [ ] Evidence cards display confidence.
- [ ] Evidence cards connect to timeline/finding IDs.
- [ ] Evidence board updates during replay.

## Issue 12 — Agent Challenge Moment

Title:

```txt
[Agent] Add visible risk/compliance challenge moment
```

Labels:

```txt
priority:P0, area:agents, area:demo-data, type:demo, status:ready, risk:demo-critical
```

Milestone:

```txt
M1 — Mock Demo Vertical Slice
```

Acceptance criteria:

- [ ] Risk agent challenges a weak breach conclusion.
- [ ] Challenge references specific missing evidence.
- [ ] Band Leader assigns follow-up verification.
- [ ] Challenge appears in War Room UI.
- [ ] Final report mentions the challenge.

## Issue 13 — Human Approval Gate

Title:

```txt
[Frontend] Build human approval gate for containment actions
```

Labels:

```txt
priority:P0, area:frontend, area:reporting, type:feature, status:ready, risk:demo-critical
```

Milestone:

```txt
M1 — Mock Demo Vertical Slice
```

Acceptance criteria:

- [ ] Approval request appears after risk assessment.
- [ ] User can approve containment.
- [ ] User can reject/hold action.
- [ ] Approval decision is added to message stream.
- [ ] Report includes approval decision.

## Issue 14 — Collaboration Provider Interface

Title:

```txt
[Band] Create CollaborationProvider interface and mock provider
```

Labels:

```txt
priority:P0, area:band, area:frontend, type:feature, status:ready, risk:integration, risk:demo-critical
```

Milestone:

```txt
M2 — Band Collaboration Connected
```

Acceptance criteria:

- [ ] `CollaborationProvider` interface exists.
- [ ] `MockCollaborationProvider` implements it.
- [ ] `BandCollaborationProvider` scaffold exists.
- [ ] UI can use provider without knowing mode.
- [ ] Missing Band credentials fall back safely.

## Issue 15 — Band Room Creation

Title:

```txt
[Band] Connect incident room creation through Band
```

Labels:

```txt
priority:P0, area:band, type:feature, status:ready, risk:integration, risk:demo-critical
```

Milestone:

```txt
M2 — Band Collaboration Connected
```

Acceptance criteria:

- [ ] App can create or reference a Band room for an incident.
- [ ] Room ID is stored in incident state.
- [ ] Errors are handled safely.
- [ ] Mock mode still works.
- [ ] README/env docs are updated.

## Issue 16 — Agent Registration

Title:

```txt
[Band] Register specialized agents in incident room
```

Labels:

```txt
priority:P0, area:band, area:agents, type:feature, status:ready, risk:integration
```

Milestone:

```txt
M2 — Band Collaboration Connected
```

Acceptance criteria:

- [ ] Band Leader agent can join/appear.
- [ ] Forensics agent can join/appear.
- [ ] Risk/compliance agent can join/appear.
- [ ] At least one additional agent joins/appears.
- [ ] UI shows active agents.

## Issue 17 — Agent Prompt Pack

Title:

```txt
[Agent] Expand prompts for all six specialized agents
```

Labels:

```txt
priority:P1, area:agents, type:feature, status:ready
```

Milestone:

```txt
M3 — Agent Intelligence and Structured Handoffs
```

Acceptance criteria:

- [ ] Band Leader prompt is specific.
- [ ] Forensics prompt is specific.
- [ ] Threat Intel prompt is specific.
- [ ] Code Review prompt is specific.
- [ ] Risk & Compliance prompt is specific.
- [ ] Remediation prompt is specific.
- [ ] Each prompt includes allowed actions and human-approval boundaries.

## Issue 18 — Final Report Page

Title:

```txt
[Report] Build audit-ready final report page
```

Labels:

```txt
priority:P0, area:reporting, area:frontend, type:feature, status:ready, risk:demo-critical
```

Milestone:

```txt
M1 — Mock Demo Vertical Slice
```

Acceptance criteria:

- [ ] Executive summary appears.
- [ ] Timeline appears.
- [ ] Evidence table appears.
- [ ] Root cause appears.
- [ ] Risk assessment appears.
- [ ] Human approval record appears.
- [ ] Remediation tasks appear.
- [ ] Audit trail appears.

## Issue 19 — Audit Replay

Title:

```txt
[Report] Add audit replay mode
```

Labels:

```txt
priority:P1, area:reporting, area:frontend, type:feature, status:ready
```

Milestone:

```txt
M4 — Demo Polish and Submission
```

Acceptance criteria:

- [ ] Replay button exists.
- [ ] Messages replay in sequence.
- [ ] Timeline updates during replay.
- [ ] Replay clearly shows handoffs.
- [ ] Replay can be used during video demo.

## Issue 20 — Final Submission README

Title:

```txt
[Docs] Prepare README for hackathon judges
```

Labels:

```txt
priority:P0, area:docs, area:submission, type:docs, status:ready, risk:demo-critical
```

Milestone:

```txt
M4 — Demo Polish and Submission
```

Acceptance criteria:

- [ ] README explains what was built.
- [ ] README explains how Band is used.
- [ ] README explains agent roles.
- [ ] README explains how to run locally.
- [ ] README includes demo link placeholder.
- [ ] README includes architecture summary.
- [ ] README includes no secrets.

## Issue 21 — Architecture Diagram

Title:

```txt
[Docs] Create architecture diagram for judges
```

Labels:

```txt
priority:P1, area:docs, area:submission, type:docs, status:ready
```

Milestone:

```txt
M4 — Demo Polish and Submission
```

Acceptance criteria:

- [ ] Diagram shows frontend.
- [ ] Diagram shows Band room.
- [ ] Diagram shows agents.
- [ ] Diagram shows sample data.
- [ ] Diagram shows report/audit trail.
- [ ] Diagram is included in README or docs.

## Issue 22 — Demo Video Script

Title:

```txt
[Pitch] Finalize 3-minute demo video script
```

Labels:

```txt
priority:P0, area:submission, area:docs, type:demo, status:ready, risk:demo-critical
```

Milestone:

```txt
M4 — Demo Polish and Submission
```

Acceptance criteria:

- [ ] Hook explains problem in 20 seconds.
- [ ] Band value is stated clearly.
- [ ] Agents and roles are shown.
- [ ] Challenge/disagreement moment is shown.
- [ ] Human approval is shown.
- [ ] Final report is shown.
- [ ] Closing line explains why this matters.

## Issue 23 — Vercel Deployment

Title:

```txt
[DevOps] Deploy frontend to Vercel
```

Labels:

```txt
priority:P0, area:devops, area:submission, type:chore, status:ready, risk:demo-critical
```

Milestone:

```txt
M4 — Demo Polish and Submission
```

Acceptance criteria:

- [ ] Vercel project connected to GitHub.
- [ ] Production deployment works.
- [ ] Demo URL is saved in README.
- [ ] Environment variables are documented.
- [ ] Mock mode works in deployed app.

## Issue 24 — Submission Copy

Title:

```txt
[Submission] Draft lablab project submission copy
```

Labels:

```txt
priority:P0, area:submission, type:docs, status:ready, risk:demo-critical
```

Milestone:

```txt
M4 — Demo Polish and Submission
```

Acceptance criteria:

- [ ] Short description written.
- [ ] Long description written.
- [ ] Track choice explained.
- [ ] Band usage explained.
- [ ] Business value explained.
- [ ] Tech stack listed.
- [ ] Demo link placeholder included.
- [ ] GitHub link placeholder included.

## Issue 25 — Final Smoke Test

Title:

```txt
[QA] Run final smoke test before submission
```

Labels:

```txt
priority:P0, area:devops, area:submission, type:bug, status:ready, risk:demo-critical
```

Milestone:

```txt
M4 — Demo Polish and Submission
```

Acceptance criteria:

- [ ] Fresh clone works.
- [ ] Install works.
- [ ] Build works.
- [ ] Deployed URL works.
- [ ] Demo flow works.
- [ ] Report works.
- [ ] README instructions are accurate.
- [ ] No secrets are committed.
- [ ] Submission assets are ready.

## Recommended First Assignments

| Person | First Issue |
|---|---|
| Caleb | Issue 4, Issue 22, Issue 24 |
| Frontend lead | Issue 6, Issue 9, Issue 10 |
| Band/backend lead | Issue 14, Issue 15, Issue 16 |
| Agent logic lead | Issue 7, Issue 12, Issue 17 |
| Demo/docs lead | Issue 8, Issue 18, Issue 20 |

## First 24 Hours Target

By the end of the first serious build day:

- Repo is live.
- Everyone has a branch.
- War Room shell exists.
- Mock incident data exists.
- Shared schemas exist.
- First replayable message sequence exists or is close.
- Band integration path is confirmed.

## Success Test

The board is working if someone can open GitHub and immediately know:

- What is most important.
- Who owns what.
- What is blocked.
- What is ready for review.
- Whether the project is on track to demo.
