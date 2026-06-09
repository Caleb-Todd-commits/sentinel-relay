import type { ConfidenceBand, Severity } from "./enums";

export type ISODateTimeString = string;
export type UUIDLike = string;
export type CaseId = string;
export type RoomId = string;
export type AgentId = string;
export type MessageId = string;
export type EvidenceId = string;
export type TaskId = string;
export type ApprovalRequestId = string;

export type ConfidenceScore = number;

export type EvidenceReferencePointer = {
  evidenceId: EvidenceId;
  source: string;
  location?: string;
};

export type RiskSignal = {
  id: string;
  label: string;
  severity: Severity;
  confidence: ConfidenceScore;
  confidenceBand: ConfidenceBand;
  rationale: string;
  evidenceIds: EvidenceId[];
};

export type FieldValidationIssue = {
  path: string;
  message: string;
  severity: "warning" | "error";
};

export type ValidationResult = {
  valid: boolean;
  issues: FieldValidationIssue[];
};
