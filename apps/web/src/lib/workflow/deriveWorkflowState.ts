import { sentinelRelayDemo } from "@/lib/demo/sentinelRelayDemo";
import type { AgentProfile, IncidentCase, RemediationTask } from "@/lib/types";
import { getWorkflowStep, mockWorkflowDecisions, mockWorkflowHandoffs, mockWorkflowSteps } from "./mockWorkflowScript";
import type { WorkflowApprovalState, WorkflowDecision, WorkflowHandoff, WorkflowViewModel } from "./types";

function unique<T>(values: T[]): T[] {
  return Array.from(new Set(values));
}

function visibleIdsFromMessages(stepIndex: number): string[] {
  return unique(
    sentinelRelayDemo.messages
      .filter((message) => message.sequence <= stepIndex)
      .flatMap((message) => message.evidenceIds),
  );
}

function deriveEvidenceIds(stepIndex: number): string[] {
  const step = getWorkflowStep(stepIndex);
  return unique([...step.visibleEvidenceIds, ...visibleIdsFromMessages(stepIndex)]);
}

function withAgentState(baseAgents: AgentProfile[], stepIndex: number): AgentProfile[] {
  const step = getWorkflowStep(stepIndex);

  return baseAgents.map((agent) => {
    if (step.completedAgentIds.includes(agent.id)) {
      return {
        ...agent,
        status: "complete",
        currentTask: agent.kind === "human_actor" ? "Decision recorded in the incident audit trail." : "Completed current workflow contribution.",
      } satisfies AgentProfile;
    }

    if (step.blockedAgentIds.includes(agent.id)) {
      return {
        ...agent,
        status: "blocked",
        currentTask: "Blocked until the human approval gate is resolved.",
      } satisfies AgentProfile;
    }

    if (step.waitingAgentIds.includes(agent.id)) {
      return {
        ...agent,
        status: "waiting",
        currentTask: "Waiting for upstream evidence or decision context.",
      } satisfies AgentProfile;
    }

    if (step.activeAgentIds.includes(agent.id)) {
      const status = step.category === "challenge" && agent.id === "agent-risk-compliance" ? "challenging" : "working";
      return {
        ...agent,
        status,
        currentTask: step.description,
      } satisfies AgentProfile;
    }

    return {
      ...agent,
      status: stepIndex === 0 ? "idle" : "assigned",
      currentTask: stepIndex === 0 ? "Ready for the incident room to open." : "Available for follow-up coordination.",
    } satisfies AgentProfile;
  });
}

function withRemediationState(tasks: RemediationTask[], visibleTaskIds: string[], approvalState: WorkflowApprovalState): RemediationTask[] {
  const visibleTaskIdSet = new Set(visibleTaskIds);

  return tasks
    .filter((task) => visibleTaskIdSet.has(task.id))
    .map((task) => {
      if (approvalState !== "approved") {
        return {
          ...task,
          status: "blocked",
          rationale: `${task.rationale} This remains blocked until containment approval is recorded.`,
        } satisfies RemediationTask;
      }

      if (task.id === "rem-001") {
        return { ...task, status: "done" } satisfies RemediationTask;
      }

      if (task.id === "rem-002") {
        return { ...task, status: "in_progress" } satisfies RemediationTask;
      }

      return { ...task, status: task.status === "blocked" ? "todo" : task.status } satisfies RemediationTask;
    });
}

function deriveHandoffs(stepIndex: number): WorkflowHandoff[] {
  return mockWorkflowHandoffs.map((handoff) => {
    if (stepIndex < handoff.visibleAtStep) {
      return { ...handoff, status: "locked" } satisfies WorkflowHandoff;
    }

    const status = stepIndex > handoff.visibleAtStep ? "complete" : "visible";
    return { ...handoff, status } satisfies WorkflowHandoff;
  });
}

function deriveDecisions(stepIndex: number): WorkflowDecision[] {
  return mockWorkflowDecisions.map((decision) => {
    if (stepIndex < decision.visibleAtStep) {
      return { ...decision, status: "locked" } satisfies WorkflowDecision;
    }

    if (decision.resolvedAtStep && stepIndex >= decision.resolvedAtStep) {
      return { ...decision, status: decision.id === "decision-003" ? "deferred" : "approved" } satisfies WorkflowDecision;
    }

    if (decision.id === "decision-003" && stepIndex >= 8) {
      return { ...decision, status: "deferred" } satisfies WorkflowDecision;
    }

    return { ...decision, status: "pending" } satisfies WorkflowDecision;
  });
}

function deriveApprovalState(stepIndex: number): WorkflowApprovalState {
  if (stepIndex >= 8) return "approved";
  if (stepIndex >= 7) return "pending";
  return "hidden";
}

export function deriveWorkflowViewModel(stepIndexInput: number): WorkflowViewModel {
  const totalSteps = mockWorkflowSteps.length - 1;
  const stepIndex = Math.max(0, Math.min(stepIndexInput, totalSteps));
  const currentStep = getWorkflowStep(stepIndex);
  const nextStep = stepIndex < totalSteps ? getWorkflowStep(stepIndex + 1) : undefined;
  const previousStep = stepIndex > 0 ? getWorkflowStep(stepIndex - 1) : undefined;
  const visibleEvidenceIds = deriveEvidenceIds(stepIndex);
  const visibleEvidenceIdSet = new Set(visibleEvidenceIds);
  const visibleTaskIds = currentStep.visibleTaskIds;
  const approvalState = deriveApprovalState(stepIndex);

  const caseState: IncidentCase = {
    ...sentinelRelayDemo.case,
    severity: currentStep.severity,
    status: currentStep.status,
    phase: currentStep.phase,
    decisionGate: currentStep.decisionGate,
    currentPhase: currentStep.title,
    updatedAt: sentinelRelayDemo.messages[Math.max(0, stepIndex - 1)]?.createdAt ?? sentinelRelayDemo.case.openedAt,
  };

  const messages = sentinelRelayDemo.messages.filter((message) => message.sequence <= stepIndex);
  const evidence = sentinelRelayDemo.evidence.filter((item) => visibleEvidenceIdSet.has(item.id));
  const timeline = sentinelRelayDemo.timeline.filter((event) => !event.sourceMessageId || messages.some((message) => message.id === event.sourceMessageId));
  const remediationTasks = withRemediationState(sentinelRelayDemo.remediationTasks, visibleTaskIds, approvalState);
  const reportReady = stepIndex >= totalSteps;

  return {
    case: caseState,
    state: {
      ...sentinelRelayDemo.state,
      status: currentStep.status,
      severity: currentStep.severity,
      phase: currentStep.phase,
      decisionGate: currentStep.decisionGate,
      updatedAt: caseState.updatedAt,
      activeAgentIds: currentStep.activeAgentIds,
      openApprovalRequestIds: currentStep.openApprovalRequestIds,
      unresolvedChallengeIds: currentStep.unresolvedChallengeIds,
      openTaskIds: currentStep.visibleTaskIds,
    },
    stepIndex,
    totalSteps,
    progressPercent: Math.round((stepIndex / totalSteps) * 100),
    currentStep,
    nextStep,
    previousStep,
    messages,
    evidence,
    lockedEvidenceCount: sentinelRelayDemo.evidence.length - evidence.length,
    timeline,
    agents: withAgentState(sentinelRelayDemo.agents, stepIndex),
    approvalState,
    approvalRequest: approvalState === "hidden" ? undefined : sentinelRelayDemo.approvalRequest,
    approvalDecision: approvalState === "approved" ? sentinelRelayDemo.approvalDecision : undefined,
    remediationTasks,
    lockedTaskCount: sentinelRelayDemo.remediationTasks.length - remediationTasks.length,
    finalReport: sentinelRelayDemo.finalReport,
    reportReady,
    handoffs: deriveHandoffs(stepIndex),
    decisions: deriveDecisions(stepIndex),
    isAtStart: stepIndex === 0,
    isAtApprovalGate: stepIndex === 7,
    isComplete: stepIndex >= totalSteps,
    canAdvance: stepIndex < totalSteps && stepIndex !== 7,
    canApprove: stepIndex === 7,
    canReplay: stepIndex > 0,
    canComplete: stepIndex < totalSteps,
    modeLabel: "Mock Mode · Band contract replay",
  };
}
