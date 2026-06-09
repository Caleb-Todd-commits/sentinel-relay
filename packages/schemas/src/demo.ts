import type { AgentProfile } from "./agent";
import type { ApprovalDecision, ApprovalRequest } from "./approval";
import type { EvidenceReference } from "./evidence";
import type { IncidentCase, IncidentStateSnapshot } from "./incident";
import type { AgentMessage } from "./messages";
import type { FinalReport } from "./report";
import type { RemediationTask } from "./remediation";
import type { TimelineEvent } from "./timeline";

export type DemoIncident = {
  schemaVersion: string;
  case: IncidentCase;
  state: IncidentStateSnapshot;
  agents: AgentProfile[];
  messages: AgentMessage[];
  evidence: EvidenceReference[];
  timeline: TimelineEvent[];
  approvalRequest: ApprovalRequest;
  approvalDecision: ApprovalDecision;
  remediationTasks: RemediationTask[];
  finalReport: FinalReport;
};
