import type { AgentMessage, AgentProfile, ApprovalDecision, ApprovalRequest, TaskStatus } from "@/lib/types";
import type { CollaborationProvider } from "./CollaborationProvider";
import type {
  CollaborationCapability,
  CollaborationProviderError,
  CollaborationProviderHealth,
  CollaborationRoom,
  CollaborationRoomSnapshot,
  CreateIncidentRoomInput,
} from "./types";
import { CollaborationProviderError as ProviderError } from "./types";

function nowIso(): string {
  return new Date().toISOString();
}

function normalizeRoomInput(input: CreateIncidentRoomInput | string): CreateIncidentRoomInput {
  return typeof input === "string" ? { caseId: input, requestedBy: "system" } : input;
}

async function safeJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) return {} as T;
  return JSON.parse(text) as T;
}

type StreamSnapshotEvent = {
  snapshot?: CollaborationRoomSnapshot;
};

/**
 * Browser-side Band provider.
 *
 * This provider never talks to Band directly. It calls Sentinel Relay server
 * routes, and those server routes hold Band credentials, translate Sentinel
 * Relay schemas into Band chat/messages/events, and maintain a local dashboard
 * mirror for replay and fallback.
 */
export class BandCollaborationProvider implements CollaborationProvider {
  readonly mode = "band" as const;
  readonly capabilities: CollaborationCapability[] = [
    "room_creation",
    "agent_registration",
    "message_send",
    "message_subscribe",
    "task_status",
    "human_approval",
    "audit_snapshot",
    "demo_hydration",
  ];

  constructor(private readonly internalApiBasePath = "/api/collaboration") {}

  getHealth(): CollaborationProviderHealth {
    return {
      mode: this.mode,
      status: "ready",
      label: "Band Mode via server adapter",
      summary:
        "The browser is using Sentinel Relay server routes for Band room creation, routed messages, structured events, approvals, and local dashboard snapshots.",
      checkedAt: nowIso(),
      canCreateRooms: true,
      canSendMessages: true,
      canSubscribe: true,
      canRequestApproval: true,
      canHydrateDemoState: true,
      warnings: [
        "Band credentials stay server-side. The browser only calls /api/collaboration routes.",
        "If server Band env vars are missing, calls return recoverable 503 errors and Mock Mode should remain the fallback demo path.",
        "The dashboard subscription uses a server-sent local mirror; live remote agents should use the Band SDK/WebSocket path.",
      ],
      nextSteps: [
        "Set BAND_PROVIDER_ENABLED=true and NEXT_PUBLIC_COLLABORATION_MODE=band when testing live mode.",
        "Register remote agents in Band, add participant IDs to env, and run the Python agent workers.",
        "Use /api/collaboration/health?live=true or pnpm band:smoke to verify credentials.",
      ],
    };
  }

  async createIncidentRoom(input: CreateIncidentRoomInput | string): Promise<CollaborationRoom> {
    const normalized = normalizeRoomInput(input);
    return this.post<CollaborationRoom>("/rooms", { action: "createIncidentRoom", input: normalized });
  }

  async registerAgent(roomId: string, agent: AgentProfile | string): Promise<void> {
    await this.post("/rooms", { action: "registerAgent", roomId, agent });
  }

  async sendMessage(roomId: string, message: AgentMessage): Promise<void> {
    await this.post("/messages", { action: "sendMessage", roomId, message });
  }

  async getMessages(roomId: string): Promise<AgentMessage[]> {
    const params = new URLSearchParams({ roomId });
    const response = await fetch(`${this.internalApiBasePath}/messages?${params.toString()}`, {
      method: "GET",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw await this.toProviderError(response, "BAND_GET_MESSAGES_FAILED");
    }

    const body = await safeJson<{ messages: AgentMessage[] }>(response);
    return body.messages ?? [];
  }

  subscribeToMessages(roomId: string, callback: (message: AgentMessage) => void): () => void {
    const eventSource = this.createSnapshotEventSource(roomId, (snapshot) => {
      for (const message of snapshot.messages) {
        callback(message);
      }
    });
    return () => eventSource?.close();
  }

  async updateTaskStatus(roomId: string, taskId: string, status: TaskStatus): Promise<void> {
    await this.post("/messages", { action: "updateTaskStatus", roomId, taskId, status });
  }

  async requestHumanApproval(roomId: string, request: ApprovalRequest): Promise<void> {
    await this.post("/approvals", { action: "requestHumanApproval", roomId, request });
  }

  async submitHumanDecision(roomId: string, decision: ApprovalDecision): Promise<void> {
    await this.post("/approvals", { action: "submitHumanDecision", roomId, decision });
  }

  async getRoomSnapshot(roomId: string): Promise<CollaborationRoomSnapshot | undefined> {
    const params = new URLSearchParams({ roomId });
    const response = await fetch(`${this.internalApiBasePath}/rooms?${params.toString()}`, {
      method: "GET",
      headers: { Accept: "application/json" },
    });

    if (response.status === 404) return undefined;

    if (!response.ok) {
      throw await this.toProviderError(response, "BAND_GET_ROOM_SNAPSHOT_FAILED");
    }

    const body = await safeJson<{ snapshot?: CollaborationRoomSnapshot }>(response);
    return body.snapshot;
  }

  subscribeToRoomSnapshot(roomId: string, callback: (snapshot: CollaborationRoomSnapshot) => void): () => void {
    const eventSource = this.createSnapshotEventSource(roomId, callback);
    return () => eventSource?.close();
  }

  async resetRoom(roomId: string): Promise<void> {
    await this.post("/rooms", { action: "resetRoom", roomId });
  }

  async hydrateRoomSnapshot(roomId: string, snapshot: Partial<CollaborationRoomSnapshot>): Promise<void> {
    await this.post("/rooms", { action: "hydrateRoomSnapshot", roomId, snapshot });
  }

  private createSnapshotEventSource(roomId: string, callback: (snapshot: CollaborationRoomSnapshot) => void): EventSource | undefined {
    if (typeof EventSource === "undefined") return undefined;
    const params = new URLSearchParams({ roomId });
    const eventSource = new EventSource(`${this.internalApiBasePath}/stream?${params.toString()}`);

    eventSource.addEventListener("snapshot", (event) => {
      const parsed = JSON.parse((event as MessageEvent<string>).data) as StreamSnapshotEvent;
      if (parsed.snapshot) callback(parsed.snapshot);
    });

    return eventSource;
  }

  private async post<T = unknown>(path: string, payload: Record<string, unknown>): Promise<T> {
    const response = await fetch(`${this.internalApiBasePath}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw await this.toProviderError(response, "BAND_PROVIDER_POST_FAILED");
    }

    return safeJson<T>(response);
  }

  private async toProviderError(response: Response, fallbackCode: string): Promise<CollaborationProviderError> {
    let body: { error?: string; code?: string; recoverable?: boolean } = {};
    try {
      body = await safeJson(response);
    } catch {
      body = {};
    }

    return new ProviderError(body.error ?? `Band provider request failed with status ${response.status}.`, {
      providerMode: this.mode,
      code: body.code ?? fallbackCode,
      recoverable: body.recoverable ?? true,
    });
  }
}
