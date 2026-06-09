import type { AgentMessage, AgentProfile, ApprovalDecision, ApprovalRequest, TaskStatus } from "@/lib/types";
import type { CollaborationAuditEvent, CollaborationRoom, CollaborationRoomSnapshot } from "@/lib/collaboration/types";

export type BandApiPerspective = "agent" | "human";

export type BandApiResponse<T> = {
  data?: T;
  error?: string;
  errors?: unknown;
  [key: string]: unknown;
};

export type BandChat = {
  id: string;
  inserted_at?: string;
  updated_at?: string;
  task_id?: string | null;
  title?: string | null;
  [key: string]: unknown;
};

export type BandParticipant = {
  id: string;
  participant_id?: string;
  role?: string;
  status?: string;
  type?: string;
  handle?: string;
  name?: string;
  [key: string]: unknown;
};

export type BandMention = {
  id: string;
  name: string;
  handle: string;
};

export type BandConfiguredAgent = {
  sentinelAgentId: string;
  envSuffix: string;
  name: string;
  handle?: string;
  participantId?: string;
  apiKey?: string;
};

export type BandRuntimeConfig = {
  enabled: boolean;
  baseUrl: string;
  wsUrl: string;
  commanderAgentApiKey?: string;
  humanApiKey?: string;
  commanderAgentId?: string;
  dashboardHumanParticipantId?: string;
  dryRun: boolean;
  configuredAgents: Record<string, BandConfiguredAgent>;
  missingRequired: string[];
  warnings: string[];
};

export type BandLocalRoomRecord = {
  room: CollaborationRoom;
  bandChatId?: string;
  createdBy?: string;
  registeredAgents: AgentProfile[];
  messages: AgentMessage[];
  approvalRequests: ApprovalRequest[];
  approvalDecisions: ApprovalDecision[];
  taskStatuses: Array<{
    roomId: string;
    taskId: string;
    status: TaskStatus;
    updatedAt: string;
  }>;
  auditEvents: CollaborationAuditEvent[];
  remoteWarnings: string[];
  remotePostedMessageIds: string[];
  remotePostedApprovalRequestIds: string[];
  remotePostedApprovalDecisionIds: string[];
  remotePostedTaskStatusKeys: string[];
};

export type BandRequestResult<T> = {
  ok: boolean;
  status: number;
  data?: T;
  raw?: unknown;
  error?: string;
};

export type BandRoomCreateResult = {
  room: CollaborationRoom;
  remoteChat?: BandChat;
  snapshot: CollaborationRoomSnapshot;
  warnings: string[];
};

export type BandRouteErrorBody = {
  code: string;
  error: string;
  recoverable: boolean;
  missing?: string[];
  warnings?: string[];
};
