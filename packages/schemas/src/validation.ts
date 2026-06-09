import { isConfidenceScore, isIncidentPhase, isIncidentStatus, isIsoDateTime, isSeverity, validateRequiredArray, validateRequiredString } from "./guards";
import type { DemoIncident } from "./demo";
import type { AgentMessage } from "./messages";
import type { ValidationResult } from "./primitives";

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

export function validateAgentMessageShape(message: unknown): ValidationResult {
  const result: ValidationResult = { valid: true, issues: [] };
  const record = asRecord(message);
  if (!record) {
    return { valid: false, issues: [{ path: "$", message: "Message must be an object.", severity: "error" }] };
  }

  for (const key of ["id", "schemaVersion", "caseId", "roomId", "agentId", "agentName", "type", "title", "summary", "createdAt"]) {
    validateRequiredString(record, "$", key, result);
  }
  validateRequiredArray(record, "$", "evidenceIds", result);

  if (typeof record.sequence !== "number" || !Number.isInteger(record.sequence) || record.sequence < 1) {
    result.valid = false;
    result.issues.push({ path: "$.sequence", message: "Expected a positive integer sequence.", severity: "error" });
  }
  if (!isConfidenceScore(record.confidence)) {
    result.valid = false;
    result.issues.push({ path: "$.confidence", message: "Expected confidence between 0 and 1.", severity: "error" });
  }
  if (!isSeverity(record.severity)) {
    result.valid = false;
    result.issues.push({ path: "$.severity", message: "Expected valid severity.", severity: "error" });
  }
  if (!isIsoDateTime(record.createdAt)) {
    result.valid = false;
    result.issues.push({ path: "$.createdAt", message: "Expected ISO date-time string.", severity: "error" });
  }

  return result;
}

export function validateDemoIncidentShape(demo: unknown): ValidationResult {
  const result: ValidationResult = { valid: true, issues: [] };
  const record = asRecord(demo);
  if (!record) {
    return { valid: false, issues: [{ path: "$", message: "Demo incident must be an object.", severity: "error" }] };
  }

  for (const key of ["schemaVersion", "case"]) {
    if (!record[key]) {
      result.valid = false;
      result.issues.push({ path: `$.${key}`, message: "Required field missing.", severity: "error" });
    }
  }

  for (const key of ["agents", "messages", "evidence", "timeline", "remediationTasks"]) {
    validateRequiredArray(record, "$", key, result);
  }

  const incident = asRecord(record.case);
  if (incident) {
    validateRequiredString(incident, "$.case", "id", result);
    validateRequiredString(incident, "$.case", "roomId", result);
    validateRequiredString(incident, "$.case", "title", result);
    if (!isSeverity(incident.severity)) {
      result.valid = false;
      result.issues.push({ path: "$.case.severity", message: "Invalid incident severity.", severity: "error" });
    }
    if (!isIncidentStatus(incident.status)) {
      result.valid = false;
      result.issues.push({ path: "$.case.status", message: "Invalid incident status.", severity: "error" });
    }
    if (!isIncidentPhase(incident.phase)) {
      result.valid = false;
      result.issues.push({ path: "$.case.phase", message: "Invalid incident phase.", severity: "error" });
    }
  }

  if (Array.isArray(record.messages)) {
    (record.messages as unknown[]).forEach((message, index) => {
      const messageResult = validateAgentMessageShape(message);
      for (const issue of messageResult.issues) {
        result.valid = false;
        result.issues.push({ ...issue, path: `$.messages[${index}]${issue.path.slice(1)}` });
      }
    });
  }

  return result;
}

export function assertValidAgentMessage(message: AgentMessage): AgentMessage {
  const result = validateAgentMessageShape(message);
  if (!result.valid) {
    throw new Error(`Invalid AgentMessage: ${result.issues.map((issue) => `${issue.path} ${issue.message}`).join("; ")}`);
  }
  return message;
}

export function assertValidDemoIncident(demo: DemoIncident): DemoIncident {
  const result = validateDemoIncidentShape(demo);
  if (!result.valid) {
    throw new Error(`Invalid DemoIncident: ${result.issues.map((issue) => `${issue.path} ${issue.message}`).join("; ")}`);
  }
  return demo;
}
