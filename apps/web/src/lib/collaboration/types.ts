import type {
  AgentMessage,
  AgentProfile,
  ApprovalDecision,
  ApprovalRequest,
  CollaborationMode,
  TaskStatus,
} from "@/lib/types";

export type CollaborationProviderStatus = "ready" | "degraded" | "not_configured" | "error";

export type CollaborationProviderHealth = {
  mode: CollaborationMode;
  status: CollaborationProviderStatus;
  label: string;
  summary: string;
  checkedAt: string;
  canCreateRooms: boolean;
  canSendMessages: boolean;
  canSubscribe: boolean;
  canRequestApproval: boolean;
  canHydrateDemoState: boolean;
  warnings: string[];
  nextSteps: string[];
};

export type CollaborationCapability =
  | "room_creation"
  | "agent_registration"
  | "message_send"
  | "message_subscribe"
  | "task_status"
  | "human_approval"
  | "audit_snapshot"
  | "demo_hydration";

export type CollaborationRoom = {
  id: string;
  caseId: string;
  title?: string;
  createdAt: string;
  updatedAt: string;
  mode: CollaborationMode;
  participantAgentIds: string[];
};

export type CollaborationAuditEventType =
  | "room_created"
  | "agent_registered"
  | "message_sent"
  | "task_status_updated"
  | "approval_requested"
  | "approval_decision_submitted"
  | "room_reset"
  | "room_hydrated"
  | "provider_warning";

export type CollaborationAuditEvent = {
  id: string;
  roomId: string;
  caseId?: string;
  type: CollaborationAuditEventType;
  actorId: string;
  title: string;
  summary: string;
  createdAt: string;
  metadata?: Record<string, unknown>;
};

export type CollaborationRoomSnapshot = {
  room: CollaborationRoom;
  messages: AgentMessage[];
  registeredAgents: AgentProfile[];
  approvalRequests: ApprovalRequest[];
  approvalDecisions: ApprovalDecision[];
  taskStatuses: Array<{
    roomId: string;
    taskId: string;
    status: TaskStatus;
    updatedAt: string;
  }>;
  auditEvents: CollaborationAuditEvent[];
};

export type CreateIncidentRoomInput = {
  caseId: string;
  title?: string;
  requestedBy?: string;
};

export type RegisterAgentInput = {
  roomId: string;
  agent: AgentProfile;
};

export type SendMessageInput = {
  roomId: string;
  message: AgentMessage;
};

export type CollaborationProviderConfig = {
  mode: CollaborationMode;
  bandApiBaseUrl?: string;
  bandApiKey?: string;
  internalApiBasePath?: string;
  preferServerProxy?: boolean;
};

export class CollaborationProviderError extends Error {
  readonly providerMode: CollaborationMode;
  readonly recoverable: boolean;
  readonly code: string;

  constructor(message: string, options: { providerMode: CollaborationMode; code: string; recoverable?: boolean }) {
    super(message);
    this.name = "CollaborationProviderError";
    this.providerMode = options.providerMode;
    this.code = options.code;
    this.recoverable = options.recoverable ?? true;
  }
}
