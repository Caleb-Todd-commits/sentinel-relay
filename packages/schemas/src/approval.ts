import type { ApprovalDecisionValue, ApprovalStatus, Severity } from "./enums";
import type { AgentId, ApprovalRequestId, CaseId, EvidenceId, ISODateTimeString } from "./primitives";

export type ApprovalRequest = {
  id: ApprovalRequestId;
  caseId: CaseId;
  requestedByAgentId: AgentId;
  action: string;
  reason: string;
  severity: Severity;
  evidenceIds: EvidenceId[];
  riskIfApproved: string;
  riskIfRejected: string;
  requiredApprover: string;
  status: ApprovalStatus;
  createdAt?: ISODateTimeString;
  expiresAt?: ISODateTimeString;
};

export type ApprovalDecision = {
  id: string;
  requestId: ApprovalRequestId;
  decision: ApprovalDecisionValue;
  decidedBy: string;
  rationale: string;
  decidedAt: ISODateTimeString;
  approvedActionScope: string[];
  explicitlyNotApproved: string[];
};
