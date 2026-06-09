# Contributing to Sentinel Relay

## Purpose

This file explains how teammates should contribute during the hackathon. The goal is to move fast without breaking the demo.

## Start Here

Before coding, read:

1. `docs/TEAM_START_HERE.md`
2. `docs/01_PROJECT_VISION_LOCK.md`
3. `docs/08_GITHUB_REPO_AND_BRANCH_RULES.md`
4. `docs/12_FIRST_SPRINT_ISSUE_BOARD.md`

## Local Setup

```bash
cd apps/web
pnpm install
pnpm dev
```

Open:

```txt
http://localhost:3000
```

## Branching

Create a branch for your task:

```bash
git checkout -b feature/war-room-shell
```

Branch patterns:

```txt
feature/<task>
fix/<task>
docs/<task>
demo/<task>
agent/<task>
band/<task>
chore/<task>
```

## Commit Messages

Use:

```txt
<type>: <short description>
```

Examples:

```txt
feat: add war room shell
band: scaffold collaboration provider
agent: define commander prompt
demo: add sample api logs
docs: update setup guide
fix: prevent report render crash
```

## Pull Requests

Every PR should include:

- What changed.
- Why it matters.
- How to test.
- What could break.
- Screenshots for UI changes.

## No Secrets

Never commit:

- `.env`
- `.env.local`
- `agent_config.yaml`
- API keys
- Band credentials
- OpenAI keys
- real customer data
- real security logs

Only commit `.env.example` with placeholder values.

## Definition of Done

A task is done when:

- Code is committed.
- It matches the issue acceptance criteria.
- The app still runs.
- Mock mode still works if touched.
- Documentation is updated if behavior changed.
- PR is opened or merged.

## Demo Safety

The project should always have one working path:

```txt
Sample incident → War Room → Messages → Evidence → Approval → Report
```

Do not break that path for optional features.
