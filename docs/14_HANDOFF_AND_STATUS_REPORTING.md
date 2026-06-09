# 14 — Handoff and Status Reporting

## Purpose

This document defines how teammates should hand work to each other and report progress. A hackathon team loses time when someone finishes a branch but nobody knows what changed, how to test it, or what still needs work.

The goal is clean handoffs.

## Standard Status Update

Use this in group chat or GitHub issue comments:

```txt
Status:
Finished:
Working next:
Blocked:
Branch/PR:
How to test:
Need from team:
```

Example:

```txt
Status: War Room shell is mostly done.
Finished: Header, agent roster, message stream layout.
Working next: Evidence board and approval card.
Blocked: Need final message schema from agent side.
Branch/PR: feature/war-room-shell
How to test: cd apps/web && pnpm dev, then open /war-room
Need from team: Confirm if Challenge should be its own message type or a Finding subtype.
```

## Pull Request Handoff

Every PR should include:

```txt
What changed:
Why:
How to test:
Known limitations:
Screenshots/video:
Follow-up issues:
```

## End-of-Session Handoff

If you stop working and someone else may continue, write:

```txt
Branch:
Last good state:
Files changed:
What is complete:
What is incomplete:
Known errors:
Next best step:
Do not touch:
```

## Demo Lead Status Template

Use this for final sprint tracking:

```txt
Demo status:
App runs locally: yes/no
Hosted app works: yes/no
Mock incident works: yes/no
Band mode works: yes/no/partial
Final report works: yes/no
Video recorded: yes/no
README final: yes/no
Submission copy final: yes/no
Biggest risk:
Next action:
```

## Blocker Escalation

If blocked, post:

```txt
Blocked on:
Impact:
What I tried:
Error/output:
Decision needed:
Suggested path:
```

Example:

```txt
Blocked on: Band WebSocket auth.
Impact: Real Band messages not showing in UI.
What I tried: Created room, registered agent, checked env vars.
Error/output: 401 on subscribe endpoint.
Decision needed: Do we keep debugging or switch to mock mode for video while backend continues?
Suggested path: Keep mock mode stable, continue Band integration on separate branch.
```

## Decision Log Update

When the team makes a major decision, update:

```txt
docs/06_DECISION_LOG.md
```

Examples of decisions worth logging:

- Track choice.
- Main scenario change.
- Stack change.
- Whether to use `dev` branch.
- Whether to cut a feature.
- Whether to rely on live Band or mock replay for video.

## What Not To Do

Avoid vague updates:

```txt
Working on stuff.
Almost done.
It is broken.
Pushed some changes.
```

Better:

```txt
I pushed the message stream component. It renders mock messages and supports Finding, Challenge, ApprovalRequest, and RemediationTask. It does not yet subscribe to Band. Test at /war-room on branch feature/message-stream.
```

## Handoff Success Criteria

A handoff is good if another teammate can continue without asking basic questions.

They should know:

- Which branch to pull.
- What changed.
- How to test.
- What is still broken.
- What to do next.
