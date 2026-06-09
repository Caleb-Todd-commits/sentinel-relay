import { agentCapabilityValues, agentStatusValues, approvalDecisionValues, approvalStatusValues, collaborationModeValues, confidenceBandValues, decisionGateValues, evidenceKindValues, evidenceSensitivityValues, incidentPhaseValues, incidentStatusValues, messageTypeValues, reportSectionTypeValues, severityValues, taskStatusValues } from "./enums";
import type { ValidationResult } from "./primitives";

function includes<const T extends readonly string[]>(values: T, value: unknown): value is T[number] {
  return typeof value === "string" && (values as readonly string[]).includes(value);
}

export const isSeverity = (value: unknown) => includes(severityValues, value);
export const isIncidentStatus = (value: unknown) => includes(incidentStatusValues, value);
export const isIncidentPhase = (value: unknown) => includes(incidentPhaseValues, value);
export const isDecisionGate = (value: unknown) => includes(decisionGateValues, value);
export const isConfidenceBand = (value: unknown) => includes(confidenceBandValues, value);
export const isAgentStatus = (value: unknown) => includes(agentStatusValues, value);
export const isAgentCapability = (value: unknown) => includes(agentCapabilityValues, value);
export const isEvidenceKind = (value: unknown) => includes(evidenceKindValues, value);
export const isEvidenceSensitivity = (value: unknown) => includes(evidenceSensitivityValues, value);
export const isMessageType = (value: unknown) => includes(messageTypeValues, value);
export const isTaskStatus = (value: unknown) => includes(taskStatusValues, value);
export const isApprovalStatus = (value: unknown) => includes(approvalStatusValues, value);
export const isApprovalDecisionValue = (value: unknown) => includes(approvalDecisionValues, value);
export const isReportSectionType = (value: unknown) => includes(reportSectionTypeValues, value);
export const isCollaborationMode = (value: unknown) => includes(collaborationModeValues, value);

export function isIsoDateTime(value: unknown): value is string {
  return typeof value === "string" && !Number.isNaN(Date.parse(value));
}

export function isConfidenceScore(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 1;
}

export function validateRequiredString(record: Record<string, unknown>, path: string, key: string, result: ValidationResult): void {
  if (typeof record[key] !== "string" || record[key] === "") {
    result.valid = false;
    result.issues.push({ path: `${path}.${key}`, message: "Expected a non-empty string.", severity: "error" });
  }
}

export function validateRequiredArray(record: Record<string, unknown>, path: string, key: string, result: ValidationResult): void {
  if (!Array.isArray(record[key])) {
    result.valid = false;
    result.issues.push({ path: `${path}.${key}`, message: "Expected an array.", severity: "error" });
  }
}
