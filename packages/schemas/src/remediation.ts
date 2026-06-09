import type { Severity, TaskStatus } from "./enums";
import type { AgentId, EvidenceId, TaskId } from "./primitives";

export type RemediationTask = {
  id: TaskId;
  title: string;
  ownerAgentId: AgentId;
  status: TaskStatus;
  severity: Severity;
  rationale: string;
  evidenceIds: EvidenceId[];
  acceptanceCriteria: string[];
  rollbackPlan?: string;
  testPlan?: string[];
};

export type RemediationPlan = {
  caseId: string;
  summary: string;
  tasks: RemediationTask[];
  blockedByApprovalRequestIds: string[];
};
