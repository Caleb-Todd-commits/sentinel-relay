import type { AgentProfile } from "@/lib/types";
import type { WorkflowHandoff } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";

const handoffTone: Record<WorkflowHandoff["status"], "neutral" | "success" | "warning" | "danger" | "accent"> = {
  locked: "neutral",
  visible: "accent",
  complete: "success",
};

export function HandoffPanel({ handoffs, agents }: { handoffs: WorkflowHandoff[]; agents: AgentProfile[] }) {
  const agentName = (agentId: string) => agents.find((agent) => agent.id === agentId)?.shortName ?? agentId;

  return (
    <section className="relay-card" aria-labelledby="handoff-heading">
      <div className="flex items-center justify-between gap-3">
        <h2 id="handoff-heading" className="font-semibold">Agent Handoffs</h2>
        <Badge>{handoffs.filter((handoff) => handoff.status !== "locked").length}/{handoffs.length} visible</Badge>
      </div>
      <div className="mt-4 space-y-3">
        {handoffs.map((handoff) => (
          <article key={handoff.id} className={`rounded-xl border p-3 ${handoff.status === "locked" ? "border-slate-800 bg-slate-950/15 opacity-55" : "border-slate-700/80 bg-slate-950/25"}`}>
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-sm font-semibold">{handoff.title}</p>
                <p className="mt-1 text-xs text-slate-500">{agentName(handoff.fromAgentId)} to {agentName(handoff.toAgentId)}</p>
              </div>
              <Badge tone={handoffTone[handoff.status]}>{handoff.status}</Badge>
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-400">{handoff.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
