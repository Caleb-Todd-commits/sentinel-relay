import type { AgentProfile } from "@/lib/types";
import type { WorkflowHandoff, WorkflowStepDefinition } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";

const statusTone: Record<WorkflowHandoff["status"], "neutral" | "success" | "warning" | "danger" | "accent"> = {
  locked: "neutral",
  visible: "accent",
  complete: "success",
};

export function CollaborationMap({ agents, handoffs, currentStep }: { agents: AgentProfile[]; handoffs: WorkflowHandoff[]; currentStep: WorkflowStepDefinition }) {
  const activeIds = new Set(currentStep.activeAgentIds);
  const activeHandoffs = handoffs.filter((handoff) => handoff.status !== "locked");
  const agentName = (agentId: string) => agents.find((agent) => agent.id === agentId)?.shortName ?? agentId;

  return (
    <section className="relay-card" aria-labelledby="collaboration-map-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="collaboration-map-heading" className="font-semibold">Agent Collaboration Map</h2>
          <p className="mt-1 text-sm text-slate-400">The visible handoff graph that judges should understand in one glance.</p>
        </div>
        <Badge tone="accent">{activeHandoffs.length} handoffs unlocked</Badge>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-3 xl:grid-cols-6">
        {agents.map((agent) => (
          <article key={agent.id} className={`rounded-2xl border p-3 ${activeIds.has(agent.id) ? "border-sky-400/40 bg-sky-400/10" : "border-slate-700/70 bg-slate-950/25"}`}>
            <div className="flex items-center justify-between gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${activeIds.has(agent.id) ? "bg-sky-300" : agent.status === "complete" ? "bg-emerald-300" : agent.status === "blocked" ? "bg-red-300" : "bg-slate-500"}`} />
              <Badge tone={agent.status === "complete" ? "success" : agent.status === "blocked" ? "danger" : activeIds.has(agent.id) ? "accent" : "neutral"}>{agent.status}</Badge>
            </div>
            <h3 className="mt-3 text-sm font-semibold leading-5">{agent.shortName}</h3>
            <p className="mt-1 text-[11px] leading-4 text-slate-500">{agent.capability}</p>
          </article>
        ))}
      </div>

      <div className="mt-5 space-y-2">
        {activeHandoffs.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/20 p-4 text-sm leading-6 text-slate-400">
            Handoffs unlock after the commander assigns specialist work and agents start sharing evidence.
          </div>
        ) : (
          activeHandoffs.map((handoff) => (
            <article key={handoff.id} className="grid gap-3 rounded-2xl border border-slate-700/70 bg-slate-950/25 p-3 md:grid-cols-[160px_1fr_120px] md:items-center">
              <div className="text-xs font-semibold text-slate-200">{agentName(handoff.fromAgentId)} → {agentName(handoff.toAgentId)}</div>
              <div>
                <p className="text-sm font-semibold text-slate-100">{handoff.title}</p>
                <p className="mt-1 text-xs leading-5 text-slate-400">{handoff.summary}</p>
              </div>
              <Badge tone={statusTone[handoff.status]}>{handoff.status}</Badge>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
