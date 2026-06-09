import type { AgentMessage, AgentProfile, ApprovalDecision, ApprovalRequest, TaskStatus } from "@/lib/types";
import type {
  CollaborationCapability,
  CollaborationProviderHealth,
  CollaborationRoom,
  CollaborationRoomSnapshot,
  CreateIncidentRoomInput,
} from "./types";

export interface CollaborationProvider {
  readonly mode: "mock" | "band";
  readonly capabilities: readonly CollaborationCapability[];

  getHealth(): CollaborationProviderHealth;

  createIncidentRoom(input: CreateIncidentRoomInput | string): Promise<CollaborationRoom>;
  registerAgent(roomId: string, agent: AgentProfile | string): Promise<void>;
  sendMessage(roomId: string, message: AgentMessage): Promise<void>;
  getMessages(roomId: string): Promise<AgentMessage[]>;
  subscribeToMessages(roomId: string, callback: (message: AgentMessage) => void): () => void;

  updateTaskStatus(roomId: string, taskId: string, status: TaskStatus): Promise<void>;
  requestHumanApproval(roomId: string, request: ApprovalRequest): Promise<void>;
  submitHumanDecision(roomId: string, decision: ApprovalDecision): Promise<void>;

  getRoomSnapshot(roomId: string): Promise<CollaborationRoomSnapshot | undefined>;
  subscribeToRoomSnapshot(roomId: string, callback: (snapshot: CollaborationRoomSnapshot) => void): () => void;

  resetRoom(roomId: string): Promise<void>;
  hydrateRoomSnapshot(roomId: string, snapshot: Partial<CollaborationRoomSnapshot>): Promise<void>;
}

export type { CollaborationProviderConfig } from "./types";
