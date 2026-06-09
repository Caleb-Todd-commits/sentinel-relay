import type { WorkflowDecision } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";

const decisionTone: Record<WorkflowDecision["status"], "neutral" | "success" | "warning" | "danger" | "accent"> = {
  locked: "neutral",
  pending: "warning",
  approved: "success",
  deferred: "accent",
};

export function DecisionPanel({ decisions }: { decisions: WorkflowDecision[] }) {
  return (
    <section className="relay-card" aria-labelledby="decision-panel-heading">
      <div className="flex items-center justify-between gap-3">
        <h2 id="decision-panel-heading" className="font-semibold">Decision Board</h2>
        <Badge>{decisions.filter((decision) => decision.status !== "locked").length} active</Badge>
      </div>
      <div className="mt-4 space-y-3">
        {decisions.map((decision) => (
          <article key={decision.id} className={`rounded-xl border p-3 ${decision.status === "locked" ? "border-slate-800 bg-slate-950/15 opacity-55" : "border-slate-700/80 bg-slate-950/25"}`}>
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-sm font-semibold leading-5">{decision.title}</p>
                <p className="mt-1 text-xs text-slate-500">Owner: {decision.owner}</p>
              </div>
              <Badge tone={decisionTone[decision.status]}>{decision.status}</Badge>
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-400">{decision.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
