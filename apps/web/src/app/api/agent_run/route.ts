import { getBandRuntimeConfig } from "@/lib/band/bandConfig";
import { BandRestClient } from "@/lib/band/bandRestClient";
import { buildMentions, buildRoutedTextContent, nowIso } from "@/lib/band/bandMappers";
import { getScenario, type ScenarioId } from "@/lib/scenarios";
import type { AgentMessage } from "@/lib/types";

export const maxDuration = 60;
export const dynamic = "force-dynamic";

// ─── NDJSON streaming helpers ────────────────────────────────────────────────

function encode(event: unknown): Uint8Array {
  return new TextEncoder().encode(JSON.stringify(event) + "\n");
}

function ndjsonStream(
  produce: (emit: (event: unknown) => void) => Promise<void>,
): Response {
  const { readable, writable } = new TransformStream<Uint8Array, Uint8Array>();
  const writer = writable.getWriter();

  produce((event) => {
    writer.write(encode(event)).catch(() => {});
  })
    .catch((err) => {
      writer
        .write(encode({ type: "error", code: "runtime_error", message: String(err) }))
        .catch(() => {});
    })
    .finally(() => {
      writer.close().catch(() => {});
    });

  return new Response(readable, {
    headers: {
      "Content-Type": "application/x-ndjson",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}

// ─── Band live path ──────────────────────────────────────────────────────────

const AGENT_ORDER = [
  "agent-commander",
  "agent-forensics",
  "agent-code-review",
  "agent-threat-intel",
  "agent-commander",        // cross-review handoff
  "agent-forensics",        // verification
  "agent-code-review",      // verification
  "agent-threat-intel",     // verification
  "agent-commander",        // assign risk
  "agent-risk-compliance",  // challenge
  "agent-commander",        // approval request
] as const;

const POST_APPROVAL_AGENTS = [
  "agent-human-approver",   // simulated in replay; in live Band this is the human participant
  "agent-commander",        // assign remediation
  "agent-remediation",      // remediation task
  "agent-commander",        // report section
] as const;

async function pollForReply(
  client: BandRestClient,
  chatId: string,
  afterSequence: number,
  timeoutMs: number,
): Promise<AgentMessage | null> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, 1500));
    const result = await client.listAgentMessages(chatId);
    if (!result.ok || !Array.isArray(result.data)) continue;

    for (const raw of result.data as unknown[]) {
      if (typeof raw !== "object" || !raw) continue;
      const item = raw as Record<string, unknown>;
      const meta = item.metadata as Record<string, unknown> | undefined;
      const payload = meta?.payload as Record<string, unknown> | undefined;
      if (
        payload?.schemaVersion &&
        typeof payload.sequence === "number" &&
        payload.sequence > afterSequence
      ) {
        return payload as unknown as AgentMessage;
      }
    }
  }
  return null;
}

async function runBandLive(
  scenario: ReturnType<typeof getScenario> & object,
  emit: (event: unknown) => void,
): Promise<{ continuation: string; messagesPosted: number } | null> {
  const config = getBandRuntimeConfig();
  if (!config.enabled || !config.bandLeaderAgentApiKey || config.dryRun) return null;

  const client = new BandRestClient(config);
  const verify = await client.verifyBandLeaderIdentity();
  if (!verify.ok) return null;

  // Create the Band chat room
  const chatResult = await client.createAgentChat();
  if (!chatResult.ok || !chatResult.data?.id) return null;
  const chatId = chatResult.data.id;

  // Register all configured agents
  for (const [agentId, agentConfig] of Object.entries(config.configuredAgents)) {
    if (agentConfig.participantId) {
      await client.addAgentParticipant(chatId, agentConfig.participantId);
    }
  }

  // Kick off the workflow by @mentioning the Band Leader
  const leaderConfig = config.configuredAgents["agent-commander"];
  const leaderMention = leaderConfig?.participantId
    ? [{ id: leaderConfig.participantId, name: "Band Leader", handle: leaderConfig.handle ?? "band-leader" }]
    : [];

  if (leaderMention.length === 0) return null;
  const leaderHandle = leaderMention[0]?.handle ?? "band-leader";

  await client.sendAgentTextMessage(
    chatId,
    `@${leaderHandle} Open incident ${scenario.caseId}: ${scenario.title}. Coordinate the full investigation.`,
    leaderMention,
  );

  emit({ type: "integration_status", mode: "live_band", band: chatId, model: "agents" });

  // Poll for messages as they arrive from the live agents
  let lastSequence = 0;
  let messagesPosted = 0;

  for (let i = 0; i < 14; i++) {
    const msg = await pollForReply(client, chatId, lastSequence, 12_000);
    if (!msg) break;

    lastSequence = msg.sequence;
    messagesPosted++;
    emit({ type: "agent_message", message: msg, mode: "live_band" });

    // Stop before approval gate to let the UI show the gate
    if (msg.type === "approval_request") {
      return { continuation: chatId, messagesPosted };
    }
  }

  return messagesPosted > 0 ? { continuation: chatId, messagesPosted } : null;
}

async function resumeBandLive(
  chatId: string,
  scenario: ReturnType<typeof getScenario> & object,
  emit: (event: unknown) => void,
): Promise<boolean> {
  const config = getBandRuntimeConfig();
  if (!config.enabled || !config.bandLeaderAgentApiKey || config.dryRun) return false;

  const client = new BandRestClient(config);

  // Post the approval decision event back to Band
  const decision = scenario.approvalDecision;
  const content = `Containment approved: ${decision.approvedActionScope.join(", ")}. Customer notification held.`;

  const leaderConfig = config.configuredAgents["agent-commander"];
  const leaderMention = leaderConfig?.participantId
    ? [{ id: leaderConfig.participantId, name: "Band Leader", handle: leaderConfig.handle ?? "band-leader" }]
    : [];

  if (leaderMention.length > 0) {
    const handle = leaderMention[0]?.handle ?? "band-leader";
    await client.sendAgentTextMessage(chatId, `@${handle} ${content}`, leaderMention);
  }

  // Poll for the remaining messages (remediation + report)
  let lastSequence = scenario.messages.findIndex((m) => m.type === "approval_request");
  let got = 0;

  for (let i = 0; i < 6; i++) {
    const msg = await pollForReply(client, chatId, lastSequence, 12_000);
    if (!msg) break;
    lastSequence = msg.sequence;
    got++;
    emit({ type: "agent_message", message: msg, mode: "live_band" });
    if (msg.type === "report_section") break;
  }

  return got > 0;
}

// ─── Verified replay path ────────────────────────────────────────────────────

async function runVerifiedReplay(
  scenario: ReturnType<typeof getScenario> & object,
  emit: (event: unknown) => void,
): Promise<string> {
  emit({ type: "fallback", mode: "verified_replay", reasonCode: "replay_path" });
  emit({ type: "integration_status", mode: "verified_replay", band: "local", model: "verified" });

  const preApproval = scenario.messages.filter((m) => m.type !== "approval_decision" && m.type !== "remediation_task" && m.type !== "report_section");

  for (const message of preApproval) {
    emit({ type: "agent_message", message, mode: "verified_replay" });
    if (message.type === "approval_request") break;
  }

  const approvalRequest = scenario.messages.find((m) => m.type === "approval_request");
  if (approvalRequest) {
    emit({
      type: "approval_required",
      continuation: "replay",
      request: approvalRequest,
      mode: "verified_replay",
    });
  }

  return "replay";
}

async function resumeVerifiedReplay(
  scenario: ReturnType<typeof getScenario> & object,
  emit: (event: unknown) => void,
): Promise<void> {
  emit({ type: "fallback", mode: "verified_replay", reasonCode: "replay_path" });

  const postApproval = scenario.messages.filter(
    (m) => m.type === "approval_decision" || m.type === "remediation_task" || m.type === "report_section",
  );

  for (const message of postApproval) {
    emit({ type: "agent_message", message, mode: "verified_replay" });
  }

  const finalReport = scenario.messages.findLast((m) => m.type === "report_section");
  if (finalReport) {
    emit({ type: "result", mode: "verified_replay", report: finalReport });
  }
}

// ─── Route handlers ──────────────────────────────────────────────────────────

export async function POST(request: Request): Promise<Response> {
  let body: { action?: string; scenarioId?: string; continuation?: string; decision?: string } = {};
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ type: "error", code: "bad_request", message: "Invalid JSON" }) + "\n", { status: 400 });
  }

  const scenarioId = (body.scenarioId ?? "INC-1042").toUpperCase() as ScenarioId;
  const scenario = getScenario(scenarioId);
  if (!scenario) {
    return new Response(JSON.stringify({ type: "error", code: "unknown_scenario", message: `Unknown scenario: ${scenarioId}` }) + "\n", { status: 400 });
  }

  // ── Approval continuation ────────────────────────────────────────────────
  if (body.action === "approve") {
    const continuation = body.continuation ?? "replay";

    return ndjsonStream(async (emit) => {
      if (continuation !== "replay") {
        // Try live Band first
        const ok = await resumeBandLive(continuation, scenario, emit).catch(() => false);
        if (ok) return;
      }
      // Verified replay fallback
      await resumeVerifiedReplay(scenario, emit);
    });
  }

  // ── Investigation start ──────────────────────────────────────────────────
  return ndjsonStream(async (emit) => {
    // Try Band live first
    const liveResult = await runBandLive(scenario, emit).catch(() => null);

    if (liveResult) {
      // Live agents responded — emit approval gate
      const approvalRequest = scenario.messages.find((m) => m.type === "approval_request");
      if (approvalRequest) {
        emit({
          type: "approval_required",
          continuation: liveResult.continuation,
          request: approvalRequest,
          mode: "live_band",
        });
      }
      return;
    }

    // Fall back to verified replay
    await runVerifiedReplay(scenario, emit);
  });
}
