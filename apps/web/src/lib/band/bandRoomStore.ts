import type { AgentMessage, AgentProfile, ApprovalDecision, ApprovalRequest, TaskStatus } from "@/lib/types";
import type { CollaborationAuditEvent, CollaborationRoom, CollaborationRoomSnapshot } from "@/lib/collaboration/types";
import type { BandChat, BandLocalRoomRecord } from "./bandTypes";
import { nowIso } from "./bandMappers";

type StoreState = {
  recordsByRoomId: Map<string, BandLocalRoomRecord>;
};

declare global {
  // eslint-disable-next-line no-var
  var __sentinelRelayBandStore: StoreState | undefined;
}

function getState(): StoreState {
  if (!globalThis.__sentinelRelayBandStore) {
    globalThis.__sentinelRelayBandStore = { recordsByRoomId: new Map() };
  }
  return globalThis.__sentinelRelayBandStore;
}

function auditId(roomId: string, type: string, count: number): string {
  return `band-audit-${roomId}-${type}-${String(count + 1).padStart(3, "0")}`;
}

function sortMessages(messages: AgentMessage[]): AgentMessage[] {
  return [...messages].sort((a, b) => a.sequence - b.sequence || a.createdAt.localeCompare(b.createdAt) || a.id.localeCompare(b.id));
}

export function createLocalRoomRecord(input: {
  caseId: string;
  title?: string;
  roomId: string;
  bandChat?: BandChat;
  createdBy?: string;
}): BandLocalRoomRecord {
  const timestamp = nowIso();
  const room: CollaborationRoom = {
    id: input.roomId,
    caseId: input.caseId,
    title: input.title ?? input.bandChat?.title ?? undefined,
    createdAt: input.bandChat?.inserted_at ?? timestamp,
    updatedAt: input.bandChat?.updated_at ?? timestamp,
    mode: "band",
    participantAgentIds: [],
  };

  const record: BandLocalRoomRecord = {
    room,
    bandChatId: input.bandChat?.id ?? input.roomId,
    createdBy: input.createdBy,
    registeredAgents: [],
    messages: [],
    approvalRequests: [],
    approvalDecisions: [],
    taskStatuses: [],
    auditEvents: [],
    remoteWarnings: [],
    remotePostedMessageIds: [],
    remotePostedApprovalRequestIds: [],
    remotePostedApprovalDecisionIds: [],
    remotePostedTaskStatusKeys: [],
  };

  record.auditEvents.push(makeAuditEvent(record, "room_created", input.createdBy ?? "band-adapter", "Band incident room created", `Created Band chat ${record.bandChatId ?? record.room.id} for ${input.caseId}.`, {
    bandChatId: record.bandChatId,
    caseId: input.caseId,
  }));

  setRoomRecord(record.room.id, record);
  return record;
}

export function getRoomRecord(roomId: string): BandLocalRoomRecord | undefined {
  return getState().recordsByRoomId.get(roomId);
}

export function setRoomRecord(roomId: string, record: BandLocalRoomRecord): void {
  getState().recordsByRoomId.set(roomId, record);
}

export function ensureRoomRecord(roomId: string): BandLocalRoomRecord {
  const record = getRoomRecord(roomId);
  if (!record) throw new Error(`No Band room record exists for ${roomId}. Create the incident room first.`);
  return record;
}

export function resetRoomRecord(roomId: string): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const updated: BandLocalRoomRecord = {
    ...record,
    messages: [],
    approvalRequests: [],
    approvalDecisions: [],
    taskStatuses: [],
    auditEvents: [...record.auditEvents],
    room: { ...record.room, updatedAt: nowIso() },
  };
  updated.auditEvents.push(makeAuditEvent(updated, "room_reset", "band-adapter", "Local room mirror reset", "Reset local Sentinel Relay mirror while preserving the remote Band chat.", {}));
  setRoomRecord(roomId, updated);
  return updated;
}

export function registerAgentInRoom(roomId: string, agent: AgentProfile): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const registeredAgents = [...record.registeredAgents.filter((existing) => existing.id !== agent.id), agent];
  const participantAgentIds = Array.from(new Set([...record.room.participantAgentIds, agent.id]));
  const updated: BandLocalRoomRecord = {
    ...record,
    registeredAgents,
    room: { ...record.room, participantAgentIds, updatedAt: nowIso() },
  };
  updated.auditEvents.push(makeAuditEvent(updated, "agent_registered", agent.id, "Agent registered in Sentinel mirror", `${agent.name} registered for Band room coordination.`, { agentId: agent.id }));
  setRoomRecord(roomId, updated);
  return updated;
}

export function addRemoteWarning(roomId: string, warning: string, metadata?: Record<string, unknown>): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const updated: BandLocalRoomRecord = {
    ...record,
    remoteWarnings: Array.from(new Set([...record.remoteWarnings, warning])),
    auditEvents: [...record.auditEvents],
    room: { ...record.room, updatedAt: nowIso() },
  };
  updated.auditEvents.push(makeAuditEvent(updated, "provider_warning", "band-adapter", "Band adapter warning", warning, metadata));
  setRoomRecord(roomId, updated);
  return updated;
}

export function addMessageToRoom(roomId: string, message: AgentMessage): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const nextMessages = sortMessages([...record.messages.filter((existing) => existing.id !== message.id), message]);
  const updated: BandLocalRoomRecord = {
    ...record,
    messages: nextMessages,
    room: { ...record.room, updatedAt: nowIso() },
    auditEvents: [...record.auditEvents],
  };
  updated.auditEvents.push(makeAuditEvent(updated, "message_sent", message.agentId, message.title, message.summary, {
    messageId: message.id,
    messageType: message.type,
    sequence: message.sequence,
  }));
  setRoomRecord(roomId, updated);
  return updated;
}

export function addApprovalRequestToRoom(roomId: string, request: ApprovalRequest): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const updated: BandLocalRoomRecord = {
    ...record,
    approvalRequests: [...record.approvalRequests.filter((existing) => existing.id !== request.id), request],
    room: { ...record.room, updatedAt: nowIso() },
    auditEvents: [...record.auditEvents],
  };
  updated.auditEvents.push(makeAuditEvent(updated, "approval_requested", request.requestedByAgentId, "Human approval requested", request.action, { requestId: request.id, status: request.status }));
  setRoomRecord(roomId, updated);
  return updated;
}

export function addApprovalDecisionToRoom(roomId: string, decision: ApprovalDecision): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const updated: BandLocalRoomRecord = {
    ...record,
    approvalDecisions: [...record.approvalDecisions.filter((existing) => existing.id !== decision.id), decision],
    room: { ...record.room, updatedAt: nowIso() },
    auditEvents: [...record.auditEvents],
  };
  updated.auditEvents.push(makeAuditEvent(updated, "approval_decision_submitted", decision.decidedBy, "Human approval decision submitted", decision.rationale, { decisionId: decision.id, requestId: decision.requestId, decision: decision.decision }));
  setRoomRecord(roomId, updated);
  return updated;
}

export function updateTaskStatusInRoom(roomId: string, taskId: string, status: TaskStatus): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const updatedAt = nowIso();
  const taskStatuses = [...record.taskStatuses.filter((existing) => existing.taskId !== taskId), { roomId, taskId, status, updatedAt }];
  const updated: BandLocalRoomRecord = {
    ...record,
    taskStatuses,
    room: { ...record.room, updatedAt },
    auditEvents: [...record.auditEvents],
  };
  updated.auditEvents.push(makeAuditEvent(updated, "task_status_updated", "band-adapter", "Task status updated", `${taskId} moved to ${status}.`, { taskId, status }));
  setRoomRecord(roomId, updated);
  return updated;
}

export function hydrateRoomRecord(roomId: string, snapshot: Partial<CollaborationRoomSnapshot>): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const updated: BandLocalRoomRecord = {
    ...record,
    room: snapshot.room ? { ...record.room, ...snapshot.room, updatedAt: nowIso() } : { ...record.room, updatedAt: nowIso() },
    messages: snapshot.messages ? sortMessages(snapshot.messages) : record.messages,
    registeredAgents: snapshot.registeredAgents ?? record.registeredAgents,
    approvalRequests: snapshot.approvalRequests ?? record.approvalRequests,
    approvalDecisions: snapshot.approvalDecisions ?? record.approvalDecisions,
    taskStatuses: snapshot.taskStatuses ?? record.taskStatuses,
    auditEvents: [...record.auditEvents],
  };
  updated.auditEvents.push(makeAuditEvent(updated, "room_hydrated", "band-adapter", "Room mirror hydrated", "Hydrated local room mirror from Sentinel Relay workflow state.", {}));
  setRoomRecord(roomId, updated);
  return updated;
}

export function getRoomSnapshot(roomId: string): CollaborationRoomSnapshot | undefined {
  const record = getRoomRecord(roomId);
  return record ? toSnapshot(record) : undefined;
}


export function hasRemotePostedMessage(roomId: string, messageId: string): boolean {
  return Boolean(getRoomRecord(roomId)?.remotePostedMessageIds.includes(messageId));
}

export function markRemotePostedMessage(roomId: string, messageId: string): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const updated: BandLocalRoomRecord = {
    ...record,
    remotePostedMessageIds: Array.from(new Set([...record.remotePostedMessageIds, messageId])),
  };
  setRoomRecord(roomId, updated);
  return updated;
}

export function hasRemotePostedApprovalRequest(roomId: string, requestId: string): boolean {
  return Boolean(getRoomRecord(roomId)?.remotePostedApprovalRequestIds.includes(requestId));
}

export function markRemotePostedApprovalRequest(roomId: string, requestId: string): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const updated: BandLocalRoomRecord = {
    ...record,
    remotePostedApprovalRequestIds: Array.from(new Set([...record.remotePostedApprovalRequestIds, requestId])),
  };
  setRoomRecord(roomId, updated);
  return updated;
}

export function hasRemotePostedApprovalDecision(roomId: string, decisionId: string): boolean {
  return Boolean(getRoomRecord(roomId)?.remotePostedApprovalDecisionIds.includes(decisionId));
}

export function markRemotePostedApprovalDecision(roomId: string, decisionId: string): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const updated: BandLocalRoomRecord = {
    ...record,
    remotePostedApprovalDecisionIds: Array.from(new Set([...record.remotePostedApprovalDecisionIds, decisionId])),
  };
  setRoomRecord(roomId, updated);
  return updated;
}

export function hasRemotePostedTaskStatus(roomId: string, taskId: string, status: string): boolean {
  return Boolean(getRoomRecord(roomId)?.remotePostedTaskStatusKeys.includes(`${taskId}:${status}`));
}

export function markRemotePostedTaskStatus(roomId: string, taskId: string, status: string): BandLocalRoomRecord {
  const record = ensureRoomRecord(roomId);
  const key = `${taskId}:${status}`;
  const updated: BandLocalRoomRecord = {
    ...record,
    remotePostedTaskStatusKeys: Array.from(new Set([...record.remotePostedTaskStatusKeys, key])),
  };
  setRoomRecord(roomId, updated);
  return updated;
}

export function toSnapshot(record: BandLocalRoomRecord): CollaborationRoomSnapshot {
  return {
    room: record.room,
    messages: sortMessages(record.messages),
    registeredAgents: record.registeredAgents,
    approvalRequests: record.approvalRequests,
    approvalDecisions: record.approvalDecisions,
    taskStatuses: record.taskStatuses,
    auditEvents: record.auditEvents,
  };
}

function makeAuditEvent(record: BandLocalRoomRecord, type: CollaborationAuditEvent["type"], actorId: string, title: string, summary: string, metadata?: Record<string, unknown>): CollaborationAuditEvent {
  return {
    id: auditId(record.room.id, type, record.auditEvents.length),
    roomId: record.room.id,
    caseId: record.room.caseId,
    type,
    actorId,
    title,
    summary,
    createdAt: nowIso(),
    metadata,
  };
}
