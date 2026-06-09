# 10 — Team Execution Protocol

## Purpose

This document defines how the team should work together once the GitHub repo is live. Sentinel Relay needs multiple people building different pieces at once. The team can move fast only if responsibilities, communication, and merge behavior are clear.

This protocol is designed for a one-week hackathon with approximately five people.

## Operating Principle

The project should always have one working demo path.

Everything else serves that.

The working demo path is:

```txt
Start sample incident
→ War Room opens
→ agent messages appear
→ evidence and timeline update
→ human approval appears
→ remediation tasks appear
→ final report renders
→ audit replay works
```

If a change improves an internal detail but risks breaking that path, it should wait or be isolated behind a flag/fallback.

## Team Roles

### 1. Product / Cybersecurity / Pitch Lead

Primary owner:

```txt
Caleb
```

Responsibilities:

- Keep the project aligned with the winning story.
- Own the cybersecurity scenario.
- Decide what is in scope and out of scope.
- Make sure the Band usage is central and visible.
- Review final demo flow.
- Own the judge pitch and submission language.

Main files:

```txt
docs/01_PROJECT_VISION_LOCK.md
docs/03_JUDGE_PITCH_AND_POSITIONING.md
docs/demo-script.md
docs/judging-notes.md
docs/status/
```

### 2. Frontend / War Room Lead

Responsibilities:

- Build the main Next.js app.
- Own `/war-room`.
- Build the agent roster, message stream, evidence board, timeline, approval gate, and report preview.
- Keep the UI judge-readable.
- Preserve mock mode.

Main files:

```txt
apps/web/src/app/
apps/web/src/components/
apps/web/src/lib/mockIncident.ts
apps/web/src/lib/types.ts
```

### 3. Band / Backend Integration Lead

Responsibilities:

- Own the collaboration provider abstraction.
- Connect real Band room creation and messages.
- Keep Band usage meaningful.
- Make sure fallback mock mode survives.
- Document required env vars.

Main files:

```txt
apps/web/src/lib/collaboration/
agents/
.env.example
docs/architecture.md
```

### 4. Agent Logic Lead

Responsibilities:

- Write agent prompts.
- Define structured outputs.
- Make agent responsibilities distinct.
- Ensure agents hand off work and challenge weak findings.
- Make outputs consistent with shared schemas.

Main files:

```txt
agents/*/prompt.md
agents/*/main.py
packages/schemas/message-contract.md
apps/web/src/lib/types.ts
```

### 5. Demo Data / Docs / Submission Lead

Responsibilities:

- Build realistic sample incident files.
- Ensure demo scenario is understandable.
- Own final README polish.
- Help produce demo video, slide deck, screenshots, and submission text.

Main files:

```txt
packages/sample-data/
docs/demo-script.md
docs/judging-notes.md
README.md
```

## Work Session Rhythm

Use short, visible updates.

At the start of each work block, post:

```txt
Working on: <issue number + task>
Branch: <branch name>
Goal: <what will be true when done>
Need from team: <anything blocking>
```

At the end of each work block, post:

```txt
Finished:
Changed files:
How to test:
PR/branch:
Blocked or next:
```

## Daily Team Checkpoint

Use this format once per day or major work session:

```txt
1. What is working right now?
2. What is broken or risky?
3. What must be done next for the demo?
4. What are we cutting?
5. Who owns each next task?
```

Do not spend long debating optional features while demo-critical tasks are unfinished.

## Decision-Making Rules

### Caleb decides product direction.

Examples:

- What scenario to demo.
- Whether to stay Track 3.
- What the judge pitch emphasizes.
- What features should be cut.

### Workstream leads decide implementation details within their area.

Examples:

- Component structure.
- Agent prompt format.
- Provider interface details.
- File organization.

### Team decides risky architecture changes together.

Examples:

- Adding a database.
- Replacing Next.js structure.
- Replacing Python agent approach.
- Removing mock fallback.
- Changing the main demo scenario.

## The 30-Minute Blocker Rule

If you are stuck for 30 minutes:

1. Stop digging alone.
2. Write what happened.
3. Post the blocker.
4. Ask for help or switch tasks.

Blocker format:

```txt
Blocked on:
What I tried:
Current error/result:
Likely cause:
Need:
```

## Demo Freeze Rule

During the last 24–36 hours:

- No major architecture rewrites.
- No new required external service unless already proven.
- No changes that remove the mock demo fallback.
- No huge PRs without review.
- No optional features before final video/script are done.

Allowed during freeze:

- UI polish.
- Bug fixes.
- Copy improvements.
- Report formatting.
- Demo video improvements.
- README/submission cleanup.

## Communication Channels

Recommended setup:

```txt
Group chat: fast updates and decisions
GitHub Issues: task ownership and history
Pull Requests: code review and merge discussion
README/docs: final source of truth
```

Do not let important technical decisions live only in group chat. If a decision changes the project, write it in:

```txt
docs/06_DECISION_LOG.md
```

## Review Expectations

When reviewing a PR, check:

- Does it help the main demo?
- Does the app still run?
- Does it preserve mock fallback?
- Are secrets avoided?
- Is the code understandable?
- Are types and schemas still consistent?
- Does this make Band usage more visible or less visible?

Review comments should be direct and practical.

Good comment:

```txt
This works, but it makes the message stream depend on Band mode only. Please keep mock fallback so the demo still runs without credentials.
```

Bad comment:

```txt
This feels weird.
```

## Pairing Rules

Pair when:

- Band connection is failing.
- UI and provider state need to connect.
- Agent output schema changes affect frontend.
- A demo-critical bug appears.

Do not pair on everything. Too much pairing slows the team.

## Handoff Rules

Every handoff should include:

```txt
What is done:
What is not done:
How to run/test:
Known problems:
Files to inspect:
Next recommended task:
```

This matters because people will be working at different times.

## File Ownership Map

| File/Folder | Primary Owner |
|---|---|
| `apps/web/src/app/war-room` | Frontend lead |
| `apps/web/src/components` | Frontend lead |
| `apps/web/src/lib/collaboration` | Band/backend lead |
| `apps/web/src/lib/types.ts` | Frontend + agent logic lead |
| `packages/schemas` | Agent logic lead |
| `packages/sample-data` | Demo/data lead |
| `agents` | Agent logic + Band lead |
| `docs/judging-notes.md` | Caleb |
| `docs/demo-script.md` | Caleb + demo lead |
| `README.md` | Caleb + docs lead |

## Cut List Protocol

If time gets tight, cut in this order:

1. Extra incident scenarios.
2. Extra animations.
3. Optional model provider comparisons.
4. Slack/Jira mock integrations.
5. GitHub mock PR generation.
6. Advanced filtering/search.
7. Login/auth.
8. Database persistence.

Do not cut:

- War Room.
- Structured messages.
- Agent handoffs.
- Human approval.
- Final report.
- Demo script.
- Mock fallback.

## Definition of Team Alignment

The team is aligned when every person can answer:

1. What are we building?
2. Why does Band matter?
3. What is my first task?
4. What branch am I using?
5. What is the demo path?
6. What should not be built yet?

If anyone cannot answer these, send them to:

```txt
docs/TEAM_START_HERE.md
docs/01_PROJECT_VISION_LOCK.md
docs/08_GITHUB_REPO_AND_BRANCH_RULES.md
```
