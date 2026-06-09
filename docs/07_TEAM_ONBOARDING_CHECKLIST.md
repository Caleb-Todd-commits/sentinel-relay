# 07 — Team Onboarding Checklist

Every teammate should read and complete this checklist before starting major work.

---

## Read First

1. `docs/01_PROJECT_VISION_LOCK.md`
2. `docs/02_PROJECT_CHARTER.md`
3. `docs/03_JUDGE_PITCH_AND_POSITIONING.md`
4. `docs/04_PRODUCT_BOUNDARIES_AND_NON_GOALS.md`
5. `docs/05_TERMINOLOGY.md`
6. `docs/06_DECISION_LOG.md`
7. `docs/01_BIGGEST_10_FIRST.md`

---

## Understand the Core Idea

You should be able to answer:

- What is Sentinel Relay?
- Why does it need multiple agents?
- Why is Band central?
- What is the main demo scenario?
- What does the human approve?
- What makes the final report traceable?

---

## 30-Second Team Explanation

Practice saying this:

> Sentinel Relay is a Band-powered incident command center for cybersecurity workflows. A company gets a suspicious alert, and specialized agents coordinate through Band to investigate logs, review code, assess threat confidence, challenge unsupported claims, request human approval, and generate an audit-ready report.

---

## Role Assignment

Each teammate should own one primary lane.

### Frontend

- War Room UI
- Landing page
- Demo page
- Report page
- Visual polish

### Band / Backend

- Collaboration provider
- Band room connection
- Agent message routing
- Provider fallback behavior

### Agent Logic

- Agent prompts
- Agent role boundaries
- Structured outputs
- Message schemas

### Demo Data / Docs

- Sample incident files
- Demo script
- README
- Architecture diagram
- Submission assets

### Product / Pitch

- Judging narrative
- Cybersecurity scenario accuracy
- Final video
- Slide structure

---

## Before Coding Checklist

- [ ] I know which part I own.
- [ ] I know the main scenario.
- [ ] I know what files I should not touch without discussion.
- [ ] I know the current branch plan.
- [ ] I know how to run the frontend locally.
- [ ] I understand that Band must be central.
- [ ] I understand that mock mode is allowed but not the final story.
- [ ] I will not commit secrets.

---

## Build Discipline

- Pull latest work before starting.
- Work in feature branches.
- Keep commits small and descriptive.
- Do not rewrite another teammate's area without checking.
- Prefer stable, readable code.
- Leave notes where integration is incomplete.
- Keep the app demoable after each major merge.

---

## Done Means

A task is not done because code exists.

A task is done when:

- It runs.
- It is understandable.
- It does not break the demo path.
- It supports the core Sentinel Relay story.
- It helps show Band-powered coordination.
