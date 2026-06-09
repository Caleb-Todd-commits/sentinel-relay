# Step 6 UI Component Inventory

## Command and framing

### `WarRoomCommandBar`

Shows the incident command summary:

- demo mode,
- case ID,
- approval state,
- severity,
- status,
- active agents,
- visible messages.

This gives the demo a command-center feel and keeps the current state visible while scrolling.

### `JudgeBriefingPanel`

Explains the project from the judge's perspective:

- Band is central,
- agents have real roles,
- agents can disagree,
- output is audit-ready.

This is intentionally explicit. Judges may only spend a short amount of time with the app, so the app should explain itself.

### `CriticalMomentCard`

Spotlights the strongest demo sequence:

```txt
Evidence emerges → Risk challenges → Human gate opens → Scoped approval
```

This prevents the most important proof from being buried in the message stream.

## Coordination visibility

### `CollaborationMap`

Shows agents as participants in a shared workflow and reveals handoffs as the mock incident progresses.

### `MessageStream`

The main Band-style collaboration stream. It now shows:

- message sequence,
- sender,
- message type,
- severity,
- confidence,
- visibility,
- structured payload summary,
- payload details,
- decision impact,
- target agents,
- evidence references,
- correlation ID,
- next action.

### `AuditReplayPanel`

A compact trace of visible messages. This should become the bridge to the final audit report and future replay mode.

## Control and state

### `WorkflowControls`

The main manual demo driver. It now includes:

- mode label,
- category label,
- progress,
- step markers,
- current judge callout,
- current Band proof,
- start/next/approval/complete/replay actions.

### `StateMachinePanel`

Shows workflow state:

- status,
- phase,
- open approval requests,
- unresolved challenges,
- next unlock.

## Decision artifacts

### `ApprovalGate`

Shows the enterprise safety pause, risks, approver, and scoped decision.

### `EvidenceBoard`

Shows visible evidence, source, location, confidence, sensitivity, excerpts, and limitations.

### `TimelinePanel`

Shows the chronological incident record as evidence and messages unlock.

### `DecisionPanel`

Shows pending, approved, deferred, and locked decisions.

### `RemediationList`

Shows which fixes are blocked or unlocked by the approval gate.

### `ReportPreview`

Shows report readiness and final report CTA.
