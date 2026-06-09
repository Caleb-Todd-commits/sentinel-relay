import type { BandApiPerspective, BandApiResponse, BandChat, BandMention, BandParticipant, BandRequestResult, BandRuntimeConfig } from "./bandTypes";
import { getBandRuntimeConfig } from "./bandConfig";

export class BandRestClient {
  constructor(private readonly config: BandRuntimeConfig = getBandRuntimeConfig()) {}

  getConfiguration() {
    return this.config;
  }

  async verifyCommanderIdentity(): Promise<BandRequestResult<unknown>> {
    return this.request<unknown>("agent", "/me", { method: "GET" });
  }

  async verifyHumanIdentity(): Promise<BandRequestResult<unknown>> {
    if (!this.config.humanApiKey) {
      return { ok: false, status: 0, error: "BAND_HUMAN_API_KEY is not configured." };
    }
    return this.request<unknown>("human", "/profile", { method: "GET" });
  }

  async createAgentChat(): Promise<BandRequestResult<BandChat>> {
    if (this.config.dryRun) {
      return {
        ok: true,
        status: 201,
        data: {
          id: `dry-run-band-chat-${Date.now()}`,
          inserted_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          task_id: null,
          title: null,
        },
      };
    }

    return this.request<BandChat>("agent", "/chats", {
      method: "POST",
      body: { chat: {} },
    });
  }

  async getAgentChat(chatId: string): Promise<BandRequestResult<BandChat>> {
    return this.request<BandChat>("agent", `/chats/${encodeURIComponent(chatId)}`, { method: "GET" });
  }

  async addAgentParticipant(chatId: string, participantId: string): Promise<BandRequestResult<BandParticipant>> {
    if (this.config.dryRun) {
      return {
        ok: true,
        status: 201,
        data: {
          id: participantId,
          participant_id: participantId,
          role: "member",
          status: "active",
          type: "Agent",
        },
      };
    }

    return this.request<BandParticipant>("agent", `/chats/${encodeURIComponent(chatId)}/participants`, {
      method: "POST",
      body: { participant: { participant_id: participantId } },
    });
  }

  async sendAgentTextMessage(chatId: string, content: string, mentions: BandMention[]): Promise<BandRequestResult<unknown>> {
    if (mentions.length === 0) {
      return { ok: false, status: 0, error: "Band text messages require at least one mention. Use events for non-routed activity." };
    }

    if (this.config.dryRun) {
      return { ok: true, status: 201, data: { id: `dry-run-message-${Date.now()}`, content, mentions } };
    }

    return this.request<unknown>("agent", `/chats/${encodeURIComponent(chatId)}/messages`, {
      method: "POST",
      body: { message: { content, mentions } },
    });
  }

  async postAgentEvent(chatId: string, eventPayload: Record<string, unknown>): Promise<BandRequestResult<unknown>> {
    if (this.config.dryRun) {
      return { ok: true, status: 201, data: { id: `dry-run-event-${Date.now()}`, ...eventPayload } };
    }

    return this.request<unknown>("agent", `/chats/${encodeURIComponent(chatId)}/events`, {
      method: "POST",
      body: eventPayload,
    });
  }

  async getHumanMessages(chatId: string): Promise<BandRequestResult<unknown[]>> {
    if (!this.config.humanApiKey) {
      return { ok: false, status: 0, error: "BAND_HUMAN_API_KEY is not configured." };
    }

    return this.request<unknown[]>("human", `/chats/${encodeURIComponent(chatId)}/messages?message_type=all`, { method: "GET" });
  }

  async listAgentMessages(chatId: string): Promise<BandRequestResult<unknown[]>> {
    return this.request<unknown[]>("agent", `/chats/${encodeURIComponent(chatId)}/messages?status=all`, { method: "GET" });
  }

  private async request<T>(perspective: BandApiPerspective, path: string, options: { method: "GET" | "POST" | "DELETE"; body?: unknown }): Promise<BandRequestResult<T>> {
    const apiKey = perspective === "human" ? this.config.humanApiKey : this.config.commanderAgentApiKey;
    if (!apiKey) {
      return {
        ok: false,
        status: 0,
        error: perspective === "human" ? "BAND_HUMAN_API_KEY is not configured." : "BAND_COMMANDER_AGENT_API_KEY is not configured.",
      };
    }

    const url = `${this.config.baseUrl}/${perspective === "human" ? "me" : "agent"}${path}`;
    const response = await fetch(url, {
      method: options.method,
      headers: {
        "X-API-Key": apiKey,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      cache: "no-store",
    });

    const raw = await this.parseJson(response);
    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        raw,
        error: this.extractError(raw, response.status),
      };
    }

    return {
      ok: true,
      status: response.status,
      data: this.unwrapData<T>(raw),
      raw,
    };
  }

  private async parseJson(response: Response): Promise<unknown> {
    const text = await response.text();
    if (!text) return undefined;
    try {
      return JSON.parse(text) as unknown;
    } catch {
      return text;
    }
  }

  private unwrapData<T>(raw: unknown): T {
    if (typeof raw === "object" && raw !== null && "data" in raw) {
      return (raw as BandApiResponse<T>).data as T;
    }
    return raw as T;
  }

  private extractError(raw: unknown, status: number): string {
    if (typeof raw === "object" && raw !== null) {
      const record = raw as Record<string, unknown>;
      if (typeof record.error === "string") return record.error;
      if (typeof record.message === "string") return record.message;
      if (record.errors) return JSON.stringify(record.errors);
    }
    if (typeof raw === "string" && raw.length > 0) return raw;
    return `Band API request failed with HTTP ${status}.`;
  }
}
