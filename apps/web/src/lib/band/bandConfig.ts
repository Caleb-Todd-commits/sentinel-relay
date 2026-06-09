import type { AgentProfile } from "@/lib/types";
import type { BandConfiguredAgent, BandRuntimeConfig } from "./bandTypes";

const DEFAULT_BAND_REST_URL = "https://app.band.ai/api/v1";
const DEFAULT_BAND_WS_URL = "wss://app.band.ai/api/v1/socket/websocket";

const agentEnvSuffixes: Record<string, string> = {
  "agent-commander": "COMMANDER",
  "agent-forensics": "FORENSICS",
  "agent-threat-intel": "THREAT_INTEL",
  "agent-code-review": "CODE_REVIEW",
  "agent-risk-compliance": "RISK_COMPLIANCE",
  "agent-remediation": "REMEDIATION",
};

function cleanEnv(value: string | undefined): string | undefined {
  if (!value) return undefined;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

function readEnv(...names: string[]): string | undefined {
  for (const name of names) {
    const value = cleanEnv(process.env[name]);
    if (value) return value;
  }
  return undefined;
}

function normalizeBaseUrl(value: string | undefined): string {
  const raw = cleanEnv(value) ?? DEFAULT_BAND_REST_URL;
  return raw.replace(/\/$/, "").replace(/\/agent$/, "").replace(/\/me$/, "");
}

function buildConfiguredAgents(): Record<string, BandConfiguredAgent> {
  const configuredAgents: Record<string, BandConfiguredAgent> = {};

  for (const [sentinelAgentId, envSuffix] of Object.entries(agentEnvSuffixes)) {
    configuredAgents[sentinelAgentId] = {
      sentinelAgentId,
      envSuffix,
      name: readEnv(`BAND_${envSuffix}_NAME`) ?? sentinelAgentId,
      handle: readEnv(`BAND_${envSuffix}_HANDLE`),
      participantId: readEnv(`BAND_${envSuffix}_PARTICIPANT_ID`, `BAND_${envSuffix}_AGENT_ID`),
      apiKey: readEnv(`BAND_${envSuffix}_AGENT_API_KEY`, `${envSuffix}_API_KEY`),
    };
  }

  return configuredAgents;
}

export function getBandRuntimeConfig(): BandRuntimeConfig {
  const baseUrl = normalizeBaseUrl(readEnv("BAND_API_BASE_URL", "THENVOI_REST_URL"));
  const wsUrl = readEnv("BAND_WS_URL", "THENVOI_WS_URL") ?? DEFAULT_BAND_WS_URL;
  const commanderAgentApiKey = readEnv("BAND_COMMANDER_AGENT_API_KEY", "COMMANDER_AGENT_API_KEY", "BAND_AGENT_API_KEY");
  const humanApiKey = readEnv("BAND_HUMAN_API_KEY");
  const commanderAgentId = readEnv("BAND_COMMANDER_PARTICIPANT_ID", "BAND_COMMANDER_AGENT_ID");
  const dashboardHumanParticipantId = readEnv("BAND_DASHBOARD_HUMAN_PARTICIPANT_ID", "BAND_HUMAN_PARTICIPANT_ID");
  const enabled = process.env.BAND_PROVIDER_ENABLED === "true" || process.env.NEXT_PUBLIC_ENABLE_BAND_MODE === "true";
  const dryRun = process.env.BAND_DRY_RUN === "true";
  const configuredAgents = buildConfiguredAgents();
  const missingRequired: string[] = [];
  const warnings: string[] = [];

  if (!enabled) {
    warnings.push("BAND_PROVIDER_ENABLED/NEXT_PUBLIC_ENABLE_BAND_MODE is not true, so server routes will report Band as not enabled.");
  }
  if (!commanderAgentApiKey) {
    missingRequired.push("BAND_COMMANDER_AGENT_API_KEY");
  }
  if (!commanderAgentId && !configuredAgents["agent-commander"]?.participantId) {
    warnings.push("No commander participant id configured. Chat creation can work, but @mentions from the dashboard may be limited.");
  }
  if (!humanApiKey) {
    warnings.push("BAND_HUMAN_API_KEY is not set. The dashboard will use its local mirror for full-room history instead of Human API reads.");
  }

  return {
    enabled,
    baseUrl,
    wsUrl,
    commanderAgentApiKey,
    humanApiKey,
    commanderAgentId,
    dashboardHumanParticipantId,
    dryRun,
    configuredAgents,
    missingRequired,
    warnings,
  };
}

export function getConfiguredAgentForProfile(agent: AgentProfile | string, config = getBandRuntimeConfig()): BandConfiguredAgent | undefined {
  const sentinelAgentId = typeof agent === "string" ? agent : agent.id;
  return config.configuredAgents[sentinelAgentId];
}

export function isBandReady(config = getBandRuntimeConfig()): boolean {
  return config.enabled && (config.dryRun || Boolean(config.commanderAgentApiKey));
}

export function getBandConfigurationSummary(config = getBandRuntimeConfig()) {
  return {
    enabled: config.enabled,
    baseUrl: config.baseUrl,
    wsUrl: config.wsUrl,
    dryRun: config.dryRun,
    hasCommanderAgentApiKey: Boolean(config.commanderAgentApiKey),
    hasHumanApiKey: Boolean(config.humanApiKey),
    configuredParticipantCount: Object.values(config.configuredAgents).filter((agent) => agent.participantId).length,
    missingRequired: config.missingRequired,
    warnings: config.warnings,
  };
}
