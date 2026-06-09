# Step 5 — Mock Incident Flow

Step 5 turns the static baseline into a staged, replayable incident workflow. The goal is to make the demo strong even before live Band credentials, hosted agents, or model calls are connected.

## Purpose

The mock incident flow is not fake filler. It is the product contract that the real Band integration must satisfy later.

The mock flow proves:

- The War Room can show a full incident from intake to report.
- Agent messages appear in a clear sequence.
- Evidence unlocks only when relevant agent findings appear.
- Agent status changes as the workflow progresses.
- Risk & Compliance can challenge another agent's conclusion.
- Human approval blocks remediation until the decision is recorded.
- The final report is unlocked only after the audit trail is complete.

## Canonical scenario

**Possible API Key Exposure After Friday Deploy**

A SaaS company detects abnormal API usage shortly after a Friday deployment. The team must determine whether an API token was exposed, whether customer impact is proven, what containment actions require approval, and what remediation should happen.

## Workflow sequence

| Step | Event | Why it matters |
|---|---|---|
| 0 | Demo staged and ready | Shows the system is stable before any external dependency. |
| 1 | Band incident room opened | Makes Band the shared coordination layer from the start. |
| 2 | Specialist tasks assigned | Shows role separation and task handoff. |
| 3 | Suspicious token usage identified | Adds evidence-backed log analysis. |
| 4 | Indicator confidence qualified | Prevents overclaiming from weak threat indicators. |
| 5 | Recent diff likely exposed token material | Connects runtime anomaly to code/config review. |
| 6 | Risk challenges customer-impact claim | Demonstrates agent disagreement and high-stakes review. |
| 7 | Human approval requested | Blocks production action until a human decision. |
| 8 | Containment approved, disclosure deferred | Records scoped human approval. |
| 9 | Containment and fix plan prepared | Unlocks remediation only after approval. |
| 10 | Audit-ready report generated | Produces final output from the collaboration trail. |

## Files added

```txt
apps/web/src/lib/workflow/types.ts
apps/web/src/lib/workflow/mockWorkflowScript.ts
apps/web/src/lib/workflow/deriveWorkflowState.ts
apps/web/src/lib/workflow/useMockIncidentWorkflow.ts
apps/web/src/lib/workflow/index.ts
apps/web/src/components/war-room/WorkflowControls.tsx
apps/web/src/components/war-room/StateMachinePanel.tsx
apps/web/src/components/war-room/HandoffPanel.tsx
apps/web/src/components/war-room/DecisionPanel.tsx
```

## Files upgraded

```txt
apps/web/src/app/war-room/page.tsx
apps/web/src/components/MessageStream.tsx
apps/web/src/components/AgentRoster.tsx
apps/web/src/components/ApprovalGate.tsx
apps/web/src/components/EvidenceBoard.tsx
apps/web/src/components/war-room/IncidentHeader.tsx
apps/web/src/components/war-room/RemediationList.tsx
apps/web/src/lib/collaboration/CollaborationProvider.ts
apps/web/src/lib/collaboration/MockCollaborationProvider.ts
apps/web/src/lib/collaboration/BandCollaborationProvider.ts
```

## Design principle

The mock workflow is deterministic. That is intentional.

For the final hackathon demo, reliability beats randomness. The judges should see the perfect story every time:

1. A high-stakes case opens.
2. Specialists contribute evidence.
3. One agent challenges unsupported conclusions.
4. A human approval gate controls production action.
5. Remediation follows the approved scope.
6. A traceable report appears.

## What should not be added yet

Do not add live SOC integrations, random incident generation, real customer data, or autonomous production actions. Those would weaken stability and distract from the core Band collaboration proof.
