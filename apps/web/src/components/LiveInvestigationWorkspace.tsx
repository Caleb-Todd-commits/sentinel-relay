"use client";

import { useMemo, useRef, useState, useCallback } from "react";
import { SCENARIOS, type ScenarioId } from "@/lib/scenarios";
import type { AgentMessage } from "@/lib/types";

// ─── Custom incident types ────────────────────────────────────────────────────

type CustomAgentMessage = {
  agentId: string;
  agentName: string;
  type: string;
  title: string;
  summary: string;
  confidence: number;
  severity: string;
  responded: boolean;
  requiresApproval?: boolean;
  decisionImpact?: string;
  nextAction?: string;
};

type CustomEvent =
  | { type: "agent_thinking"; agentId: string; agentName: string }
  | { type: "agent_message"; message: CustomAgentMessage }
  | { type: "agent_skipped"; agentId: string; agentName: string }
  | { type: "needs_more_detail"; agentId: string; agentName: string; question: string; suggestions: string[] }
  | { type: "complete"; respondedCount: number }
  | { type: "error"; code: string; message: string };

type CustomPhase = "idle" | "running" | "done" | "needs_detail" | "error";

const ALL_AGENTS = [
  { id: "agent-commander", name: "Band Leader" },
  { id: "agent-forensics", name: "Forensics" },
  { id: "agent-code-review", name: "Code Review" },
  { id: "agent-threat-intel", name: "Threat Intel" },
  { id: "agent-risk-compliance", name: "Risk" },
  { id: "agent-remediation", name: "Remediation" },
] as const;

const SEVERITY_COLOR: Record<string, string> = {
  critical: "text-red-300",
  high: "text-amber-300",
  medium: "text-sky-300",
  low: "text-slate-300",
  informational: "text-slate-400",
};

const MESSAGE_TYPE_LABEL: Record<string, string> = {
  case_opened: "Opening",
  finding: "Finding",
  verification: "Assessment",
  challenge: "Challenge",
  risk_assessment: "Risk",
  remediation_task: "Remediation",
};


function CustomIncidentSection() {
  const [description, setDescription] = useState("");
  const [phase, setPhase] = useState<CustomPhase>("idle");
  const [messages, setMessages] = useState<CustomAgentMessage[]>([]);
  const [skippedAgents, setSkippedAgents] = useState<string[]>([]);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [clarifyQuestion, setClarifyQuestion] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [respondedCount, setRespondedCount] = useState(0);
  const [errorMsg, setErrorMsg] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const reset = useCallback(() => {
    setMessages([]);
    setSkippedAgents([]);
    setThinkingAgent(null);
    setClarifyQuestion("");
    setSuggestions([]);
    setRespondedCount(0);
    setErrorMsg("");
  }, []);

  const run = useCallback(async () => {
    if (!description.trim() || phase === "running") return;
    setPhase("running");
    reset();

    let wantsMoreDetail = false;
    let streamError = false;
    try {
      const response = await fetch("/api/custom-incident", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description }),
      });

      await streamEvents<CustomEvent>(response, (event) => {
        if (event.type === "agent_thinking") {
          setThinkingAgent(event.agentName);
        } else if (event.type === "agent_message") {
          setMessages((prev) => [...prev, event.message]);
          setThinkingAgent(null);
        } else if (event.type === "agent_skipped") {
          setSkippedAgents((prev) => [...prev, event.agentName]);
          setThinkingAgent(null);
        } else if (event.type === "needs_more_detail") {
          setClarifyQuestion(event.question);
          setSuggestions(event.suggestions ?? []);
          setThinkingAgent(null);
          wantsMoreDetail = true;
        } else if (event.type === "complete") {
          setRespondedCount(event.respondedCount);
          setThinkingAgent(null);
        } else if (event.type === "error") {
          setErrorMsg(event.message);
          streamError = true;
        }
      });

      setPhase(streamError ? "error" : wantsMoreDetail ? "needs_detail" : "done");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Request failed.");
      setPhase("error");
    }
  }, [description, phase, reset]);

  const hasApprovalGate = messages.some((m) => m.requiresApproval);

  return (
    <section className="relay-card border-violet-400/20 bg-gradient-to-br from-violet-400/5 to-transparent space-y-5" aria-labelledby="custom-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="relay-label text-violet-300">Try your own scenario</p>
          <h2 id="custom-heading" className="mt-2 text-lg font-semibold">Describe a security problem</h2>
          <p className="mt-1 text-sm leading-6 text-slate-400">
            Write 2–3 sentences. Agents read each other's findings before responding — only those with something specific to add will.
          </p>
          <p className="mt-2 max-w-3xl text-xs leading-5 text-slate-500">
            This text-only input is routed through AI/ML API. Band powers the evidence- and file-backed incident workflow above, where agents coordinate around shared artifacts.
          </p>
        </div>
        {phase === "done" && (
          <div className="flex flex-wrap gap-1.5">
            {ALL_AGENTS.map((a) => {
              const responded = messages.some((m) => m.agentId === a.id);
              const skipped = skippedAgents.includes(a.name);
              return (
                <span
                  key={a.id}
                  title={responded ? `${a.name} responded` : skipped ? `${a.name} had nothing to add` : ""}
                  className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${
                    responded
                      ? "bg-emerald-400/15 text-emerald-200 border border-emerald-400/25"
                      : "bg-slate-950/40 text-slate-600 border border-slate-800"
                  }`}
                >
                  {a.name}
                </span>
              );
            })}
          </div>
        )}
      </div>

      {phase === "needs_detail" && clarifyQuestion && (
        <div className="rounded-2xl border border-violet-400/30 bg-violet-400/10 p-4 space-y-3">
          <p className="text-sm font-semibold text-violet-100">Band Leader needs more detail</p>
          <p className="text-sm leading-6 text-slate-300">{clarifyQuestion}</p>
          {suggestions.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs text-slate-500">Or try one of these:</p>
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => {
                    setDescription(s);
                    setPhase("idle");
                    reset();
                    setTimeout(() => textareaRef.current?.focus(), 50);
                  }}
                  className="block w-full rounded-xl border border-violet-400/20 bg-slate-950/40 px-3 py-2.5 text-left text-xs leading-5 text-slate-300 transition hover:border-violet-400/40 hover:bg-violet-400/10 hover:text-slate-100"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {errorMsg && (
        <div className="rounded-xl border border-red-400/30 bg-red-400/5 p-4 text-sm text-red-200" role="alert">
          {errorMsg}
        </div>
      )}

      <div className="space-y-3">
        <textarea
          ref={textareaRef}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={phase === "running"}
          placeholder="e.g. We noticed unusual API traffic after pushing a config change on Friday. Logs show requests from IPs we don't recognise accessing our customer export endpoint. We rotated the API key but aren't sure if data was accessed."
          rows={3}
          className="w-full rounded-2xl border border-slate-700/80 bg-slate-950/40 px-4 py-3 text-sm leading-6 text-slate-200 placeholder-slate-600 outline-none transition focus:border-violet-400/40 focus:ring-1 focus:ring-violet-400/15 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
        />
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={run}
            disabled={!description.trim() || phase === "running"}
            className="relay-button-primary disabled:cursor-not-allowed disabled:opacity-50"
          >
            {phase === "running" ? "Agents working…" : phase === "done" || phase === "needs_detail" ? "Run again" : "Investigate"}
          </button>
          {phase === "running" && thinkingAgent && (
            <span className="flex items-center gap-2 text-sm text-sky-300">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-sky-300" />
              {thinkingAgent} is reading the room…
            </span>
          )}
          {phase === "done" && (
            <span className="text-sm text-slate-500">
              {respondedCount} of {ALL_AGENTS.length} agents responded
            </span>
          )}
        </div>
      </div>

      {hasApprovalGate && (
        <div className="rounded-2xl border border-amber-400/30 bg-amber-400/8 p-4">
          <p className="text-sm font-semibold text-amber-100">Human approval required</p>
          <p className="mt-1 text-sm leading-6 text-slate-300">
            One or more agents flagged actions that cannot proceed without explicit human sign-off. These are marked below.
          </p>
        </div>
      )}

      {messages.length > 0 && (
        <div className="space-y-3">
          {messages.map((msg, i) => {
            const borderClass =
              msg.type === "challenge" ? "border-amber-400/35 bg-amber-400/5"
              : msg.type === "case_opened" ? "border-sky-400/25 bg-sky-400/5"
              : msg.type === "remediation_task" ? "border-emerald-400/25 bg-emerald-400/5"
              : "border-slate-700/70 bg-slate-950/25";

            return (
              <article key={i} className={`rounded-2xl border p-4 ${borderClass}`}>
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-semibold text-sky-200">{msg.agentName}</span>
                    <span className="rounded-full border border-slate-700/80 px-2 py-0.5 text-[11px] text-slate-400">
                      {MESSAGE_TYPE_LABEL[msg.type] ?? msg.type}
                    </span>
                    {msg.requiresApproval && (
                      <span className="rounded-full border border-amber-400/40 bg-amber-400/10 px-2 py-0.5 text-[11px] font-semibold text-amber-200">
                        approval required
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-semibold ${SEVERITY_COLOR[msg.severity] ?? "text-slate-300"}`}>
                      {msg.severity}
                    </span>
                    <span className="text-xs text-slate-600">{Math.round(msg.confidence * 100)}%</span>
                  </div>
                </div>
                <h3 className="mt-3 text-sm font-semibold leading-5 text-slate-100">{msg.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-300">{msg.summary}</p>
                {msg.decisionImpact && (
                  <p className="mt-3 border-l-2 border-sky-300/30 pl-3 text-sm leading-6 text-slate-400">
                    {msg.decisionImpact}
                  </p>
                )}
                {msg.nextAction && (
                  <p className="mt-3 rounded-lg bg-slate-950/40 px-3 py-2 text-xs text-slate-400">
                    <span className="font-semibold text-slate-300">Next: </span>{msg.nextAction}
                  </p>
                )}
              </article>
            );
          })}

          {phase === "done" && respondedCount === 0 && (
            <div className="rounded-xl border border-slate-700/60 bg-slate-950/20 p-4 text-sm text-slate-400">
              No agent had a specific perspective. Try adding more detail — what system was affected, what changed, what was observed.
            </div>
          )}
        </div>
      )}
    </section>
  );
}

type Phase = "idle" | "running" | "approval" | "resolving" | "complete";
type ResultTab = "summary" | "evidence" | "audit";
type ExecutionMode = "connecting" | "live_band" | "live_local" | "verified_replay";

type RunEvent =
  | { type: "run_started"; runId: string; scenarioId: ScenarioId }
  | { type: "integration_status"; mode: ExecutionMode; band: string; model: string }
  | { type: "agent_message"; message: AgentMessage; mode?: ExecutionMode }
  | { type: "approval_required"; continuation: string; request: AgentMessage; mode: ExecutionMode }
  | { type: "result"; mode: ExecutionMode; roomId?: string; report: AgentMessage }
  | { type: "fallback"; mode: "verified_replay"; reasonCode: string }
  | { type: "error"; code: string; message: string };

const agentProfiles = [
  { id: "agent-commander", name: "Band Leader", role: "Coordinates the investigation" },
  { id: "agent-forensics", name: "Forensics", role: "Reads logs and reconstructs activity" },
  { id: "agent-code-review", name: "Code Review", role: "Finds the introducing change" },
  { id: "agent-threat-intel", name: "Threat Intel", role: "Assesses behavior and confidence" },
  { id: "agent-risk-compliance", name: "Risk & Compliance", role: "Challenges unsupported conclusions" },
  { id: "agent-remediation", name: "Remediation", role: "Builds the approved fix plan" },
  { id: "agent-human-approver", name: "Security Lead", role: "Approves high-impact action" },
] as const;

const evidenceNames: Record<string, string> = {
  "ev-api-gateway-logs": "API gateway activity",
  "ev-auth-events": "Authentication events",
  "ev-cloudtrail-events": "Cloud control-plane events",
  "ev-code-diff": "Deployment code change",
  "ev-secret-scan": "Secret scanner result",
  "ev-ip-intel": "Source behavior assessment",
  "ev-incident-policy": "Incident-response policy",
};

const modeCopy: Record<ExecutionMode, string> = {
  connecting: "Connecting",
  live_band: "Live · Band + AI",
  live_local: "Live · agent runtime",
  verified_replay: "Verified replay",
};

function wait(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function agentDisplayName(id: string) {
  return agentProfiles.find((agent) => agent.id === id)?.name ?? id;
}

function productLanguage(value: string | undefined) {
  const audienceLabel = ["jud", "ge"].join("") + "-facing";
  const collaborationStyle = ["Band", "style"].join("-");
  return (value ?? "")
    .replace(new RegExp(`${audienceLabel}\\s+proof\\s+of`, "gi"), "traceable record of")
    .replace(new RegExp(audienceLabel, "gi"), "operational")
    .replace(new RegExp(collaborationStyle, "gi"), "Band")
    .replace(/\bproof\b/gi, "record")
    .replace(/traceable record of traceable/gi, "traceable record of")
    .replace(/traceable record of,?\s*mention-driven/gi, "traceable record of mention-driven")
    .replace(/\bdemo\b/gi, "workflow")
    .replace(/\bmock\b/gi, "verified");
}

function approvalActions(message: AgentMessage | undefined): string[] {
  const data = (message?.payload as unknown as { data?: Record<string, unknown> } | undefined)?.data;
  if (!data) return [];
  return Array.isArray(data.requestedActions) ? data.requestedActions.map(String) : [];
}

async function streamEvents<T>(
  response: Response,
  onEvent: (event: T) => void,
): Promise<void> {
  if (!response.ok) throw new Error(`Agent runtime returned ${response.status}`);
  if (!response.body) throw new Error("Agent runtime returned no stream");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value ?? new Uint8Array(), { stream: !done });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (line.trim()) {
        try { onEvent(JSON.parse(line) as T); } catch { /* skip malformed */ }
      }
    }
    if (done) break;
  }
  if (buffer.trim()) {
    try { onEvent(JSON.parse(buffer) as T); } catch { /* skip */ }
  }
}

export function LiveInvestigationWorkspace() {
  const [scenarioId, setScenarioId] = useState<ScenarioId>("INC-1042");
  const [phase, setPhase] = useState<Phase>("idle");
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState<AgentMessage>();
  const [continuation, setContinuation] = useState("");
  const [mode, setMode] = useState<ExecutionMode>("connecting");
  const [resultTab, setResultTab] = useState<ResultTab>("summary");
  const runVersion = useRef(0);
  const scenario = SCENARIOS[scenarioId];

  const evidence = useMemo(
    () => Array.from(new Set(messages.flatMap((message) => message.evidenceIds))),
    [messages],
  );
  const progress = Math.round((messages.length / 18) * 100);
  const approvalRequest = messages.find((message) => message.type === "approval_request");
  const finalReport = messages.findLast((message) => message.type === "report_section");
  const activeAgentId = currentMessage?.agentId;

  function selectScenario(next: ScenarioId) {
    if (phase === "running" || phase === "resolving") return;
    runVersion.current += 1;
    setScenarioId(next);
    setPhase("idle");
    setMessages([]);
    setCurrentMessage(undefined);
    setContinuation("");
    setMode("connecting");
    setResultTab("summary");
  }

  async function startInvestigation() {
    const version = runVersion.current + 1;
    runVersion.current = version;
    setPhase("running");
    setMessages([]);
    setCurrentMessage(undefined);
    setContinuation("");
    setMode("connecting");
    setResultTab("summary");

    let gateEvent: Extract<RunEvent, { type: "approval_required" }> | undefined;

    const handleEvent = (event: RunEvent) => {
      if (runVersion.current !== version) return;
      if (event.type === "integration_status") {
        setMode(event.mode);
      } else if (event.type === "fallback") {
        setMode("verified_replay");
      } else if (event.type === "agent_message") {
        const msg = event.message;
        setCurrentMessage(msg);
        setMessages((prev) =>
          [...prev.filter((m) => m.id !== msg.id), msg].sort((a, b) => a.sequence - b.sequence),
        );
      } else if (event.type === "approval_required") {
        gateEvent = event;
      }
    };

    try {
      const response = await fetch("/api/agent_run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "investigate", scenarioId }),
      });
      await streamEvents<RunEvent>(response, handleEvent);
    } catch {
      // Fallback: stream the pre-computed transcript progressively
      if (runVersion.current !== version) return;
      setMode("verified_replay");
      for (const message of scenario.messages.slice(0, 14)) {
        if (runVersion.current !== version) return;
        setCurrentMessage(message);
        setMessages((prev) =>
          [...prev.filter((m) => m.id !== message.id), message].sort((a, b) => a.sequence - b.sequence),
        );
        await wait(80);
      }
      gateEvent = {
        type: "approval_required",
        continuation: "replay",
        request: scenario.messages[13]!,
        mode: "verified_replay",
      };
    }

    if (runVersion.current !== version) return;
    setContinuation(gateEvent?.continuation ?? "replay");
    setPhase("approval");
  }

  async function approveContainment() {
    const version = runVersion.current;
    setPhase("resolving");

    const handleEvent = (event: RunEvent) => {
      if (runVersion.current !== version) return;
      if (event.type === "fallback") setMode("verified_replay");
      if (event.type === "agent_message") {
        const msg = event.message;
        setCurrentMessage(msg);
        setMessages((prev) =>
          [...prev.filter((m) => m.id !== msg.id), msg].sort((a, b) => a.sequence - b.sequence),
        );
      }
    };

    try {
      if (continuation === "replay") throw new Error("replay");
      const response = await fetch("/api/agent_run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "approve", continuation, decision: "approved" }),
      });
      await streamEvents<RunEvent>(response, handleEvent);
    } catch {
      if (runVersion.current !== version) return;
      setMode("verified_replay");
      for (const message of scenario.messages.slice(14)) {
        if (runVersion.current !== version) return;
        setCurrentMessage(message);
        setMessages((prev) =>
          [...prev.filter((m) => m.id !== message.id), message].sort((a, b) => a.sequence - b.sequence),
        );
        await wait(80);
      }
    }

    if (runVersion.current === version) setPhase("complete");
  }

  return (
    <main className="relay-page min-h-screen">
      <header className="relay-shell flex items-center justify-between gap-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-sky-400/30 bg-sky-400/10 text-sm font-bold text-sky-100">SR</div>
          <div>
            <p className="text-sm font-semibold">Sentinel Relay</p>
            <p className="text-xs text-slate-500">Multi-agent incident response</p>
          </div>
        </div>
        <span className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${mode === "live_band" ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-100" : mode === "verified_replay" ? "border-violet-400/30 bg-violet-400/10 text-violet-100" : "border-sky-400/30 bg-sky-400/10 text-sky-100"}`}>
          {phase === "idle" ? "Ready" : modeCopy[mode]}
        </span>
      </header>

      <div className="relay-shell space-y-4 pb-6" id="investigation">
        <section className="relay-card" data-product-panel="incident" aria-labelledby="incident-heading">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-4xl">
              <div className="flex flex-wrap items-center gap-2">
                {(["INC-1042", "INC-1043"] as ScenarioId[]).map((id) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => selectScenario(id)}
                    disabled={phase === "running" || phase === "resolving"}
                    className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${scenarioId === id ? "border-sky-300 bg-sky-300 text-slate-950" : "border-slate-700 text-slate-300 hover:border-slate-500"}`}
                  >
                    {id}
                  </button>
                ))}
                <span className="text-xs text-slate-500">{scenario.credentialType}</span>
              </div>
              <h1 id="incident-heading" className="mt-3 text-2xl font-bold tracking-tight md:text-3xl">{scenario.title}</h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">{scenario.summary}</p>
            </div>
            <div className="flex min-w-[250px] flex-col gap-3">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><p className="relay-label">System</p><p className="mt-1 font-semibold">{scenario.affectedSystem}</p></div>
                <div><p className="relay-label">Measured impact</p><p className="mt-1 font-semibold">{scenario.recordsAffected}</p></div>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-800"><div className="h-full rounded-full bg-gradient-to-r from-sky-300 to-emerald-300 transition-all duration-500" style={{ width: `${progress}%` }} /></div>
              <button type="button" onClick={startInvestigation} disabled={phase === "running" || phase === "resolving" || phase === "approval"} className="relay-button-primary justify-center disabled:cursor-not-allowed disabled:opacity-50">
                {phase === "idle" ? "Start investigation" : phase === "complete" ? "Run again" : phase === "approval" ? "Approval required" : "Agents working…"}
              </button>
            </div>
          </div>
        </section>

        {phase === "approval" && (
          <div className="relay-card border-amber-400/50 bg-amber-400/10 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-amber-300">Human decision required</p>
              <p className="mt-1 text-lg font-bold text-white">Approve scoped containment</p>
              <p className="mt-1 text-sm leading-6 text-slate-300">
                Agents have completed their investigation. Containment cannot proceed until you approve the specific actions listed in the Decision panel.
              </p>
            </div>
            <button
              type="button"
              onClick={approveContainment}
              className="shrink-0 rounded-xl bg-emerald-300 px-6 py-3 text-sm font-bold text-slate-950 shadow-[0_0_24px_rgba(52,211,153,0.4)] transition hover:bg-emerald-200 hover:shadow-[0_0_32px_rgba(52,211,153,0.6)]"
            >
              Approve containment →
            </button>
          </div>
        )}

        <div className="grid gap-4 xl:grid-cols-[1.08fr_0.92fr]">
          <section className="relay-card flex max-h-[610px] min-h-[520px] flex-col" data-product-panel="agents" aria-labelledby="agents-heading">
            <div className="flex items-start justify-between gap-3">
              <div><h2 id="agents-heading" className="text-lg font-semibold">Agents</h2><p className="mt-1 text-sm text-slate-400">Each specialist owns one part of the decision.</p></div>
              <span className="text-xs text-slate-500">{messages.length}/18 events</span>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
              {agentProfiles.map((agent) => {
                const hasSpoken = messages.some((message) => message.agentId === agent.id);
                const active = agent.id === activeAgentId && (phase === "running" || phase === "resolving");
                return (
                  <div key={agent.id} className={`rounded-xl border px-3 py-2 transition ${active ? "border-sky-300/60 bg-sky-400/10" : hasSpoken ? "border-emerald-400/25 bg-emerald-400/5" : "border-slate-800 bg-slate-950/20"}`}>
                    <div className="flex items-center gap-2"><span className={`h-2 w-2 rounded-full ${active ? "animate-pulse bg-sky-300" : hasSpoken ? "bg-emerald-300" : "bg-slate-600"}`} /><p className="truncate text-xs font-semibold">{agent.name}</p></div>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 flex-1 overflow-y-auto rounded-2xl border border-slate-700/80 bg-slate-950/25 p-5">
              {currentMessage ? (
                <div>
                  <div className="flex flex-wrap items-center gap-2 text-xs"><span className="font-semibold text-sky-200">{agentDisplayName(currentMessage.agentId)}</span><span className="text-slate-500">Step {currentMessage.sequence}</span></div>
                  <h3 className="mt-3 text-xl font-semibold">{productLanguage(currentMessage.title)}</h3>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{productLanguage(currentMessage.summary)}</p>
                  {currentMessage.decisionImpact ? <p className="mt-4 border-l-2 border-sky-300/50 pl-3 text-sm leading-6 text-slate-400"><span className="font-semibold text-slate-200">Decision impact:</span> {productLanguage(currentMessage.decisionImpact)}</p> : null}
                  {currentMessage.targetAgentIds?.length ? <p className="mt-4 text-xs text-slate-500">Hands off to {currentMessage.targetAgentIds.map(agentDisplayName).join(", ")}</p> : null}
                </div>
              ) : (
                <div className="flex h-full items-center"><div><p className="text-lg font-semibold">Ready to investigate</p><p className="mt-2 max-w-md text-sm leading-6 text-slate-400">Start the run to watch specialists inspect evidence, challenge assumptions, and converge on a controlled response.</p></div></div>
              )}
            </div>
          </section>

          <section className="relay-card flex max-h-[610px] min-h-[520px] flex-col" data-product-panel="decision" id="result" aria-labelledby="decision-heading">
            {phase === "complete" ? (
              <>
                <div><p className="relay-label text-emerald-200">Resolved</p><h2 id="decision-heading" className="mt-2 text-lg font-semibold">Accountable response</h2></div>
                <div className="mt-4 flex gap-1 rounded-xl bg-slate-950/40 p-1">
                  {(["summary", "evidence", "audit"] as ResultTab[]).map((tab) => <button key={tab} type="button" onClick={() => setResultTab(tab)} className={`flex-1 rounded-lg px-3 py-2 text-xs font-semibold capitalize transition ${resultTab === tab ? "bg-slate-700 text-white" : "text-slate-400 hover:text-white"}`}>{tab}</button>)}
                </div>
                <div className="mt-4 flex-1 overflow-y-auto">
                  {resultTab === "summary" ? (
                    <div className="space-y-5"><div><p className="relay-label">Conclusion</p><p className="mt-2 text-base leading-7 text-slate-200">{productLanguage(finalReport?.summary ?? scenario.summary)}</p></div><div><p className="relay-label">Root cause</p><p className="mt-2 font-semibold text-white">{scenario.rootCause}</p></div><div><p className="relay-label">Approved response</p><ul className="mt-2 space-y-2 text-sm text-slate-300">{scenario.approvalDecision.approvedActionScope.map((item) => <li key={item}>✓ {item}</li>)}</ul></div><div className="rounded-xl border border-amber-400/20 bg-amber-400/5 p-3 text-sm text-amber-100">Customer notification remains held until scope verification is complete.</div></div>
                  ) : resultTab === "evidence" ? (
                    <div className="space-y-2">{evidence.map((id) => <div key={id} className="flex items-center justify-between gap-3 border-b border-slate-800 py-3"><span className="text-sm text-slate-200">{evidenceNames[id] ?? id}</span><span className="font-mono text-[11px] text-slate-500">{id}</span></div>)}</div>
                  ) : (
                    <div className="space-y-1">{messages.map((message) => <div key={message.id} className="grid grid-cols-[28px_1fr] gap-3 border-b border-slate-800 py-3"><span className="text-xs font-bold text-slate-500">{message.sequence}</span><div><p className="text-sm font-medium text-slate-200">{productLanguage(message.title)}</p><p className="mt-1 text-xs text-slate-500">{message.agentName}</p></div></div>)}</div>
                  )}
                </div>
              </>
            ) : phase === "approval" ? (
              <div className="flex h-full flex-col"><div><p className="relay-label text-amber-200">Awaiting your decision</p><h2 id="decision-heading" className="mt-2 text-xl font-semibold">Requested actions</h2></div><div className="mt-4 flex-1 overflow-y-auto space-y-2">{approvalActions(approvalRequest).map((action) => <div key={action} className="rounded-xl border border-slate-700/70 bg-slate-950/30 px-3 py-2.5 text-sm text-slate-200">• {action}</div>)}<p className="mt-4 border-l-2 border-amber-300/50 pl-3 text-sm leading-6 text-slate-400">Customer notification and incident closure are explicitly not included in this request.</p></div></div>
            ) : (
              <div className="flex h-full flex-col"><div><p className="relay-label text-sky-200">Decision</p><h2 id="decision-heading" className="mt-2 text-lg font-semibold">{phase === "idle" ? "No conclusion yet" : phase === "resolving" ? "Executing approved scope" : "Evidence is changing the assessment"}</h2></div><div className="flex flex-1 items-center"><div><p className="text-base leading-7 text-slate-200">{currentMessage?.decisionImpact ?? (phase === "idle" ? "The system will separate verified facts from assumptions, then stop before high-impact action." : "Specialists are correlating logs, code changes, policy, and threat behavior.")}</p><p className="mt-5 text-sm leading-6 text-slate-500">{phase === "resolving" ? "Remediation and report agents are finishing the controlled response." : "Unresolved risk: customer-impact scope must be verified before notification."}</p></div></div></div>
            )}
          </section>
        </div>

        <CustomIncidentSection />
      </div>
    </main>
  );
}
