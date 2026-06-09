# 09 — Issues, Milestones, and Labels

## Purpose

This document defines how the team should organize work inside GitHub. A one-week hackathon can become chaotic quickly. This issue system is designed to keep everyone moving without burying the team in process.

The goal is simple:

- Everyone knows what to build.
- Nobody silently duplicates work.
- Blockers are visible early.
- Demo-critical work stays prioritized.
- Judges see a professional, understandable repo.

## Issue Philosophy

Issues are not bureaucracy. They are the project’s task map.

Every issue should be:

- Small enough to finish quickly.
- Clear enough that another teammate can understand it.
- Connected to a milestone.
- Labeled by area and priority.
- Assigned to one owner when actively being worked.

## Issue Title Format

Use this format:

```txt
[Area] Action-focused task name
```

Examples:

```txt
[Frontend] Build war room layout shell
[Band] Create collaboration provider interface
[Agent] Define commander agent structured output
[Demo] Add API key exposure sample incident files
[Report] Build final audit report page
[Docs] Update README with local setup commands
[Pitch] Draft 3-minute demo script
```

## Issue Body Format

Every issue should answer:

```md
## Goal
What should be true when this is done?

## Why It Matters
How does this help the project win or stay stable?

## Scope
What should be included?

## Out of Scope
What should not be touched?

## Acceptance Criteria
- [ ] Specific measurable outcome
- [ ] Specific measurable outcome
- [ ] Specific measurable outcome

## Dependencies
Blocked by or related to any other issue?

## Notes
Any implementation details, links, or warnings.
```

## Priority Labels

Use these labels carefully.

### `priority:P0`

Demo-critical. If this is not done, the project may not work or may not be understandable.

Examples:

- War Room page does not render.
- Band messages are not visible.
- Sample incident cannot run.
- Final report is missing.
- Submission README is unclear.

### `priority:P1`

Important. Strongly improves the demo or judging score, but the project can technically function without it.

Examples:

- Replay mode polish.
- Better evidence cards.
- Improved agent prompt quality.
- Better report formatting.

### `priority:P2`

Nice-to-have. Do only after P0 and P1 work.

Examples:

- Extra incident scenario.
- Additional animation.
- Optional Slack/Jira mock integration.
- Secondary model provider.

## Area Labels

Use one or more area labels.

```txt
area:frontend        Next.js pages, components, UI state
area:band            Band SDK/API integration, rooms, messages, agents
area:agents          Agent prompts, runners, structured outputs
area:demo-data       Sample logs, mock incident, seeded demo data
area:schemas         Shared types, contracts, message objects
area:reporting       Final report, audit replay, timeline generation
area:docs            README, architecture, pitch, onboarding docs
area:submission      lablab submission content, video, slides
area:ui-polish       Visual polish only
area:devops          Vercel, scripts, CI, environment setup
```

## Type Labels

```txt
type:feature       New behavior or product surface
type:bug           Broken behavior
type:docs          Documentation work
type:chore         Config, cleanup, repo management
type:decision      Decision needed from team
type:research      Need to verify docs, API, or approach
type:demo          Demo flow, sample data, video support
```

## Status Labels

```txt
status:ready        Ready to work
status:in-progress  Someone is actively working
status:blocked      Cannot continue without input/help
status:needs-review Needs review or testing
status:done         Finished, usually not necessary if issue is closed
```

## Risk Labels

```txt
risk:demo-critical       Affects the final demo path
risk:security-sensitive  Could touch secrets, credentials, or unsafe data
risk:integration         Depends on external API or runtime behavior
risk:large-change        Many files or broad architecture change
```

## Recommended Label Colors

These are optional, but make the repo easier to scan.

| Label | Color |
|---|---|
| `priority:P0` | `b60205` |
| `priority:P1` | `d93f0b` |
| `priority:P2` | `fbca04` |
| `area:frontend` | `1d76db` |
| `area:band` | `5319e7` |
| `area:agents` | `0052cc` |
| `area:demo-data` | `0e8a16` |
| `area:schemas` | `006b75` |
| `area:reporting` | `7057ff` |
| `area:docs` | `0075ca` |
| `area:submission` | `c5def5` |
| `area:ui-polish` | `bfd4f2` |
| `area:devops` | `d4c5f9` |
| `type:feature` | `a2eeef` |
| `type:bug` | `d73a4a` |
| `type:docs` | `0075ca` |
| `type:chore` | `ffffff` |
| `type:decision` | `fef2c0` |
| `type:research` | `e4e669` |
| `type:demo` | `c2e0c6` |
| `status:ready` | `0e8a16` |
| `status:in-progress` | `fbca04` |
| `status:blocked` | `b60205` |
| `status:needs-review` | `5319e7` |
| `risk:demo-critical` | `ff0000` |
| `risk:security-sensitive` | `8b0000` |
| `risk:integration` | `d4c5f9` |
| `risk:large-change` | `f9d0c4` |

## Milestone Plan

### M0 — Repo Ready

Purpose:

Set up the repo so the team can work safely.

Includes:

- Repo created
- README updated
- GitHub templates added
- First issues created
- Branch rules defined
- Team roles confirmed

Exit criteria:

- Every teammate can clone and run the baseline.
- Every teammate knows their first issue.

### M1 — Mock Demo Vertical Slice

Purpose:

Build the full demo without depending on live APIs.

Includes:

- War Room UI
- Sample incident state
- Message stream
- Agent roster
- Evidence board
- Timeline
- Human approval gate
- Report preview
- Replay mode

Exit criteria:

- User can click “Run Demo Incident.”
- The full story plays from incident open to final report.
- The app remains demoable even if Band is unavailable.

### M2 — Band Collaboration Connected

Purpose:

Make real Band usage central to the workflow.

Includes:

- Collaboration provider interface
- Band provider implementation
- Band room creation
- Agent registration
- Structured messages through Band
- At least 3 agents collaborating through Band

Exit criteria:

- Real Band messages appear in the War Room.
- Band is used during the workflow, not only afterward.

### M3 — Agent Intelligence and Structured Handoffs

Purpose:

Make the agents feel specialized and useful.

Includes:

- Commander orchestration
- Forensics findings
- Threat Intel confidence assessment
- Code Review root-cause hypothesis
- Risk & Compliance challenge
- Remediation tasks
- Human approval request

Exit criteria:

- Agents produce structured messages.
- At least one agent challenge/disagreement appears.
- Handoffs are visible and meaningful.

### M4 — Demo Polish and Submission

Purpose:

Prepare the final hackathon package.

Includes:

- Polished UI
- Final report design
- Audit replay polish
- README finalization
- Architecture diagram
- 3-minute demo video
- Slide deck or pitch notes
- Submission text

Exit criteria:

- Hosted app works.
- Repo is public.
- Video explains the project clearly.
- The submission tells the Band story directly.

## Issue Assignment Rules

Each active issue should have one primary owner.

Good:

```txt
Owner: Jordan
Reviewer: Caleb
Pairing help: Sam if Band messages fail
```

Bad:

```txt
Everyone work on this
```

For team speed, one issue can have helpers, but one person owns finishing it.

## Blocking Rules

If an issue is blocked for more than 30 minutes, mark it `status:blocked` and post:

```txt
Blocked by:
What I tried:
What I need:
Best next option:
```

Do not silently struggle for hours during a hackathon.

## Demo-Critical Rule

Any issue labeled `risk:demo-critical` gets priority over all polish.

Examples:

- App will not run.
- War Room breaks.
- Sample incident cannot replay.
- Report cannot render.
- Band messages do not show and mock fallback is broken.

## Suggested First Board

```txt
Backlog:
- Optional features and polish ideas

Ready:
- Clear tasks with no blockers

In Progress:
- Tasks being actively built

Needs Review:
- PR open or ready for someone to test

Blocked:
- Needs help or decision

Done:
- Merged or completed
```

## Do Not Create These Issues Yet

Avoid distracting work early:

```txt
Add login/auth
Add user accounts
Add real SIEM integration
Add multiple customers
Add payments
Add mobile app
Add browser extension
Add production-grade database
Add complex admin dashboard
```

These are not needed to win the hackathon.

## Issue System Success Criteria

This system is working if:

- The team knows what matters most.
- The repo shows clear momentum.
- The final README can point to completed issues/milestones.
- Nobody has to ask “what should I do next?”
- Demo-critical work is obvious.
