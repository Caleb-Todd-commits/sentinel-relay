import type { AgentMessage, AgentProfile, EvidenceReference } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { asPercent, formatMessageType, formatSeverity } from "@/lib/utils/format";

const typeTone: Record<AgentMessage["type"], "neutral" | "success" | "warning" | "danger" | "accent"> = {
  case_opened: "accent",
  room_created: "accent",
  agent_joined: "neutral",
  task_assignment: "accent",
  finding: "warning",
  challenge: "danger",
  verification: "neutral",
  risk_assessment: "warning",
  approval_request: "warning",
  approval_decision: "success",
  remediation_task: "success",
  report_section: "accent",
  state_update: "neutral",
  handoff: "accent",
  watchdog_alert: "danger",
};

function evidenceTitle(evidence: EvidenceReference[], id: string): string {
  return evidence.find((item) => item.id === id)?.title ?? id;
}

function agentName(agents: AgentProfile[] | undefined, id: string): string {
  return agents?.find((agent) => agent.id === id)?.shortName ?? id;
}

function payloadSummary(message: AgentMessage): string | undefined {
  if (!message.payload) return undefined;

  switch (message.payload.kind) {
    case "finding":
      return `Claim: ${message.payload.data.claim}`;
    case "challenge":
      return `Challenge: ${message.payload.data.reason}`;
    case "risk_assessment":
      return `Risk: ${message.payload.data.rationale}`;
    case "task_assignment":
      return `Task: ${message.payload.data.objective}`;
    case "handoff":
      return `Handoff: ${message.payload.data.contextSummary}`;
    case "generic":
      return undefined;
    default:
      return undefined;
  }
}

function payloadDetails(message: AgentMessage): string[] {
  if (!message.payload) return [];

  switch (message.payload.kind) {
    case "finding":
      return [
        ...message.payload.data.limitations.map((item) => `Limitation: ${item}`),
        ...message.payload.data.requestedVerifications.map((item) => `Verify: ${item}`),
      ];
    case "challenge":
      return [
        `Blocking: ${message.payload.data.blocking ? "yes" : "no"}`,
        `Required next step: ${message.payload.data.requiredNextStep}`,
      ];
    case "risk_assessment":
      return [
        `Recommended severity: ${message.payload.data.recommendedSeverity}`,
        `Escalation required: ${message.payload.data.escalationRequired ? "yes" : "no"}`,
        ...message.payload.data.requiredApprovals.map((item) => `Approval: ${item}`),
      ];
    case "task_assignment":
      return [
        `Expected output: ${message.payload.data.expectedOutput}`,
        ...message.payload.data.acceptanceCriteria.map((item) => `Criteria: ${item}`),
      ];
    case "handoff":
      return [`Reason: ${message.payload.data.reason}`];
    case "generic":
      return Object.entries(message.payload.data).slice(0, 3).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : String(value)}`);
    default:
      return [];
  }
}

export function MessageStream({ messages, evidence, agents }: { messages: AgentMessage[]; evidence: EvidenceReference[]; agents?: AgentProfile[] }) {
  return (
    <section className="relay-card" aria-labelledby="message-stream-heading">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 id="message-stream-heading" className="font-semibold">Band Collaboration Stream</h2>
          <p className="mt-1 text-sm text-slate-400">Structured handoffs, challenges, approvals, and report events.</p>
        </div>
        <Badge tone="accent">{messages.length} visible messages</Badge>
      </div>

      {messages.length === 0 ? (
        <div className="mt-5 rounded-2xl border border-dashed border-slate-700 bg-slate-950/20 p-5 text-sm leading-6 text-slate-400">
          Start the incident to open the shared room and begin the Band-style coordination stream.
        </div>
      ) : (
        <div className="mt-5 space-y-4">
          {messages.map((message) => {
            const structuredPayloadSummary = payloadSummary(message);
            const details = payloadDetails(message);
            const isCritical = message.type === "challenge" || message.type === "approval_request" || message.type === "approval_decision";

            return (
              <article key={message.id} className={`relay-message-card ${isCritical ? "relay-message-card-critical" : ""}`}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-600 bg-slate-950 text-xs font-bold text-slate-300">{message.sequence}</span>
                      <p className="text-sm font-semibold">{message.agentName}</p>
                      <Badge tone={typeTone[message.type]}>{formatMessageType(message.type)}</Badge>
                    </div>
                    <p className="mt-2 text-xs text-slate-500">{message.createdAt} · {message.id}</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Badge tone={message.severity === "high" || message.severity === "critical" ? "warning" : "neutral"}>{formatSeverity(message.severity)}</Badge>
                    <Badge>{asPercent(message.confidence)} confidence</Badge>
                    <Badge>{message.visibility}</Badge>
                  </div>
                </div>

                <h3 className="mt-4 text-base font-semibold leading-6">{message.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-300">{message.summary}</p>

                <div className="mt-4 grid gap-3 lg:grid-cols-2">
                  {structuredPayloadSummary ? (
                    <div className="rounded-xl border border-violet-400/20 bg-violet-400/5 p-3">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-violet-200">Structured payload</p>
                      <p className="mt-1 text-sm leading-6 text-slate-300">{structuredPayloadSummary}</p>
                    </div>
                  ) : null}

                  {message.decisionImpact ? (
                    <div className="rounded-xl border border-sky-400/20 bg-sky-400/5 p-3">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-sky-200">Decision impact</p>
                      <p className="mt-1 text-sm leading-6 text-slate-300">{message.decisionImpact}</p>
                    </div>
                  ) : null}
                </div>

                {details.length ? (
                  <div className="mt-4 rounded-xl border border-slate-700/80 bg-slate-950/25 p-3">
                    <p className="relay-label">Payload details</p>
                    <ul className="mt-2 grid gap-1 text-xs leading-5 text-slate-300 md:grid-cols-2">
                      {details.slice(0, 6).map((detail) => <li key={detail}>• {detail}</li>)}
                    </ul>
                  </div>
                ) : null}

                <div className="mt-4 flex flex-wrap gap-2">
                  {message.targetAgentIds?.map((id) => (
                    <span key={id} className="rounded-lg border border-slate-700 bg-slate-900/80 px-2 py-1 text-xs text-slate-300">
                      to: {agentName(agents, id)}
                    </span>
                  ))}
                  {message.evidenceIds.map((id) => (
                    <span key={id} className="rounded-lg border border-slate-700 bg-slate-900/80 px-2 py-1 text-xs text-slate-300">
                      evidence: {evidenceTitle(evidence, id)}
                    </span>
                  ))}
                  {message.correlationId ? (
                    <span className="rounded-lg border border-slate-700 bg-slate-950/80 px-2 py-1 font-mono text-[11px] text-slate-500">
                      {message.correlationId}
                    </span>
                  ) : null}
                </div>

                {message.nextAction ? (
                  <p className="mt-4 rounded-xl border border-slate-700/80 bg-slate-950/25 p-3 text-sm text-slate-400"><span className="font-semibold text-slate-300">Next:</span> {message.nextAction}</p>
                ) : null}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
