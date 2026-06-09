import type { WorkflowViewModel } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";

const briefingItems = [
  {
    title: "Band is central",
    body: "Every important step is modeled as shared room context: assignments, findings, challenges, approvals, and report generation.",
  },
  {
    title: "Agents have real roles",
    body: "Forensics, Threat Intel, Code Review, Risk, Remediation, and Human Approval each own different decisions.",
  },
  {
    title: "The system can disagree",
    body: "Risk & Compliance blocks overclaiming until evidence and approval are strong enough.",
  },
  {
    title: "The output is audit-ready",
    body: "Messages, evidence, decisions, and remediation tasks become a replayable incident record.",
  },
];

export function JudgeBriefingPanel({ workflow }: { workflow: WorkflowViewModel }) {
  return (
    <section className="relay-card relay-card-highlight" aria-labelledby="judge-briefing-heading">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Badge tone="warning">Judge lens</Badge>
          <h2 id="judge-briefing-heading" className="mt-3 text-lg font-semibold">Why this is not a normal chatbot demo</h2>
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
          <p className="relay-label text-sky-200">Current judge callout</p>
          <p className="mt-2 text-sm leading-6 text-slate-200">{workflow.currentStep.judgeCallout}</p>
        </div>
        <div className="rounded-2xl border border-violet-400/25 bg-violet-400/10 p-4">
          <p className="relay-label text-violet-200">Current Band proof</p>
          <p className="mt-2 text-sm leading-6 text-slate-200">{workflow.currentStep.bandProof}</p>
        </div>
      </div>
    </section>
  );
}
