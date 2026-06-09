import type { WorkflowViewModel } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";

type WorkflowControlsProps = {
  workflow: WorkflowViewModel;
  onStart: () => void;
  onAdvance: () => void;
  onApprove: () => void;
  onReplay: () => void;
  onComplete: () => void;
};

const categoryTone: Record<WorkflowViewModel["currentStep"]["category"], "neutral" | "success" | "warning" | "danger" | "accent"> = {
  setup: "neutral",
  room: "accent",
  assignment: "accent",
  evidence: "warning",
  verification: "accent",
  challenge: "danger",
  approval: "warning",
  remediation: "success",
  report: "success",
};

export function WorkflowControls({ workflow, onStart, onAdvance, onApprove, onReplay, onComplete }: WorkflowControlsProps) {
  const primaryLabel = workflow.isAtStart ? "Start incident" : workflow.isAtApprovalGate ? "Approval required" : "Run next step";

  return (
    <section className="relay-card relay-control-card space-y-5" aria-labelledby="workflow-controls-heading">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-5xl">
          <div className="flex flex-wrap gap-2">
            <Badge tone="accent">{workflow.modeLabel}</Badge>
            <Badge tone={categoryTone[workflow.currentStep.category]}>{workflow.currentStep.category}</Badge>
            <Badge>{workflow.progressPercent}% complete</Badge>
            {workflow.isAtApprovalGate ? <Badge tone="warning">human decision required</Badge> : null}
          </div>
          <h2 id="workflow-controls-heading" className="mt-3 text-xl font-semibold tracking-tight">{workflow.currentStep.title}</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">{workflow.currentStep.description}</p>
        </div>
        <div className="rounded-2xl border border-slate-700 bg-slate-950/40 p-4 text-right">
          <p className="relay-label">Current step</p>
          <p className="mt-1 text-3xl font-bold">{workflow.stepIndex}<span className="text-base text-slate-500">/{workflow.totalSteps}</span></p>
        </div>
      </div>

      <div aria-label="Workflow progress" className="space-y-2">
        <div className="h-2 overflow-hidden rounded-full bg-slate-800">
          <div className="h-full rounded-full bg-gradient-to-r from-sky-300 via-violet-300 to-emerald-300 transition-all" style={{ width: `${workflow.progressPercent}%` }} />
        </div>
        <div className="grid grid-cols-11 gap-1">
          {Array.from({ length: workflow.totalSteps + 1 }).map((_, index) => (
            <span key={index} className={`h-1.5 rounded-full ${index <= workflow.stepIndex ? "bg-sky-300" : "bg-slate-800"}`} />
          ))}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {workflow.isAtStart ? (
          <button type="button" onClick={onStart} className="relay-button-primary">Start incident</button>
        ) : (
          <button type="button" onClick={onAdvance} disabled={!workflow.canAdvance} className="relay-button-primary disabled:cursor-not-allowed disabled:opacity-50">
            {primaryLabel}
          </button>
        )}

        {workflow.canApprove ? (
          <button type="button" onClick={onApprove} className="relay-button-primary border-emerald-400/40 bg-emerald-400/15 text-emerald-100 hover:bg-emerald-400/25">
            Approve containment
          </button>
        ) : null}

        <button type="button" onClick={onComplete} disabled={!workflow.canComplete} className="relay-button-secondary disabled:cursor-not-allowed disabled:opacity-50">Complete demo</button>
        <button type="button" onClick={onReplay} disabled={!workflow.canReplay} className="relay-button-secondary disabled:cursor-not-allowed disabled:opacity-50">Replay from start</button>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <div className="rounded-2xl border border-sky-400/20 bg-sky-400/5 p-4">
          <p className="relay-label text-sky-200">Judge callout</p>
          <p className="mt-2 text-sm leading-6 text-slate-300">{workflow.currentStep.judgeCallout}</p>
        </div>
        <div className="rounded-2xl border border-violet-400/20 bg-violet-400/5 p-4">
          <p className="relay-label text-violet-200">Band proof</p>
          <p className="mt-2 text-sm leading-6 text-slate-300">{workflow.currentStep.bandProof}</p>
        </div>
      </div>
    </section>
  );
}
