import type { ReportSectionType, Severity } from "./enums";
import type { CaseId, EvidenceId, ISODateTimeString, MessageId, TaskId } from "./primitives";

export type ReportSection = {
  id: string;
  type: ReportSectionType;
  title: string;
  content: string;
  evidenceIds: EvidenceId[];
  sourceMessageIds: MessageId[];
};

export type FinalReport = {
  caseId: CaseId;
  title: string;
  generatedAt: ISODateTimeString;
  generatedByAgentId: string;
  severity: Severity;
  executiveSummary: string;
  rootCause: string;
  riskAssessment: string;
  customerImpact: string;
  approvedActions: string[];
  remediationTasks: TaskId[] | string[];
  openQuestions: string[];
  sections: ReportSection[];
  auditTrailMessageIds: MessageId[];
};
