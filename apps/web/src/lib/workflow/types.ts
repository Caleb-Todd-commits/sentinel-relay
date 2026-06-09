import type {
  AgentMessage,
  AgentProfile,
  ApprovalDecision,
  ApprovalRequest,
  DecisionGate,
  EvidenceReference,
  FinalReport,
  IncidentCase,
  IncidentPhase,
  IncidentStateSnapshot,
  IncidentStatus,
  RemediationTask,
  Severity,
  TimelineEvent,
} from "@/lib/types";
import type { CollaborationProviderHealth, CollaborationRoomSnapshot } from "@/lib/collaboration";

export type WorkflowApprovalState = "hidden" | "pending" | "approved";
export type WorkflowRunMode = "manual" | "completed";

export type WorkflowStepCategory =
  | "setup"
  | "room"
  | "assignment"
  | "evidence"
  | "verification"
  | "challenge"
  | "approval"
  | "remediation"
  | "report";

export type WorkflowStepDefinition = {
  /**
   * Step zero is the pre-run state. Step N unlocks message sequence N.
   */
  stepIndex: number;
  category: WorkflowStepCategory;
  title: string;
  shortLabel: string;
  description: string;
  messageId?: string;
  phase: IncidentPhase;
  status: IncidentStatus;
  severity: Severity;
  decisionGate: DecisionGate;
  activeAgentIds: string[];
  completedAgentIds: string[];
  waitingAgentIds: string[];
  blockedAgentIds: string[];
  visibleEvidenceIds: string[];
  visibleTaskIds: string[];
  unresolvedChallengeIds: string[];
  openApprovalRequestIds: string[];
  judgeCallout: string;
  bandProof: string;
};

export type WorkflowHandoff = {
  id: string;
  fromAgentId: string;
  toAgentId: string;
  title: string;
  summary: string;
  visibleAtStep: number;
  evidenceIds: string[];
  status: "locked" | "visible" | "complete";
};

export type WorkflowDecision = {
  id: string;
  title: string;
  summary: string;
  owner: string;
  status: "locked" | "pending" | "approved" | "deferred";
  visibleAtStep: number;
  resolvedAtStep?: number;
};

export type WorkflowCollaborationState = {
  providerMode: "mock" | "band";
  providerHealth: CollaborationProviderHealth;
  roomId?: string;
  syncStatus: "initializing" | "syncing" | "ready" | "error";
  lastSyncedStep: number;
  error?: string;
  snapshot?: CollaborationRoomSnapshot;
  auditEventCount: number;
  registeredAgentCount: number;
};

export type WorkflowViewModel = {
  case: IncidentCase;
  state: IncidentStateSnapshot;
  stepIndex: number;
  totalSteps: number;
  progressPercent: number;
  currentStep: WorkflowStepDefinition;
  nextStep?: WorkflowStepDefinition;
  previousStep?: WorkflowStepDefinition;
  messages: AgentMessage[];
  evidence: EvidenceReference[];
  lockedEvidenceCount: number;
  timeline: TimelineEvent[];
  agents: AgentProfile[];
  approvalState: WorkflowApprovalState;
  approvalRequest?: ApprovalRequest;
  approvalDecision?: ApprovalDecision;
  remediationTasks: RemediationTask[];
  lockedTaskCount: number;
  finalReport: FinalReport;
  reportReady: boolean;
  handoffs: WorkflowHandoff[];
  decisions: WorkflowDecision[];
  isAtStart: boolean;
  isAtApprovalGate: boolean;
  isComplete: boolean;
  canAdvance: boolean;
  canApprove: boolean;
  canReplay: boolean;
  canComplete: boolean;
  modeLabel: string;
  collaboration?: WorkflowCollaborationState;
};
