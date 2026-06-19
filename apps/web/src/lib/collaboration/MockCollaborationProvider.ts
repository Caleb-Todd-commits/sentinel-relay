import type { AgentMessage, AgentProfile, ApprovalDecision, ApprovalRequest, TaskStatus } from "@/lib/types";
import type { CollaborationProvider } from "./CollaborationProvider";
import type {
  CollaborationAuditEvent,
  CollaborationProviderHealth,
  CollaborationRoom,
  CollaborationRoomSnapshot,
  CreateIncidentRoomInput,
} from "./types";

function nowIso(): string {
  return new Date().toISOString();
}

function normalizeRoomInput(input: CreateIncidentRoomInput | string): CreateIncidentRoomInput {
  return typeof input === "string" ? { caseId: input, requestedBy: "system" } : input;
}

function stableRoomId(caseId: string): string {
  return `mock-room-${caseId}`;
}

function auditId(type: string, roomId: string, count: number): string {
  return `audit-${roomId}-${type}-${String(count + 1).padStart(3, "0")}`;
}

function messageSort(a: AgentMessage, b: AgentMessage): number {
  return a.sequence - b.sequence || a.createdAt.localeCompare(b.createdAt) || a.id.localeCompare(b.id);
}

export class MockCollaborationProvider implements CollaborationProvider {
  readonly mode = "mock" as const;
  readonly capabilities = [
    "room_creation",
    "agent_registration",
    "message_send",
    "message_subscribe",
    "task_status",
    "human_approval",
    "audit_snapshot",
    "demo_hydration",
  ] as const;

  private readonly roomsById = new Map<string, CollaborationRoom>();
  private readonly messagesByRoom = new Map<string, AgentMessage[]>();
  private readonly agentProfilesByRoom = new Map<string, Map<string, AgentProfile>>();
  private readonly subscribersByRoom = new Map<string, Set<(message: AgentMessage) => void>>();
  private readonly snapshotSubscribersByRoom = new Map<string, Set<(snapshot: CollaborationRoomSnapshot) => void>>();
  private readonly approvalRequestsByRoom = new Map<string, ApprovalRequest[]>();
  private readonly approvalDecisionsByRoom = new Map<string, ApprovalDecision[]>();
  private readonly taskStatusesByRoom = new Map<string, Array<{ roomId: string; taskId: string; status: TaskStatus; updatedAt: string }>>();
  private readonly auditEventsByRoom = new Map<string, CollaborationAuditEvent[]>();

  getHealth(): CollaborationProviderHealth {
    return {
      mode: this.mode,
      status: "ready",
      label: "Mock Mode",
      summary: "Using an in-memory collaboration provider that follows the same Sentinel Relay provider contract as Band Mode.",
      checkedAt: nowIso(),
      canCreateRooms: true,
      canSendMessages: true,
      canSubscribe: true,
      canRequestApproval: true,
      canHydrateDemoState: true,
      warnings: [
        "Messages are not persisted across browser refreshes.",
        "This mode proves the collaboration contract before live Band credentials are connected.",
      ],
      nextSteps: [
        "Keep Mock Mode available as the demo fallback path.",
        "Connect the Band provider through server-side API routes when live credentials are available.",
      ],
    };
  }

  async createIncidentRoom(input: CreateIncidentRoomInput | string): Promise<CollaborationRoom> {
    const normalized = normalizeRoomInput(input);
    const roomId = stableRoomId(normalized.caseId);
    const existingRoom = this.roomsById.get(roomId);

    if (existingRoom) {
      return existingRoom;
    }

    const timestamp = nowIso();
    const room: CollaborationRoom = {
      id: roomId,
      caseId: normalized.caseId,
      title: normalized.title,
      createdAt: timestamp,
      updatedAt: timestamp,
      mode: this.mode,
      participantAgentIds: [],
    };

    this.roomsById.set(roomId, room);
    this.messagesByRoom.set(roomId, []);
    this.agentProfilesByRoom.set(roomId, new Map());
    this.approvalRequestsByRoom.set(roomId, []);
    this.approvalDecisionsByRoom.set(roomId, []);
    this.taskStatusesByRoom.set(roomId, []);
    this.auditEventsByRoom.set(roomId, []);

    this.appendAuditEvent(roomId, {
      type: "room_created",
      actorId: normalized.requestedBy ?? "system",
      title: "Incident room created",
      summary: `Created mock collaboration room for ${normalized.caseId}.`,
      metadata: { caseId: normalized.caseId, title: normalized.title },
    });

    await this.emitSnapshot(roomId);
    return room;
  }

  async registerAgent(roomId: string, agent: AgentProfile | string): Promise<void> {
    const room = this.requireRoom(roomId);
    const agentId = typeof agent === "string" ? agent : agent.id;
    const participantAgentIds = Array.from(new Set([...room.participantAgentIds, agentId]));

    this.roomsById.set(roomId, { ...room, participantAgentIds, updatedAt: nowIso() });

    if (typeof agent !== "string") {
      const agents = this.agentProfilesByRoom.get(roomId) ?? new Map<string, AgentProfile>();
      agents.set(agent.id, agent);
      this.agentProfilesByRoom.set(roomId, agents);
    }

    this.appendAuditEvent(roomId, {
      type: "agent_registered",
      actorId: agentId,
      title: "Agent registered",
      summary: `${agentId} joined the incident coordination room.`,
      metadata: { agentId },
    });

    await this.emitSnapshot(roomId);
  }

  async sendMessage(roomId: string, message: AgentMessage): Promise<void> {
    this.requireRoom(roomId);
    const existingMessages = this.messagesByRoom.get(roomId) ?? [];
    const withoutDuplicate = existingMessages.filter((existingMessage) => existingMessage.id !== message.id);
    const nextMessages = [...withoutDuplicate, message].sort(messageSort);

    this.messagesByRoom.set(roomId, nextMessages);
    this.touchRoom(roomId);

    this.appendAuditEvent(roomId, {
      type: "message_sent",
      actorId: message.agentId,
      title: message.title,
      summary: message.summary,
      metadata: { messageId: message.id, messageType: message.type, sequence: message.sequence },
    });

    const subscribers = this.subscribersByRoom.get(roomId) ?? new Set();
    subscribers.forEach((callback) => callback(message));
    await this.emitSnapshot(roomId);
  }

  async getMessages(roomId: string): Promise<AgentMessage[]> {
    this.requireRoom(roomId);
    return [...(this.messagesByRoom.get(roomId) ?? [])].sort(messageSort);
  }

  subscribeToMessages(roomId: string, callback: (message: AgentMessage) => void): () => void {
    const subscribers = this.subscribersByRoom.get(roomId) ?? new Set<(message: AgentMessage) => void>();
    subscribers.add(callback);
    this.subscribersByRoom.set(roomId, subscribers);

    return () => {
      const currentSubscribers = this.subscribersByRoom.get(roomId);
      currentSubscribers?.delete(callback);
    };
  }

  async updateTaskStatus(roomId: string, taskId: string, status: TaskStatus): Promise<void> {
    this.requireRoom(roomId);
    const existingRecords = this.taskStatusesByRoom.get(roomId) ?? [];
    const nextRecords = existingRecords.filter((record) => record.taskId !== taskId);
    nextRecords.push({ roomId, taskId, status, updatedAt: nowIso() });
    this.taskStatusesByRoom.set(roomId, nextRecords);
    this.touchRoom(roomId);

    this.appendAuditEvent(roomId, {
      type: "task_status_updated",
      actorId: "workflow-engine",
      title: "Task status updated",
      summary: `${taskId} moved to ${status}.`,
      metadata: { taskId, status },
    });

    await this.emitSnapshot(roomId);
  }

  async requestHumanApproval(roomId: string, request: ApprovalRequest): Promise<void> {
    this.requireRoom(roomId);
    const existingRequests = this.approvalRequestsByRoom.get(roomId) ?? [];
    const withoutDuplicate = existingRequests.filter((existingRequest) => existingRequest.id !== request.id);
    this.approvalRequestsByRoom.set(roomId, [...withoutDuplicate, request]);
    this.touchRoom(roomId);

    this.appendAuditEvent(roomId, {
      type: "approval_requested",
      actorId: request.requestedByAgentId,
      title: "Human approval requested",
      summary: request.action,
      metadata: { requestId: request.id, status: request.status },
    });

    await this.emitSnapshot(roomId);
  }

  async submitHumanDecision(roomId: string, decision: ApprovalDecision): Promise<void> {
    this.requireRoom(roomId);
    const existingDecisions = this.approvalDecisionsByRoom.get(roomId) ?? [];
    const withoutDuplicate = existingDecisions.filter((existingDecision) => existingDecision.id !== decision.id);
    this.approvalDecisionsByRoom.set(roomId, [...withoutDuplicate, decision]);
    this.touchRoom(roomId);

    this.appendAuditEvent(roomId, {
      type: "approval_decision_submitted",
      actorId: decision.decidedBy,
      title: "Human decision recorded",
      summary: decision.rationale,
      metadata: { requestId: decision.requestId, decision: decision.decision },
    });

    await this.emitSnapshot(roomId);
  }

  async getRoomSnapshot(roomId: string): Promise<CollaborationRoomSnapshot | undefined> {
    const room = this.roomsById.get(roomId);
    if (!room) return undefined;

    return {
      room,
      messages: [...(this.messagesByRoom.get(roomId) ?? [])].sort(messageSort),
      registeredAgents: Array.from(this.agentProfilesByRoom.get(roomId)?.values() ?? []),
      approvalRequests: [...(this.approvalRequestsByRoom.get(roomId) ?? [])],
      approvalDecisions: [...(this.approvalDecisionsByRoom.get(roomId) ?? [])],
      taskStatuses: [...(this.taskStatusesByRoom.get(roomId) ?? [])],
      auditEvents: [...(this.auditEventsByRoom.get(roomId) ?? [])],
    };
  }

  subscribeToRoomSnapshot(roomId: string, callback: (snapshot: CollaborationRoomSnapshot) => void): () => void {
    const subscribers = this.snapshotSubscribersByRoom.get(roomId) ?? new Set<(snapshot: CollaborationRoomSnapshot) => void>();
    subscribers.add(callback);
    this.snapshotSubscribersByRoom.set(roomId, subscribers);

    void this.getRoomSnapshot(roomId).then((snapshot) => {
      if (snapshot) callback(snapshot);
    });

    return () => {
      const currentSubscribers = this.snapshotSubscribersByRoom.get(roomId);
      currentSubscribers?.delete(callback);
    };
  }

  async resetRoom(roomId: string): Promise<void> {
    const room = this.requireRoom(roomId);
    this.messagesByRoom.set(roomId, []);
    this.approvalRequestsByRoom.set(roomId, []);
    this.approvalDecisionsByRoom.set(roomId, []);
    this.taskStatusesByRoom.set(roomId, []);
    this.auditEventsByRoom.set(roomId, []);
    this.roomsById.set(roomId, { ...room, updatedAt: nowIso() });

    this.appendAuditEvent(roomId, {
      type: "room_reset",
      actorId: "workflow-engine",
      title: "Room reset",
      summary: "Cleared messages, approvals, task statuses, and audit events for deterministic replay.",
    });

    await this.emitSnapshot(roomId);
  }

  async hydrateRoomSnapshot(roomId: string, snapshot: Partial<CollaborationRoomSnapshot>): Promise<void> {
    this.requireRoom(roomId);

    if (snapshot.messages) {
      this.messagesByRoom.set(roomId, [...snapshot.messages].sort(messageSort));
    }

    if (snapshot.registeredAgents) {
      this.agentProfilesByRoom.set(roomId, new Map(snapshot.registeredAgents.map((agent) => [agent.id, agent])));
      const room = this.requireRoom(roomId);
      const participantAgentIds = Array.from(new Set([...room.participantAgentIds, ...snapshot.registeredAgents.map((agent) => agent.id)]));
      this.roomsById.set(roomId, { ...room, participantAgentIds, updatedAt: nowIso() });
    }

    if (snapshot.approvalRequests) {
      this.approvalRequestsByRoom.set(roomId, [...snapshot.approvalRequests]);
    }

    if (snapshot.approvalDecisions) {
      this.approvalDecisionsByRoom.set(roomId, [...snapshot.approvalDecisions]);
    }

    if (snapshot.taskStatuses) {
      this.taskStatusesByRoom.set(roomId, [...snapshot.taskStatuses]);
    }

    this.appendAuditEvent(roomId, {
      type: "room_hydrated",
      actorId: "workflow-engine",
      title: "Room snapshot hydrated",
      summary: "Loaded deterministic demo state into the provider-backed collaboration room.",
      metadata: {
        messageCount: snapshot.messages?.length ?? 0,
        approvalRequestCount: snapshot.approvalRequests?.length ?? 0,
        approvalDecisionCount: snapshot.approvalDecisions?.length ?? 0,
      },
    });

    await this.emitSnapshot(roomId);
  }

  seedMessages(roomId: string, messages: AgentMessage[]): void {
    this.messagesByRoom.set(roomId, [...messages].sort(messageSort));
  }

  private requireRoom(roomId: string): CollaborationRoom {
    const room = this.roomsById.get(roomId);
    if (!room) {
      throw new Error(`Mock collaboration room ${roomId} has not been created.`);
    }
    return room;
  }

  private touchRoom(roomId: string): void {
    const room = this.requireRoom(roomId);
    this.roomsById.set(roomId, { ...room, updatedAt: nowIso() });
  }

  private appendAuditEvent(
    roomId: string,
    event: Omit<CollaborationAuditEvent, "id" | "roomId" | "caseId" | "createdAt">,
  ): void {
    const room = this.roomsById.get(roomId);
    const existingEvents = this.auditEventsByRoom.get(roomId) ?? [];
    const nextEvent: CollaborationAuditEvent = {
      id: auditId(event.type, roomId, existingEvents.length),
      roomId,
      caseId: room?.caseId,
      createdAt: nowIso(),
      ...event,
    };
    this.auditEventsByRoom.set(roomId, [...existingEvents, nextEvent]);
  }

  private async emitSnapshot(roomId: string): Promise<void> {
    const snapshot = await this.getRoomSnapshot(roomId);
    if (!snapshot) return;
    const subscribers = this.snapshotSubscribersByRoom.get(roomId) ?? new Set();
    subscribers.forEach((callback) => callback(snapshot));
  }
}
