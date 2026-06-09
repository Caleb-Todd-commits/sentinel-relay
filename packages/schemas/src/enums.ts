export const SCHEMA_VERSION = "0.4.0" as const;
export const PRODUCT_NAME = "Sentinel Relay" as const;

export const severityValues = ["informational", "low", "medium", "high", "critical"] as const;
export type Severity = (typeof severityValues)[number];

export const incidentStatusValues = [
  "draft",
  "open",
  "triaging",
  "investigating",
  "awaiting_approval",
  "approved_for_containment",
  "remediating",
  "report_ready",
  "closed",
] as const;
export type IncidentStatus = (typeof incidentStatusValues)[number];

export const incidentPhaseValues = [
  "intake",
  "triage",
  "evidence_collection",
  "hypothesis_review",
  "risk_review",
  "human_approval",
  "containment",
  "remediation",
  "reporting",
  "closed",
] as const;
export type IncidentPhase = (typeof incidentPhaseValues)[number];

export const decisionGateValues = ["none", "human_required", "approved", "rejected", "deferred"] as const;
export type DecisionGate = (typeof decisionGateValues)[number];

export const confidenceBandValues = ["unknown", "low", "medium", "high", "verified"] as const;
export type ConfidenceBand = (typeof confidenceBandValues)[number];

export const agentStatusValues = [
  "offline",
  "idle",
  "assigned",
  "working",
  "challenging",
  "waiting",
  "blocked",
  "complete",
] as const;
export type AgentStatus = (typeof agentStatusValues)[number];

export const agentCapabilityValues = [
  "case_command",
  "log_forensics",
  "threat_assessment",
  "code_review",
  "risk_compliance",
  "remediation",
  "human_approval",
  "report_generation",
] as const;
export type AgentCapability = (typeof agentCapabilityValues)[number];

export const agentKindValues = ["ai_agent", "human_actor", "system"] as const;
export type AgentKind = (typeof agentKindValues)[number];

export const evidenceKindValues = [
  "log",
  "code_diff",
  "policy",
  "ticket",
  "timeline",
  "decision",
  "configuration",
  "external_indicator",
  "report",
] as const;
export type EvidenceKind = (typeof evidenceKindValues)[number];

export const evidenceSensitivityValues = ["public_demo", "internal", "confidential", "restricted"] as const;
export type EvidenceSensitivity = (typeof evidenceSensitivityValues)[number];

export const messageTypeValues = [
  "case_opened",
  "room_created",
  "agent_joined",
  "task_assignment",
  "finding",
  "challenge",
  "verification",
  "risk_assessment",
  "approval_request",
  "approval_decision",
  "remediation_task",
  "report_section",
  "state_update",
  "handoff",
  "watchdog_alert",
] as const;
export type AgentMessageType = (typeof messageTypeValues)[number];

export const messageVisibilityValues = ["judge_demo", "internal", "security_lead_only"] as const;
export type MessageVisibility = (typeof messageVisibilityValues)[number];

export const taskStatusValues = ["blocked", "todo", "in_progress", "review", "done", "deferred"] as const;
export type TaskStatus = (typeof taskStatusValues)[number];
export type RemediationTaskStatus = TaskStatus;

export const approvalStatusValues = ["pending", "approved", "rejected", "deferred", "expired"] as const;
export type ApprovalStatus = (typeof approvalStatusValues)[number];

export const approvalDecisionValues = ["approved", "rejected", "deferred"] as const;
export type ApprovalDecisionValue = (typeof approvalDecisionValues)[number];

export const reportSectionTypeValues = [
  "executive_summary",
  "timeline",
  "evidence",
  "root_cause",
  "risk_assessment",
  "customer_impact",
  "actions_taken",
  "remediation",
  "open_questions",
  "audit_trail",
] as const;
export type ReportSectionType = (typeof reportSectionTypeValues)[number];

export const collaborationModeValues = ["mock", "band"] as const;
export type CollaborationMode = (typeof collaborationModeValues)[number];
