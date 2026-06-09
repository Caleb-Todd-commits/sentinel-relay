import type { WorkflowViewModel } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";

function stageState(workflow: WorkflowViewModel, threshold: number) {
  if (workflow.stepIndex < threshold) return "locked";
  if (workflow.stepIndex === threshold) return "active";
  return "complete";
}

const stageTone = {
  locked: "neutral",
  active: "warning",
  complete: "success",
} as const;

const stages = [
  {
    threshold: 3,
    title: "Evidence emerges",
    body: "Forensics posts suspicious token usage with cited log evidence.",
  },
  {
    threshold: 6,
    title: "Risk challenges",
    body: "Risk blocks the unsupported customer-impact claim instead of rubber-stamping it.",
  },
  {
    threshold: 7,
    title: "Human gate opens",
    body: "Commander requests approval before containment can proceed.",
  },
  {
    threshold: 8,
    title: "Scoped approval",
    body: "Containment is approved, but customer notification is explicitly deferred.",
  },
];

export function CriticalMomentCard({ workflow }: { workflow: WorkflowViewModel }) {
  const challengeReached = workflow.stepIndex >= 6;
  const approvalReached = workflow.stepIndex >= 8;

  return (
    <section className="relay-card relay-critical-card" aria-labelledby="critical-moment-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Badge tone={challengeReached ? "warning" : "neutral"}>Winning demo moment</Badge>
          <h2 id="critical-moment-heading" className="mt-3 text-lg font-semibold">Challenge → approval → constrained action</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
            This is the moment that proves multi-agent coordination: one agent limits another agent&apos;s conclusion, the commander escalates, and remediation only acts inside the approved scope.
          </p>
        </div>
        <Badge tone={approvalReached ? "success" : challengeReached ? "warning" : "neutral"}>
          {approvalReached ? "resolved" : challengeReached ? "active" : "pending"}
        </Badge>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-4">
        {stages.map((stage) => {
          const state = stageState(workflow, stage.threshold);
          return (
            <article key={stage.title} className={`rounded-2xl border p-4 ${state === "locked" ? "border-slate-800 bg-slate-950/20 opacity-65" : state === "active" ? "border-amber-400/40 bg-amber-400/10" : "border-emerald-400/30 bg-emerald-400/10"}`}>
              <Badge tone={stageTone[state]}>{state}</Badge>
              <h3 className="mt-3 text-sm font-semibold text-slate-100">{stage.title}</h3>
              <p className="mt-2 text-xs leading-5 text-slate-400">{stage.body}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
