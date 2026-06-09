import type { WorkflowViewModel } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";
import { formatStatus } from "@/lib/utils/format";

export function StateMachinePanel({ workflow }: { workflow: WorkflowViewModel }) {
  const decisionTone = workflow.state.decisionGate === "approved" ? "success" : workflow.state.decisionGate === "human_required" ? "warning" : "neutral";

  return (
    <section className="relay-card" aria-labelledby="state-machine-heading">
      <div className="flex items-center justify-between gap-3">
        <h2 id="state-machine-heading" className="font-semibold">Workflow State</h2>
        <Badge tone={decisionTone}>{workflow.state.decisionGate}</Badge>
      </div>

      <dl className="mt-4 grid gap-3 text-sm">
        <div className="rounded-xl border border-slate-700/80 bg-slate-950/25 p-3">
          <dt className="relay-label">Status</dt>
          <dd className="mt-1 font-semibold text-slate-100">{formatStatus(workflow.state.status)}</dd>
        </div>
        <div className="rounded-xl border border-slate-700/80 bg-slate-950/25 p-3">
          <dt className="relay-label">Phase</dt>
          <dd className="mt-1 font-semibold text-slate-100">{formatStatus(workflow.state.phase)}</dd>
        </div>
        <div className="rounded-xl border border-slate-700/80 bg-slate-950/25 p-3">
          <dt className="relay-label">Open approval requests</dt>
          <dd className="mt-1 font-semibold text-slate-100">{workflow.state.openApprovalRequestIds.length}</dd>
        </div>
        <div className="rounded-xl border border-slate-700/80 bg-slate-950/25 p-3">
          <dt className="relay-label">Unresolved challenges</dt>
          <dd className="mt-1 font-semibold text-slate-100">{workflow.state.unresolvedChallengeIds.length}</dd>
        </div>
      </dl>

      {workflow.nextStep ? (
        <div className="mt-4 rounded-xl border border-slate-700/80 bg-slate-950/25 p-3">
          <p className="relay-label">Next unlock</p>
          <p className="mt-1 text-sm font-semibold text-slate-100">{workflow.nextStep.shortLabel}</p>
          <p className="mt-1 text-xs leading-5 text-slate-400">{workflow.nextStep.description}</p>
        </div>
      ) : (
        <div className="mt-4 rounded-xl border border-emerald-400/30 bg-emerald-400/10 p-3">
          <p className="text-sm font-semibold text-emerald-100">Workflow complete</p>
          <p className="mt-1 text-xs leading-5 text-slate-300">The report is ready and the audit trail can be replayed from the Band-style message stream.</p>
        </div>
      )}
    </section>
  );
}
