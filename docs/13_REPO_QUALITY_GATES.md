# 13 — Repo Quality Gates

## Purpose

This document defines the minimum quality checks for Sentinel Relay. It is not meant to slow the team down. It is meant to stop the project from collapsing during the demo.

Quality gates should answer one question:

> Is the project still stable enough to show to judges?

## Quality Gate Levels

Use three levels.

## Level 1 — Local Sanity Check

Run before opening a pull request.

```bash
cd apps/web
pnpm install
pnpm typecheck
pnpm build
```

Then manually check:

```txt
/ loads
/demo loads
/war-room loads
/report loads
```

A PR should not be opened if the app cannot render basic pages.

## Level 2 — Pull Request Check

Use before merging.

Checklist:

- [ ] PR has a clear summary.
- [ ] Related issue is linked.
- [ ] No secrets are included.
- [ ] Mock demo path still works.
- [ ] New env vars are added to `.env.example`.
- [ ] Shared schema changes are documented.
- [ ] UI changes include screenshots if possible.
- [ ] Known limitations are listed.

## Level 3 — Demo Readiness Check

Use before recording the final video or submitting.

Checklist:

- [ ] Fresh clone works.
- [ ] Install instructions work.
- [ ] Frontend builds.
- [ ] Hosted app opens.
- [ ] Sample incident starts.
- [ ] War Room shows agent activity.
- [ ] Agent handoff is visible.
- [ ] Agent challenge/disagreement is visible.
- [ ] Human approval is visible.
- [ ] Final report renders.
- [ ] README explains Band usage.
- [ ] Video script matches actual product.
- [ ] No secrets are committed.

## Required Commands

From repo root:

```bash
pnpm web:typecheck
pnpm web:build
```

From web app:

```bash
cd apps/web
pnpm typecheck
pnpm build
```

Optional:

```bash
pnpm lint
```

Only require lint if the lint setup is stable. Do not let lint configuration consume the project.

## CI Workflow

A starter GitHub Actions workflow is included:

```txt
.github/workflows/ci.yml
```

It is intentionally simple. It checks the web app because that is the main judge-facing surface.

Do not make CI complicated unless the project is already stable.

## What Counts as Broken

Broken means:

- App cannot build.
- App cannot run locally.
- Main pages crash.
- Mock mode is gone.
- Sample incident cannot complete.
- Report cannot render.
- Secrets are committed.
- README setup instructions are wrong.

Broken does not mean:

- UI spacing is imperfect.
- A secondary page needs polish.
- Optional agent output is still mocked.
- A non-demo feature is incomplete.

## Secret Scanning

Before major commits, run:

```bash
git diff --cached
```

Look for:

```txt
API keys
Bearer tokens
Band credentials
OpenAI keys
.env values
agent_config.yaml
real logs
private customer data
```

Use fake values only:

```txt
BAND_API_KEY=replace_me
OPENAI_API_KEY=replace_me
DEMO_TOKEN=tok_demo_redacted
```

## Environment Variable Gate

If a PR adds an environment variable, it must also update:

```txt
.env.example
README.md or relevant docs
```

Example:

```env
BAND_API_KEY=replace_me
BAND_AGENT_ID=replace_me
BAND_ROOM_ID=replace_me_optional
```

## Schema Change Gate

If a PR changes a message shape, it must update:

```txt
apps/web/src/lib/types.ts
packages/schemas/message-contract.md
agent prompt if affected
mockIncident.ts if affected
```

The danger is frontend and agents drifting apart. Keep them aligned.

## Demo Path Gate

Every major PR should preserve this:

```txt
No credentials → mock mode → sample incident → report
```

This means the project remains demonstrable even if external services fail.

## Pull Request Risk Ratings

Every PR should include one of these:

```txt
Risk: Low
Risk: Medium
Risk: High
```

### Low Risk

- Docs updates.
- Minor UI copy.
- Sample data improvements.
- Small component styling.

### Medium Risk

- New frontend state logic.
- Provider interface changes.
- Agent prompt changes affecting output.
- Report generation changes.

### High Risk

- Band integration changes.
- Shared schema rewrites.
- Dependency upgrades.
- Major routing or state changes.
- Removing mock fallback.

High-risk PRs should be reviewed before merging unless they are necessary to restore the demo.

## Stability Over Cleverness

Prefer:

- Simple state.
- Clear types.
- Small components.
- Readable data flow.
- Mock fallback.
- Explicit structured messages.

Avoid:

- Hidden magic.
- Complex agent chains before basics work.
- Unnecessary databases.
- New frameworks during final days.
- Fragile live-only demos.

## Final Quality Standard

The final repo should feel like a serious prototype from a focused team, not a pile of files produced during a rush.

A judge should be able to open the repo and quickly understand:

- What the product does.
- How Band is used.
- How the agents collaborate.
- How to run the demo.
- Why the workflow matters.
