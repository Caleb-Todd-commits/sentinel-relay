import type { AgentMessage, ApprovalDecision, ApprovalRequest } from "@/lib/types";
import type { BandConfiguredAgent, BandMention } from "./bandTypes";
import { getBandRuntimeConfig } from "./bandConfig";

export function nowIso(): string {
  return new Date().toISOString();
}

export function buildSentinelTraceId(messageId: string): string {
  return `sentinel-relay:${messageId}:${Date.now()}`;
}

export function toBandEventFromAgentMessage(message: AgentMessage) {
  return {
    event: {
      content: `${message.agentName}: ${message.title}\n${message.summary}`,
      message_type: "task",
      metadata: {
        source_system: "sentinel_relay",
        schema_version: message.schemaVersion,
        envelope_type: "sentinel_relay.agent_message",
        case_id: message.caseId,
        room_id: message.roomId,
        message_id: message.id,
        agent_id: message.agentId,
        message_type: message.type,
        severity: message.severity,
        confidence: message.confidence,
        evidence_ids: message.evidenceIds,
        target_agent_ids: message.targetAgentIds ?? [],
        payload: message,
      },
    },
  };
}

export function toBandEventFromApprovalRequest(request: ApprovalRequest) {
  return {
    event: {
      content: `Human approval requested: ${request.action}`,
      message_type: "task",
      metadata: {
        source_system: "sentinel_relay",
        envelope_type: "sentinel_relay.approval_request",
        approval_request_id: request.id,
        case_id: request.caseId,
        requested_by_agent_id: request.requestedByAgentId,
        action: request.action,
        severity: request.severity,
        status: request.status,
        payload: request,
      },
    },
  };
}

export function toBandEventFromApprovalDecision(decision: ApprovalDecision) {
  return {
    event: {
      content: `Human decision recorded: ${decision.decision.toUpperCase()} — ${decision.rationale}`,
      message_type: "task",
      metadata: {
        source_system: "sentinel_relay",
        envelope_type: "sentinel_relay.approval_decision",
        approval_decision_id: decision.id,
        approval_request_id: decision.requestId,
        decided_by: decision.decidedBy,
        decision: decision.decision,
        approved_action_scope: decision.approvedActionScope,
        explicitly_not_approved: decision.explicitlyNotApproved,
        payload: decision,
      },
    },
  };
}

export function toBandEventFromTaskStatus(roomId: string, taskId: string, status: string) {
  return {
    event: {
      content: `Sentinel Relay task ${taskId} moved to ${status}.`,
      message_type: "task",
      metadata: {
        source_system: "sentinel_relay",
        envelope_type: "sentinel_relay.task_status",
        room_id: roomId,
        task_id: taskId,
        status,
      },
    },
  };
}

export function buildMentions(targetAgentIds: string[] | undefined): BandMention[] {
  const config = getBandRuntimeConfig();
  const mentions: BandMention[] = [];

  for (const targetAgentId of targetAgentIds ?? []) {
    const configuredAgent = config.configuredAgents[targetAgentId];
    if (!configuredAgent?.participantId) continue;
    mentions.push({
      id: configuredAgent.participantId,
      name: configuredAgent.name,
      handle: configuredAgent.handle ?? configuredAgent.name.toLowerCase().replace(/[^a-z0-9]+/g, ".").replace(/^\.|\.$/g, ""),
    });
  }

  return mentions;
}

export function buildRoutedTextContent(message: AgentMessage, mentions: BandMention[]): string {
  const mentionPrefix = mentions.length > 0 ? `${mentions.map((mention) => `@${mention.handle}`).join(" ")} ` : "";
  const evidenceText = message.evidenceIds.length > 0 ? `\nEvidence: ${message.evidenceIds.join(", ")}` : "";
  const nextAction = message.nextAction ? `\nNext action: ${message.nextAction}` : "";
  return `${mentionPrefix}${message.title}\n${message.summary}${evidenceText}${nextAction}`.trim();
}

export function configuredAgentToMention(agent: BandConfiguredAgent): BandMention | undefined {
  if (!agent.participantId) return undefined;
  return {
    id: agent.participantId,
    name: agent.name,
    handle: agent.handle ?? agent.name.toLowerCase().replace(/[^a-z0-9]+/g, ".").replace(/^\.|\.$/g, ""),
  };
}
