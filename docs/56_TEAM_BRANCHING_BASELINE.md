# 56 — Team Branching Baseline

Use this page before splitting into branches.

## Shared Repo

```txt
https://github.com/Caleb-Todd-commits/sentinel-relay
```

Current repo visibility is private. Invited teammates need to accept their GitHub collaborator invitation before cloning.

## Baseline Rule

`main` is the demo-ready baseline. Before creating a branch:

```bash
git checkout main
git pull origin main
corepack pnpm install
corepack pnpm verify
```

If `corepack pnpm verify` passes, create your branch:

```bash
git checkout -b feature/short-task-name
```

## Branch Plan

For five people, use:

```txt
feature branches -> dev -> main
```

Keep `main` stable. Use `dev` as the shared integration branch once the team starts merging parallel work. If the team is moving fast and `dev` slows everyone down, merge feature branches into `main` only after `corepack pnpm verify` passes.

`main` is protected on GitHub. Non-admin changes need a pull request, one approval, and the `Typecheck and build web app` CI check.

## Workstream Lanes

- Frontend and War Room UI
- Band/provider integration
- Agent prompts and runners
- Schemas, sample data, and validation
- Demo script, report, and submission docs

Each branch should mostly stay inside one lane. If a change crosses lanes, say so in the pull request.

## Required Before Pull Request

Run:

```bash
corepack pnpm verify
```

For UI work, also open the app locally:

```bash
corepack pnpm dev
```

Check:

- `/`
- `/demo`
- `/war-room`
- `/report`
- Mock Mode still works

## Secret Rules

- Do not commit `.env` files.
- Do not commit real Band, OpenAI, GitHub, cloud, or customer credentials.
- Use only `.env.example` placeholders in git.
- Put live credentials in local `.env` files or deployment secret stores.
- Re-run `corepack pnpm verify` after changing env handling.

## Communication Rule

Post the branch name, owner, and goal in the team chat before doing substantial work.

Example:

```txt
branch: band/agent-routing
owner: @username
goal: connect routed Band messages for Band Leader -> specialist handoffs
touching: apps/web/src/lib/band, agents/common
```
