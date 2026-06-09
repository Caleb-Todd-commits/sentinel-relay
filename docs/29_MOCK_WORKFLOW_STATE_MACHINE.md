# Mock Workflow State Machine

The mock flow uses a small state machine instead of hardcoded page flags. This keeps the demo stable and makes the future Band integration easier.

## Source of truth

The workflow state lives in:

```txt
apps/web/src/lib/workflow/mockWorkflowScript.ts
```

Each `WorkflowStepDefinition` defines:

- step index
- category
- title
- description
- linked message ID
- incident phase
- incident status
- severity
- decision gate
- active agents
- completed agents
- waiting agents
- blocked agents
- visible evidence IDs
- visible remediation task IDs
- unresolved challenge IDs
- open approval request IDs
- judge callout
- Band proof explanation

## Derived state

The UI does not manually decide what to show. It calls:

```ts
deriveWorkflowViewModel(stepIndex)
```

That function returns the complete War Room view model:

- current incident case state
- visible messages
- visible evidence
- visible timeline events
- agent statuses
- approval gate state
- visible remediation tasks
- decision board
- handoff board
- report readiness
- button states

## Approval gate behavior

Step 7 is special.

At step 7:

- approval request is visible
- remediation is blocked
- `Run next step` is disabled
- `Approve containment` is enabled

When the user clicks **Approve containment**, the workflow advances to step 8, revealing the approval decision. This is deliberate because the demo must show that high-impact actions do not execute automatically.

## Report readiness

The final report is locked until step 10.

This reinforces the audit story: the report is generated from the complete message stream, not invented at the beginning.

## Why this matters for Band

When real Band messages are connected later, the frontend should not need a major rewrite. The real provider should emit the same structured objects that the mock workflow currently derives.
