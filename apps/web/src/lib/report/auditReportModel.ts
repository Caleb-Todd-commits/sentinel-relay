import type {
  AgentMessage,
  AgentProfile,
  ApprovalDecision,
  DemoIncident,
  EvidenceReference,
  FinalReport,
  RemediationTask,
  TimelineEvent,
} from "@/lib/types";

export type ReportReadinessStatus = "ready" | "blocked" | "needs_review";

export type ReportMetric = {
  label: string;
  value: string;
  detail: string;
  tone: "neutral" | "success" | "warning" | "danger" | "accent";
};

export type AuditTrailRecord = {
  sequence: number;
  messageId: string;
  timestamp: string;
  actor: string;
  actionType: string;
  title: string;
  decisionImpact: string;
  evidenceTitles: string[];
  targetAgents: string[];
  traceId: string;
};

export type EvidenceMatrixRow = {
  id: string;
  title: string;
  source: string;
  kind: string;
  confidenceLabel: string;
  sensitivity: string;
  usedBySections: string[];
  citedByMessages: string[];
  limitations: string[];
};

export type RemediationReportRow = {
  id: string;
  title: string;
  owner: string;
  status: RemediationTask["status"];
  severity: RemediationTask["severity"];
  evidenceTitles: string[];
  acceptanceCriteria: string[];
  testPlan: string[];
  rollbackPlan: string;
};

export type ReportIntegrityCheck = {
  label: string;
  status: ReportReadinessStatus;
  detail: string;
};

export type ApprovalNarrative = {
  decision: string;
  decidedBy: string;
  decidedAt: string;
  rationale: string;
  approvedScope: string[];
  notApproved: string[];
};

export type AuditReportModel = {
  report: FinalReport;
  metrics: ReportMetric[];
  auditTrail: AuditTrailRecord[];
  evidenceMatrix: EvidenceMatrixRow[];
  remediationRows: RemediationReportRow[];
  integrityChecks: ReportIntegrityCheck[];
  approval?: ApprovalNarrative;
  generatedByName: string;
  primaryLimitations: string[];
  exportChecklist: string[];
};

const readableStatus: Record<RemediationTask["status"], string> = {
  blocked: "Blocked",
  todo: "Todo",
  in_progress: "In Progress",
  review: "In Review",
  done: "Done",
  deferred: "Deferred",
};

function percent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function messageTypeLabel(type: AgentMessage["type"]): string {
  return type
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function agentLabel(agents: AgentProfile[], id: string): string {
  return agents.find((agent) => agent.id === id)?.shortName ?? id;
}

function evidenceLabel(evidence: EvidenceReference[], id: string): string {
  return evidence.find((item) => item.id === id)?.title ?? id;
}

function evidenceById(evidence: EvidenceReference[]): Map<string, EvidenceReference> {
  return new Map(evidence.map((item) => [item.id, item]));
}

function messageById(messages: AgentMessage[]): Map<string, AgentMessage> {
  return new Map(messages.map((message) => [message.id, message]));
}

function buildAuditTrail(report: FinalReport, messages: AgentMessage[], evidence: EvidenceReference[], agents: AgentProfile[]): AuditTrailRecord[] {
  const messagesById = messageById(messages);

  return report.auditTrailMessageIds
    .map((messageId) => messagesById.get(messageId))
    .filter((message): message is AgentMessage => Boolean(message))
    .sort((a, b) => a.sequence - b.sequence)
    .map((message) => ({
      sequence: message.sequence,
      messageId: message.id,
      timestamp: message.createdAt,
      actor: message.agentName,
      actionType: messageTypeLabel(message.type),
      title: message.title,
      decisionImpact: message.decisionImpact ?? "No direct decision impact recorded.",
      evidenceTitles: message.evidenceIds.map((id) => evidenceLabel(evidence, id)),
      targetAgents: (message.targetAgentIds ?? []).map((id) => agentLabel(agents, id)),
      traceId: message.correlationId ?? `trace-${message.id}`,
    }));
}

function buildEvidenceMatrix(report: FinalReport, messages: AgentMessage[], evidence: EvidenceReference[]): EvidenceMatrixRow[] {
  return evidence.map((item) => {
    const usedBySections = report.sections
      .filter((section) => section.evidenceIds.includes(item.id))
      .map((section) => section.title);
    const citedByMessages = messages
      .filter((message) => message.evidenceIds.includes(item.id))
      .map((message) => `${message.sequence}. ${message.title}`);

    return {
      id: item.id,
      title: item.title,
      source: item.source,
      kind: item.kind,
      confidenceLabel: percent(item.confidence),
      sensitivity: item.sensitivity,
      usedBySections,
      citedByMessages,
      limitations: item.limitations ?? [],
    };
  });
}

function buildRemediationRows(tasks: RemediationTask[], evidence: EvidenceReference[], agents: AgentProfile[]): RemediationReportRow[] {
  return tasks.map((task) => ({
    id: task.id,
    title: task.title,
    owner: agentLabel(agents, task.ownerAgentId),
    status: task.status,
    severity: task.severity,
    evidenceTitles: task.evidenceIds.map((id) => evidenceLabel(evidence, id)),
    acceptanceCriteria: task.acceptanceCriteria,
    testPlan: task.testPlan ?? [],
    rollbackPlan: task.rollbackPlan ?? "Rollback plan not provided.",
  }));
}

function buildIntegrityChecks(report: FinalReport, messages: AgentMessage[], evidence: EvidenceReference[], approval?: ApprovalDecision): ReportIntegrityCheck[] {
  const evidenceMap = evidenceById(evidence);
  const messageMap = messageById(messages);
  const missingEvidence = new Set<string>();
  const missingMessages = new Set<string>();

  for (const section of report.sections) {
    for (const evidenceId of section.evidenceIds) {
      if (!evidenceMap.has(evidenceId)) missingEvidence.add(evidenceId);
    }
    for (const messageId of section.sourceMessageIds) {
      if (!messageMap.has(messageId)) missingMessages.add(messageId);
    }
  }

  for (const messageId of report.auditTrailMessageIds) {
    if (!messageMap.has(messageId)) missingMessages.add(messageId);
  }

  const challengePresent = messages.some((message) => message.type === "challenge");
  const approvalPresent = Boolean(approval) && messages.some((message) => message.type === "approval_decision");
  const reportSectionPresent = messages.some((message) => message.type === "report_section");

  return [
    {
      label: "Evidence references resolve",
      status: missingEvidence.size === 0 ? "ready" : "blocked",
      detail: missingEvidence.size === 0 ? "Every report evidence reference maps to a known evidence item." : `Missing evidence: ${Array.from(missingEvidence).join(", ")}`,
    },
    {
      label: "Audit messages resolve",
      status: missingMessages.size === 0 ? "ready" : "blocked",
      detail: missingMessages.size === 0 ? "Every report source message maps to a collaboration-stream event." : `Missing messages: ${Array.from(missingMessages).join(", ")}`,
    },
    {
      label: "Challenge recorded",
      status: challengePresent ? "ready" : "needs_review",
      detail: challengePresent ? "Risk & Compliance challenged the customer-impact claim before approval." : "No challenge message was found in the audit trail.",
    },
    {
      label: "Human approval recorded",
      status: approvalPresent ? "ready" : "blocked",
      detail: approvalPresent ? "Containment was explicitly approved and customer notification was explicitly held." : "No human approval decision was found.",
    },
    {
      label: "Report-generation event recorded",
      status: reportSectionPresent ? "ready" : "needs_review",
      detail: reportSectionPresent ? "The final report is backed by a report_section event in the coordination stream." : "No report_section event was found.",
    },
  ];
}

function buildMetrics(report: FinalReport, messages: AgentMessage[], evidence: EvidenceReference[], tasks: RemediationTask[], checks: ReportIntegrityCheck[]): ReportMetric[] {
  const readyChecks = checks.filter((check) => check.status === "ready").length;
  const completedTasks = tasks.filter((task) => task.status === "done" || task.status === "review" || task.status === "in_progress").length;
  const challengeCount = messages.filter((message) => message.type === "challenge").length;

  return [
    {
      label: "Audit trail",
      value: `${report.auditTrailMessageIds.length} events`,
      detail: "Structured Band-style records included in final report.",
      tone: "accent",
    },
    {
      label: "Evidence coverage",
      value: `${evidence.length} items`,
      detail: "Logs, code diff, policy, ticket, and approval evidence are traceable.",
      tone: "success",
    },
    {
      label: "Integrity checks",
      value: `${readyChecks}/${checks.length}`,
      detail: "Report references resolve against known messages and evidence.",
      tone: readyChecks === checks.length ? "success" : "warning",
    },
    {
      label: "Challenge control",
      value: `${challengeCount} recorded`,
      detail: "The system captures disagreement before high-impact decisions.",
      tone: challengeCount > 0 ? "success" : "warning",
    },
    {
      label: "Remediation state",
      value: `${completedTasks}/${tasks.length}`,
      detail: "Containment and fix tasks are linked to evidence and approval.",
      tone: "warning",
    },
    {
      label: "Severity",
      value: report.severity.toUpperCase(),
      detail: "High until customer data scope is fully verified.",
      tone: report.severity === "critical" || report.severity === "high" ? "warning" : "neutral",
    },
  ];
}

function buildApprovalNarrative(approval?: ApprovalDecision): ApprovalNarrative | undefined {
  if (!approval) return undefined;

  return {
    decision: approval.decision,
    decidedBy: approval.decidedBy,
    decidedAt: approval.decidedAt,
    rationale: approval.rationale,
    approvedScope: approval.approvedActionScope,
    notApproved: approval.explicitlyNotApproved,
  };
}

function collectPrimaryLimitations(evidence: EvidenceReference[], report: FinalReport): string[] {
  const evidenceLimitations = evidence.flatMap((item) => item.limitations ?? []);
  return Array.from(new Set([...evidenceLimitations, ...report.openQuestions])).slice(0, 8);
}

export function buildAuditReportModel(incident: DemoIncident): AuditReportModel {
  const checks = buildIntegrityChecks(incident.finalReport, incident.messages, incident.evidence, incident.approvalDecision);

  return {
    report: incident.finalReport,
    metrics: buildMetrics(incident.finalReport, incident.messages, incident.evidence, incident.remediationTasks, checks),
    auditTrail: buildAuditTrail(incident.finalReport, incident.messages, incident.evidence, incident.agents),
    evidenceMatrix: buildEvidenceMatrix(incident.finalReport, incident.messages, incident.evidence),
    remediationRows: buildRemediationRows(incident.remediationTasks, incident.evidence, incident.agents),
    integrityChecks: checks,
    approval: buildApprovalNarrative(incident.approvalDecision),
    generatedByName: agentLabel(incident.agents, incident.finalReport.generatedByAgentId),
    primaryLimitations: collectPrimaryLimitations(incident.evidence, incident.finalReport),
    exportChecklist: [
      "Confirm live Band room ID and participant IDs are attached before production use.",
      "Attach raw logs, diff artifact, and incident policy snapshot to the case record.",
      "Confirm exact customer record scope before external notification.",
      "Have legal/comms review any customer-facing message before release.",
      "Close remediation tasks only after acceptance criteria and test plan pass.",
    ],
  };
}

export { readableStatus };
