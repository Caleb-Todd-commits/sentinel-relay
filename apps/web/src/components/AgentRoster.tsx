import type { AgentProfile } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";

const statusTone: Record<AgentProfile["status"], "neutral" | "success" | "warning" | "danger" | "accent"> = {
  offline: "danger",
  idle: "neutral",
  assigned: "accent",
  working: "accent",
  challenging: "warning",
  waiting: "warning",
  blocked: "danger",
  complete: "success",
};

const dotClass: Record<AgentProfile["status"], string> = {
  offline: "bg-red-300",
  idle: "bg-slate-500",
  assigned: "bg-sky-300",
  working: "bg-sky-300 shadow-[0_0_18px_rgba(125,211,252,0.45)]",
  challenging: "bg-amber-300 shadow-[0_0_18px_rgba(252,211,77,0.45)]",
  waiting: "bg-amber-200",
  blocked: "bg-red-300 shadow-[0_0_18px_rgba(252,165,165,0.45)]",
  complete: "bg-emerald-300",
};

export function AgentRoster({ agents }: { agents: AgentProfile[] }) {
  return (
    <section className="relay-card" aria-labelledby="agent-roster-heading">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 id="agent-roster-heading" className="font-semibold">Agent Roster</h2>
          <p className="mt-1 text-xs text-slate-500">Role-separated participants in the shared incident room.</p>
        </div>
        <Badge>{agents.length} agents</Badge>
      </div>
      <div className="mt-4 space-y-3">
        {agents.map((agent) => (
          <article key={agent.id} className="rounded-2xl border border-slate-700/80 bg-slate-950/25 p-3 transition hover:border-slate-500/80">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`h-2.5 w-2.5 rounded-full ${dotClass[agent.status]}`} />
                  <p className="font-medium leading-tight">{agent.shortName}</p>
                </div>
                <p className="mt-1 text-xs text-slate-500">{agent.role}</p>
              </div>
              <Badge tone={statusTone[agent.status]}>{agent.status}</Badge>
            </div>
            {agent.currentTask ? <p className="mt-3 text-xs leading-5 text-slate-400">{agent.currentTask}</p> : null}
            <div className="mt-3 flex flex-wrap gap-1.5">
              <span className="rounded-md border border-slate-700 bg-slate-950/70 px-2 py-1 text-[11px] text-slate-400">{agent.capability}</span>
              {agent.requiresHumanApprovalFor.length ? (
                <span className="rounded-md border border-amber-400/20 bg-amber-400/10 px-2 py-1 text-[11px] text-amber-100">approval-bound</span>
              ) : null}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
