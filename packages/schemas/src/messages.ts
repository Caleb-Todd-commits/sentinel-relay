import type { AgentMessageType, MessageVisibility, Severity } from "./enums";
import type { AgentId, CaseId, ConfidenceScore, EvidenceId, ISODateTimeString, MessageId, RoomId, TaskId } from "./primitives";

export type AgentMessageBase = {
  id: MessageId;
  schemaVersion: string;
  caseId: CaseId;
  roomId: RoomId;
  sequence: number;
  agentId: AgentId;
  agentName: string;
  type: AgentMessageType;
  title: string;
  summary: string;
  confidence: ConfidenceScore;
  severity: Severity;
  evidenceIds: EvidenceId[];
  targetAgentIds?: AgentId[];
  createdAt: ISODateTimeString;
  visibility: MessageVisibility;
  decisionImpact?: string;
  nextAction?: string;
  correlationId?: string;
};

export type FindingPayload = {
  claim: string;
  supportingEvidenceIds: EvidenceId[];
  contradictingEvidenceIds: EvidenceId[];
  limitations: string[];
  requestedVerifications: string[];
};

export type ChallengePayload = {
  challengedMessageId: MessageId;
  reason: string;
  requiredNextStep: string;
  blocking: boolean;
  suggestedOwnerAgentId?: AgentId;
};

export type RiskAssessmentPayload = {
  currentRisk: Severity;
  recommendedSeverity: Severity;
  escalationRequired: boolean;
  rationale: string;
  requiredApprovals: string[];
};

export type TaskAssignmentPayload = {
  taskId: TaskId;
  assignedToAgentId: AgentId;
  objective: string;
  expectedOutput: string;
  acceptanceCriteria: string[];
};

export type HandoffPayload = {
  fromAgentId: AgentId;
  toAgentId: AgentId;
  reason: string;
  contextSummary: string;
  evidenceIds: EvidenceId[];
};

export type AgentMessagePayload =
  | { kind: "finding"; data: FindingPayload }
  | { kind: "challenge"; data: ChallengePayload }
  | { kind: "risk_assessment"; data: RiskAssessmentPayload }
  | { kind: "task_assignment"; data: TaskAssignmentPayload }
  | { kind: "handoff"; data: HandoffPayload }
  | { kind: "generic"; data: Record<string, unknown> };

export type AgentMessage = AgentMessageBase & {
  payload?: AgentMessagePayload;
};

export type BandEnvelope = {
  schemaVersion: string;
  envelopeType: "sentinel_relay.agent_message";
  caseId: CaseId;
  roomId: RoomId;
  senderAgentId: AgentId;
  messageId: MessageId;
  sentAt: ISODateTimeString;
  traceId: string;
  payload: AgentMessage;
};
