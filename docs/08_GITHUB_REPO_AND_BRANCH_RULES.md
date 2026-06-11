# 08 — GitHub Repo and Branch Rules

## Purpose

This document locks the repo setup and branch rules for Sentinel Relay. The goal is to keep a fast hackathon build from becoming chaotic. Every teammate should know where work goes, how it is reviewed, what counts as done, and how to avoid breaking the demo.

Sentinel Relay is a one-week hackathon project, so the process should be lightweight. However, because the project depends on multiple people building frontend, Band integration, agents, sample data, and demo materials at the same time, we still need a clear workflow.

The repo should be treated like the central command system for the project:

- Code lives in GitHub.
- Tasks live in GitHub Issues.
- Work happens on branches.
- Pull requests are the checkpoint before shared code changes.
- `main` should stay demo-ready.
- Secrets must never be committed.

## Repo Name

Recommended repo name:

```txt
sentinel-relay
```

Recommended owner:

```txt
Caleb-Todd-commits/sentinel-relay
```

The working team repo is:

```txt
https://github.com/Caleb-Todd-commits/sentinel-relay
```

Keep it private while credentials, live integration notes, and team setup are still moving. Switch to public only when the team is ready for hackathon submission and has re-run the secret checks.

## Repo Visibility

Current team setup:

```txt
Private
```

Reason:

- The invited team can collaborate without exposing in-progress integration notes.
- Secrets are still handled only through local `.env` files and deployment secret stores.
- The repo can be made public later if hackathon submission requires source review.

## Local Repo Setup

From the root of the project folder:

```bash
git init
git add .
git commit -m "chore: initialize Sentinel Relay baseline"
gh repo create sentinel-relay --private --source=. --remote=origin --push
```

If GitHub CLI is not installed, create the repo manually at GitHub.com, then run:

```bash
git remote add origin https://github.com/<owner>/sentinel-relay.git
git branch -M main
git push -u origin main
```

## Required Branches

Use these long-lived branches:

```txt
main
```

Optional during heavy development:

```txt
dev
```

### `main`

`main` is the demo-safe branch.

Rules:

- It should always build.
- It should always be safe to deploy.
- It should never contain broken experiments.
- It should never contain secrets.
- It should only be updated through pull requests once teammates are active.

### `dev`

`dev` is optional. Use it only if the team wants a shared integration branch.

Recommended hackathon approach:

- If there are 2–3 builders: skip `dev`, merge feature branches into `main` carefully.
- If there are 4–5 builders: use `dev` for integration, then merge `dev` into `main` when stable.

Because this project expects roughly 5 people, the recommended approach is:

```txt
feature branches → dev → main
```

But if this slows the team down, simplify to:

```txt
feature branches → main
```

The rule is simple: do not let process slow down the build, but do not let broken code reach the final demo branch.

## Feature Branch Naming

Use this pattern:

```txt
feature/<short-description>
fix/<short-description>
docs/<short-description>
chore/<short-description>
demo/<short-description>
agent/<agent-name-or-capability>
band/<integration-area>
```

Examples:

```txt
feature/war-room-shell
feature/evidence-board
feature/audit-replay
band/collaboration-provider
band/room-creation
agent/commander-routing
agent/forensics-log-parser
docs/demo-script-v1
demo/sample-incident-data
fix/report-render-crash
chore/add-ci-workflow
```

## Branch Ownership

Each major workstream should have one main branch owner.

| Workstream | Suggested Branch | Owner Type |
|---|---|---|
| Frontend dashboard | `feature/war-room-ui` | Frontend lead |
| Band integration | `band/collaboration-provider` | Band/backend lead |
| Agent logic | `agent/core-agent-prompts` | Agent logic lead |
| Demo/sample data | `demo/sample-incident-data` | Demo/data lead |
| Final report | `feature/final-report` | Frontend or report lead |
| Submission docs | `docs/submission-package` | Caleb/demo lead |

Branch owners are not the only people allowed to contribute. They are responsible for keeping that branch focused and mergeable.

## Commit Message Standard

Use clear, boring commit messages. Do not be clever.

Format:

```txt
<type>: <short description>
```

Allowed types:

```txt
feat      New feature
fix       Bug fix
docs      Documentation only
chore     Repo/config/tooling work
refactor  Code cleanup without behavior change
test      Tests or validation scripts
demo      Demo data, video, pitch, sample flow
agent     Agent prompts, logic, schemas
band      Band integration work
ui        UI-only changes
```

Examples:

```txt
feat: add war room shell
ui: add agent roster cards
band: scaffold collaboration provider
agent: define commander output schema
demo: add api key exposure sample logs
docs: add judge pitch narrative
fix: prevent empty timeline render crash
chore: add pull request template
```

## Pull Request Rules

Every pull request should answer four questions:

1. What changed?
2. Why does it matter for the demo?
3. How was it tested?
4. What could break?

A pull request should be small enough to review quickly. Large PRs are allowed only when building foundational scaffolding.

Recommended PR size:

```txt
Ideal: 100–400 changed lines
Acceptable during setup: 400–1,000 changed lines
Risky: 1,000+ changed lines
```

If a PR is large, include a strong summary.

## Merge Rules

During early build:

- One review is preferred.
- Caleb or the workstream lead can merge if the team is moving fast.
- Do not merge code that prevents the demo from running.

During the final 48 hours:

- No major architecture rewrites.
- No untested API integration changes directly to `main`.
- Every merge must preserve the fallback demo path.
- UI polish is allowed if it does not break the core flow.

## Main Branch Protection

Turn on these settings when the repo is created:

Recommended minimum:

- Require a pull request before merging.
- Require at least 1 approval.
- Require conversation resolution before merging.
- Block force pushes.
- Block deletions.

If CI is stable:

- Require status checks to pass before merging.

If CI is flaky or incomplete:

- Do not block merges on CI yet.
- Use manual validation instead.

Hackathon rule: a stable demo matters more than perfect branch protection.

## Required Repo Files

The repo should include:

```txt
README.md
CONTRIBUTING.md
SECURITY.md
.env.example
.gitignore
.github/PULL_REQUEST_TEMPLATE.md
.github/CODEOWNERS
.github/ISSUE_TEMPLATE/
.github/workflows/ci.yml
docs/TEAM_START_HERE.md
docs/01_PROJECT_VISION_LOCK.md
docs/08_GITHUB_REPO_AND_BRANCH_RULES.md
```

## Required GitHub Issues

All work should be tracked as issues. Issue titles should be short and action-oriented.

Examples:

```txt
[Frontend] Build war room layout shell
[Band] Create collaboration provider interface
[Agent] Define commander agent prompt and schema
[Demo] Create API key exposure sample data
[Report] Build audit report page
[Pitch] Draft 3-minute demo script
```

## Required GitHub Labels

Use labels to keep work easy to scan.

Core labels:

```txt
priority:P0
priority:P1
priority:P2
status:ready
status:blocked
status:in-progress
area:frontend
area:band
area:agents
area:demo-data
area:docs
area:reporting
area:ui-polish
area:submission
type:feature
type:bug
type:docs
type:chore
type:decision
risk:demo-critical
risk:security-sensitive
```

## Milestones

Use these milestones:

1. **M0 — Repo Ready**
2. **M1 — Mock Demo Vertical Slice**
3. **M2 — Band Collaboration Connected**
4. **M3 — Agent Intelligence and Structured Handoffs**
5. **M4 — Demo Polish and Submission**

## Project Board Columns

Use a GitHub Project board or issue labels with these states:

```txt
Backlog
Ready
In Progress
Needs Review
Blocked
Done
```

For a one-week hackathon, do not make the board more complicated than this.

## Daily Sync Rule

At the beginning or end of each work session, each person should post:

```txt
Yesterday/last session: what I finished
Today/this session: what I am building
Blocked: what I need
PR/branch: link or branch name
```

## Demo Safety Rule

At all times, one path must remain demoable.

This means:

- Mock mode must continue to work.
- The sample incident must continue to run.
- The War Room must continue to render.
- The report page must not be deleted or hidden.
- Real Band integration should not destroy mock fallback.

The project can have incomplete pieces. It cannot have no demo.

## Secret Safety Rule

Never commit:

- API keys
- Band credentials
- `.env`
- `.env.local`
- `agent_config.yaml`
- real logs
- real customer data
- private tokens
- screenshots showing secrets

Only commit:

- `.env.example`
- fake sample data
- safe mock keys like `sk_demo_redacted`

## Definition of Repo Ready

Step 2 is complete when:

- Public repo exists.
- `main` exists.
- Optional `dev` exists if the team wants it.
- Issue templates exist.
- PR template exists.
- CODEOWNERS exists.
- Labels and milestones are defined.
- First sprint issues are written.
- Every teammate knows their initial area.
- README points to the important docs.
- No secrets are committed.

## Final Instruction

Do not use GitHub as a storage bucket. Use it as the team operating system.

Every task should have an issue. Every major change should have a branch. Every merge should protect the demo.
