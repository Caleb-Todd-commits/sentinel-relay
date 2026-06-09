import type { DecisionGate, IncidentPhase, IncidentStatus, Severity } from "./enums";
import type { CaseId, ISODateTimeString, RoomId } from "./primitives";

export type IncidentCase = {
  id: CaseId;
  roomId: RoomId;
  title: string;
  summary: string;
  severity: Severity;
  status: IncidentStatus;
  openedAt: ISODateTimeString;
  updatedAt: ISODateTimeString;
  businessUnit: string;
  affectedSystem: string;
  currentPhase: string;
  phase: IncidentPhase;
  decisionGate: DecisionGate;
  owner?: string;
  tags: string[];
};

export type IncidentStateSnapshot = {
  caseId: CaseId;
  roomId: RoomId;
  status: IncidentStatus;
  severity: Severity;
  phase: IncidentPhase;
  decisionGate: DecisionGate;
  updatedAt: ISODateTimeString;
  activeAgentIds: string[];
  openApprovalRequestIds: string[];
  unresolvedChallengeIds: string[];
  openTaskIds: string[];
};
