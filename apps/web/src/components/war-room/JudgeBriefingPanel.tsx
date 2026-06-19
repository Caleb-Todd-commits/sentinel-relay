import type { WorkflowViewModel } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";

const briefingItems = [
  {
    title: "Shared room, not a pipeline",
    body: "Every step posts into a shared incident room — assignments, findings, challenges, approvals, and report generation are all visible in one place.",
  },
  {
    title: "Role-separated agents",
    body: "Forensics, Threat Intel, Code Review, Risk & Compliance, and Remediation each own separate decisions.",
  },
  {
    title: "Agents can disagree",
    body: "Risk & Compliance blocks an overclaimed conclusion until the evidence and approval are strong enough to proceed.",
  },
  {
    title: "Audit-ready output",
    body: "Every message, evidence reference, decision, and remediation task becomes a replayable incident record.",
  },
];

export function JudgeBriefingPanel({ workflow }: { workflow: WorkflowViewModel }) {
  return (
    <section className="relay-card relay-card-highlight" aria-labelledby="judge-briefing-heading">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Badge tone="accent">How it works</Badge>
          <h2 id="judge-briefing-heading" className="mt-3 text-lg font-semibold">Structured coordination, not a chatbot</h2>
        </div>
        <Badge>{workflow.currentStep.shortLabel}</Badge>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {briefingItems.map((item) => (
          <article key={item.title} className="rounded-2xl border border-slate-700/70 bg-slate-950/30 p-4">
            <h3 className="text-sm font-semibold text-slate-100">{item.title}</h3>
            <p className="mt-2 text-xs leading-5 text-slate-400">{item.body}</p>
          </article>
        ))}
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-2">
        <div className="rounded-2xl border border-sky-400/25 bg-sky-400/10 p-4">
          <p className="relay-label text-sky-200">What's happening now</p>
          <p className="mt-2 text-sm leading-6 text-slate-200">{workflow.currentStep.judgeCallout}</p>
        </div>
        <div className="rounded-2xl border border-violet-400/25 bg-violet-400/10 p-4">
          <p className="relay-label text-violet-200">Band coordination proof</p>
          <p className="mt-2 text-sm leading-6 text-slate-200">{workflow.currentStep.bandProof}</p>
        </div>
      </div>
    </section>
  );
}
