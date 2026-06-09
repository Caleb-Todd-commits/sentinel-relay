# Step 6 — War Room UI System

## Purpose

Step 6 turns the mocked workflow from a functional demo into a judge-readable command center. The goal is not decorative polish. The goal is to make the core hackathon proof visible in seconds:

> Specialized agents coordinate through a shared Band-style room, challenge each other, request human approval, and produce an audit-ready incident record.

## What changed

The War Room now has a stronger visual hierarchy:

1. **Command bar** — persistent high-level state for the incident.
2. **Incident header** — case identity, severity, status, and decision gate.
3. **Judge briefing panel** — explains why this is a Band-native multi-agent workflow.
4. **Workflow controls** — manual demo driver with progress and current step.
5. **Critical moment spotlight** — highlights the challenge/approval/remediation sequence.
6. **Collaboration map** — shows agents and handoffs as a visible coordination graph.
7. **State and agents rail** — current workflow state, roster, and handoff list.
8. **Band collaboration stream** — structured message cards with payload details.
9. **Approval gate** — enterprise safety checkpoint.
10. **Audit replay trail** — compact record of messages that can become the final report.
11. **Evidence/output rail** — decisions, evidence, timeline, remediation, and report preview.

## New components

```txt
apps/web/src/components/war-room/WarRoomCommandBar.tsx
apps/web/src/components/war-room/JudgeBriefingPanel.tsx
apps/web/src/components/war-room/CriticalMomentCard.tsx
apps/web/src/components/war-room/CollaborationMap.tsx
apps/web/src/components/war-room/AuditReplayPanel.tsx
apps/web/src/components/war-room/WarRoomSectionHeader.tsx
```

## Upgraded components

```txt
apps/web/src/app/war-room/page.tsx
apps/web/src/components/MessageStream.tsx
apps/web/src/components/AgentRoster.tsx
apps/web/src/components/EvidenceBoard.tsx
apps/web/src/components/TimelinePanel.tsx
apps/web/src/components/ApprovalGate.tsx
apps/web/src/components/war-room/WorkflowControls.tsx
apps/web/src/app/globals.css
```

## Design principles

### 1. Judge-readable before feature-rich

A judge should understand the product before reading the README. The page now puts the thesis up front:

- this is a high-stakes incident workflow,
- agents have specialized responsibilities,
- Band-style coordination is visible,
- disagreement and approval are first-class events,
- the final artifact is traceable.

### 2. Coordination must be visible

The UI shows handoffs, targets, evidence references, payload details, correlation IDs, and decision impact. This matters because the project should not look like a single response generator.

### 3. The critical moment must be obvious

The Risk & Compliance challenge is the main differentiator. Step 6 gives it a dedicated spotlight and stronger message-card styling.

### 4. Safety is part of the product

The approval gate is designed as an enterprise control, not a formality. It clearly separates approved containment from unapproved customer notification.

### 5. Deterministic replay is an advantage

The mock flow is not framed as fake. It is framed as a deterministic Band-contract replay. That gives the team a reliable demo path while real Band integration is added later.

## Demo guidance

When presenting, do not click through too quickly. Let the judge see these moments:

1. Start incident.
2. Show room created and specialist agents registered.
3. Show Forensics evidence.
4. Show Code Review tying evidence to deployment diff.
5. Pause at Risk challenge.
6. Explain that the agent blocks overclaiming.
7. Approve containment.
8. Show that customer notification is still not approved.
9. Show remediation and report unlock.
10. Show audit replay trail.

## What this step intentionally does not do

- Does not connect real Band.
- Does not add live AI calls.
- Does not add authentication.
- Does not add a database.
- Does not introduce random workflows.

Step 6 is about making the existing workflow polished and understandable.
