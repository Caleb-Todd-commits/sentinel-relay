import { Badge } from "@/components/ui/Badge";

export function OpenQuestionsCard({ questions, limitations }: { questions: string[]; limitations: string[] }) {
  return (
    <section className="relay-card" aria-labelledby="open-questions-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="open-questions-heading" className="font-semibold">Open Questions and Limitations</h2>
          <p className="mt-1 text-sm leading-6 text-slate-400">The report should clearly state what is known, what is likely, and what still needs verification.</p>
        </div>
        <Badge tone="warning">requires follow-up</Badge>
      </div>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-amber-400/20 bg-amber-400/5 p-4">
          <p className="relay-label">Open questions</p>
          <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-300">
            {questions.map((item) => <li key={item}>• {item}</li>)}
          </ul>
        </div>
        <div className="rounded-2xl border border-slate-700/80 bg-slate-950/25 p-4">
          <p className="relay-label">Primary limitations</p>
          <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-300">
            {limitations.map((item) => <li key={item}>• {item}</li>)}
          </ul>
        </div>
      </div>
    </section>
  );
}
