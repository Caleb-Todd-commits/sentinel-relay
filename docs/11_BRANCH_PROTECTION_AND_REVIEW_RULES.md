# 11 — Branch Protection and Review Rules

## Purpose

This document defines the exact GitHub branch protection and review rules for Sentinel Relay. The goal is to protect the demo while still moving fast.

## Recommended Branch Setup

Use:

```txt
main
```

Optional:

```txt
dev
```

Recommended for a 5-person team:

```txt
feature branches → dev → main
```

Recommended if the team is moving very quickly:

```txt
feature branches → main
```

## Main Branch Rules

`main` must stay stable.

Recommended settings in GitHub:

1. Go to the GitHub repo.
2. Click **Settings**.
3. Click **Branches**.
4. Add branch protection rule.
5. Branch name pattern: `main`.

Enable:

- Require a pull request before merging.
- Require approvals: `1`.
- Dismiss stale pull request approvals when new commits are pushed: optional.
- Require conversation resolution before merging.
- Block force pushes.
- Block deletions.

If CI is working:

- Require status checks to pass before merging.
- Select `Web CI`.

If CI is not stable yet:

- Do not require CI until it is reliable.
- Use manual validation in PR checklist.

## Dev Branch Rules

If using `dev`, protect it lightly.

Recommended:

- Require pull request before merging: optional.
- Require 1 approval for risky changes.
- Allow faster merges for docs and demo data.
- Do not allow force pushes.

## Pull Request Requirements

Every PR should include:

- Summary.
- Related issue.
- Screenshots for UI changes.
- Testing steps.
- Demo impact.
- Risk assessment.
- Confirmation that no secrets were added.

A PR template has been added at:

```txt
.github/PULL_REQUEST_TEMPLATE.md
```

## Review Priority

Review PRs in this order:

1. Demo-critical fixes.
2. Band integration that unblocks agents.
3. War Room UI changes.
4. Mock flow and sample data.
5. Final report and audit replay.
6. Docs and submission package.
7. Optional polish.

## Fast Merge Exception

During the hackathon, a fast merge is allowed when all are true:

- It is demo-critical.
- The change is small.
- It has been locally tested.
- It does not remove mock fallback.
- The team is notified.

Fast merge message format:

```txt
Fast-merging because:
Risk:
Tested by:
Rollback plan:
```

## Rollback Rule

If a merge breaks the demo path and cannot be fixed quickly:

```bash
git revert <commit-sha>
```

Do not spend hours fixing a broken `main` if a revert restores the demo.

## What Blocks a Merge

A PR should not merge if:

- App does not run.
- TypeScript errors are introduced in shared code.
- Mock mode is broken.
- Secrets are committed.
- Sample incident cannot complete.
- UI becomes unreadable.
- Band integration replaces rather than complements fallback mode.
- The change expands scope without team agreement.

## What Does Not Block a Merge

A PR can merge with minor issues if:

- The demo path works.
- The issue is documented.
- The problem has a follow-up issue.
- It does not affect judging clarity.

Examples:

- Slight spacing issue.
- Non-critical console warning.
- Placeholder copy in a non-demo page.
- Optional agent still using mock output.

## Manual Test Checklist Before Merge

For frontend changes:

```bash
cd apps/web
pnpm install
pnpm typecheck
pnpm build
pnpm dev
```

Then verify:

- `/` loads.
- `/demo` loads.
- `/war-room` loads.
- `/report` loads.
- No obvious UI crash.

For Band/agent changes:

- Mock mode still works.
- Missing credentials do not crash app.
- `.env.example` is updated if env vars changed.
- Real credentials are not committed.
- Structured message format is preserved.

For docs changes:

- Links and filenames are correct.
- Instructions match actual repo structure.
- No secrets or private info are included.

## Final 24-Hour Merge Policy

In the final 24 hours:

- Only merge changes that improve demo, stability, or submission.
- Avoid dependency upgrades.
- Avoid broad refactors.
- Avoid renaming core files.
- Avoid changing the main scenario.
- Avoid anything that requires teammates to relearn the app.

The final day is for sharpening, not reinventing.

## Emergency Demo Branch

If `main` becomes unstable near submission, create:

```txt
demo/final-stable
```

This branch should point to the last known good demo.

Use it for:

- Vercel production deployment.
- Video recording.
- Final submission link if needed.

## Review Language Standard

Keep review comments useful.

Good:

```txt
This component works, but it mixes mock messages and UI rendering. Could you move message creation into mockIncident.ts so the War Room stays easier to connect to Band later?
```

Bad:

```txt
This is messy.
```

The goal is not ego. The goal is shipping.
