import type { AgentCapability, AgentKind, AgentStatus } from "./enums";
import type { AgentId, ISODateTimeString } from "./primitives";

export type AgentProfile = {
  id: AgentId;
  name: string;
  shortName: string;
  kind: AgentKind;
  role: string;
  responsibility: string;
  capability: AgentCapability;
  status: AgentStatus;
  currentTask?: string;
  allowedDecisions: string[];
  requiresHumanApprovalFor: string[];
  createdAt?: ISODateTimeString;
};

export type AgentAssignment = {
  id: string;
  caseId: string;
  roomId: string;
  assignedByAgentId: AgentId;
  assignedToAgentId: AgentId;
  objective: string;
  expectedOutputType: string;
  dueAt?: ISODateTimeString;
  evidenceIds: string[];
  status: "assigned" | "accepted" | "working" | "blocked" | "complete";
};
