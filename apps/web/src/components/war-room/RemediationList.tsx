import type { AgentProfile, RemediationTask } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";

const statusTone: Record<RemediationTask["status"], "neutral" | "success" | "warning" | "danger" | "accent"> = {
  blocked: "danger",
  todo: "neutral",
  in_progress: "accent",
  review: "warning",
  done: "success",
  deferred: "neutral",
};

export function RemediationList({ tasks, agents, lockedCount = 0 }: { tasks: RemediationTask[]; agents: AgentProfile[]; lockedCount?: number }) {
  const agentName = (agentId: string) => agents.find((agent) => agent.id === agentId)?.shortName ?? agentId;

  return (
    <section className="relay-card" aria-labelledby="remediation-heading">
      <div className="flex items-center justify-between gap-3">
        <h2 id="remediation-heading" className="font-semibold">Remediation Tasks</h2>
        <div className="flex gap-2">
          <Badge>{tasks.length} visible</Badge>
          {lockedCount > 0 ? <Badge>{lockedCount} locked</Badge> : null}
        </div>
      </div>
      <div className="mt-4 space-y-3">
        {tasks.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-700 bg-slate-950/20 p-4 text-sm leading-6 text-slate-400">
            Remediation remains locked until the human approval gate is resolved.
          </div>
        ) : tasks.map((task) => (
          <article key={task.id} className="rounded-xl border border-slate-700/80 bg-slate-950/25 p-3">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-sm font-semibold leading-5">{task.title}</p>
                <p className="mt-1 text-xs text-slate-500">Owner: {agentName(task.ownerAgentId)}</p>
              </div>
              <Badge tone={statusTone[task.status]}>{task.status}</Badge>
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-400">{task.rationale}</p>
            {task.acceptanceCriteria.length ? (
              <ul className="mt-3 space-y-1 text-xs leading-5 text-slate-300">
                {task.acceptanceCriteria.slice(0, 2).map((criterion) => <li key={criterion}>• {criterion}</li>)}
              </ul>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
