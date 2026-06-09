import type { WorkflowCollaborationState } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";

const statusTone: Record<WorkflowCollaborationState["syncStatus"], "neutral" | "success" | "warning" | "danger"> = {
  initializing: "neutral",
  syncing: "warning",
  ready: "success",
  error: "danger",
};

export function ProviderStatusPanel({ collaboration }: { collaboration?: WorkflowCollaborationState }) {
  if (!collaboration) {
    return null;
  }

  const health = collaboration.providerHealth;
  const syncTone = statusTone[collaboration.syncStatus];

  return (
    <section className="relay-card space-y-4 border-cyan-400/20 bg-cyan-400/[0.03]">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="relay-eyebrow">Collaboration provider</p>
          <h2 className="mt-2 text-lg font-semibold text-white">{health.label}</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">{health.summary}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge tone={collaboration.providerMode === "band" ? "warning" : "success"}>{collaboration.providerMode.toUpperCase()}</Badge>
          <Badge tone={syncTone}>{collaboration.syncStatus}</Badge>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Room</p>
          <p className="mt-1 truncate font-mono text-xs text-slate-200">{collaboration.roomId ?? "initializing"}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Registered agents</p>
          <p className="mt-1 text-lg font-semibold text-white">{collaboration.registeredAgentCount}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Provider audit events</p>
          <p className="mt-1 text-lg font-semibold text-white">{collaboration.auditEventCount}</p>
        </div>
      </div>

      {collaboration.error ? (
        <div className="rounded-2xl border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">
          {collaboration.error}
        </div>
      ) : null}

      <div className="grid gap-3 lg:grid-cols-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Warnings</p>
          <ul className="mt-2 space-y-1 text-sm text-slate-300">
            {health.warnings.map((warning) => (
              <li key={warning}>• {warning}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Next adapter steps</p>
          <ul className="mt-2 space-y-1 text-sm text-slate-300">
            {health.nextSteps.map((step) => (
              <li key={step}>• {step}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
