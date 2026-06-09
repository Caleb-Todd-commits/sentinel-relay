# UI Component Inventory

## Current components

### `SiteHeader`

Global navigation and product identity. Used on all routes.

### `Badge`

Reusable status chip. Supports these tones:

- `neutral`
- `success`
- `warning`
- `danger`
- `accent`

### `MetricCard`

Reusable small metric card used in the incident header.

### `IncidentHeader`

Shows:

- case ID
- Band room ID
- title
- summary
- severity
- status
- affected system
- decision gate
- demo progress

### `AgentRoster`

Shows each agent with:

- short name
- role
- current status
- current task

### `MessageStream`

The most important component in the project.

Shows:

- sequence
- created time
- agent name
- message type
- severity
- confidence
- summary
- decision impact
- next action
- evidence chips

This is where the Band collaboration becomes judge-visible.

### `EvidenceBoard`

Shows evidence references with:

- title
- source file
- location
- summary
- excerpt
- confidence

### `TimelinePanel`

Shows the incident timeline as an audit-style sequence.

### `ApprovalGate`

Shows:

- requested action
- reason
- approver
- approval status
- human decision rationale

This should remain one of the highest-visibility UI elements because it proves enterprise safety.

### `RemediationList`

Shows remediation tasks with:

- task title
- owner agent
- status
- rationale

### `ReportPreview`

Shows whether the final report is locked or ready.

## Component rules

1. Components should receive typed props.
2. Components should not fetch external data directly yet.
3. Components should remain reusable when mock data is replaced by Band data.
4. Do not place business logic in visual components unless it is minor display logic.
5. Keep message rendering structured and evidence-backed.

## Next recommended UI additions

These should happen after the current baseline is running:

1. Auto-play replay mode with pause/resume.
2. Evidence filtering by selected message.
3. Agent activity highlighting when a message appears.
4. Report export styling.
5. More obvious Band room state indicator once real Band is connected.
