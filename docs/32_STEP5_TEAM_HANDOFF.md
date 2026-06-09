# Step 5 Team Handoff

## What changed

The War Room is now driven by a mock incident workflow engine instead of simple static slicing.

The key new concept is the **workflow view model**. The UI receives one object that tells it exactly what to show at the current step.

## Files frontend teammates should know

```txt
apps/web/src/app/war-room/page.tsx
apps/web/src/lib/workflow/mockWorkflowScript.ts
apps/web/src/lib/workflow/deriveWorkflowState.ts
apps/web/src/lib/workflow/useMockIncidentWorkflow.ts
apps/web/src/components/war-room/WorkflowControls.tsx
apps/web/src/components/war-room/StateMachinePanel.tsx
apps/web/src/components/war-room/HandoffPanel.tsx
apps/web/src/components/war-room/DecisionPanel.tsx
```

## Files Band/backend teammates should know

```txt
apps/web/src/lib/collaboration/CollaborationProvider.ts
apps/web/src/lib/collaboration/MockCollaborationProvider.ts
apps/web/src/lib/collaboration/BandCollaborationProvider.ts
apps/web/src/lib/workflow/types.ts
```

## Files agent teammates should know

```txt
packages/schemas/src/messages.ts
packages/schemas/contracts/AGENT_OUTPUT_CONTRACT.md
apps/web/src/lib/workflow/mockWorkflowScript.ts
```

Agents eventually need to emit the same message types and payload shapes that the mock workflow is already displaying.

## Next build step

Step 6 is the War Room UI polish pass.

Recommended Step 6 work:

1. Improve responsive layout.
2. Add stronger visual hierarchy to message cards.
3. Add a clearer audit replay mode.
4. Add a compact judge mode.
5. Improve final report navigation.
6. Add skeleton/loading states.
7. Make the challenge and approval moments visually unforgettable.
