import { Badge } from "@/components/ui/Badge";

export function ReportExportPanel({ checklist }: { checklist: string[] }) {
  return (
    <section className="relay-card" aria-labelledby="export-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="export-heading" className="font-semibold">Enterprise Export Checklist</h2>
          <p className="mt-1 text-sm leading-6 text-slate-400">Structured output requirements for a production-ready audit handoff.</p>
        </div>
        <Badge>scenario</Badge>
      </div>
      <ul className="mt-5 space-y-2 text-sm leading-6 text-slate-300">
        {checklist.map((item) => <li key={item} className="rounded-xl border border-slate-700/70 bg-slate-950/25 p-3">• {item}</li>)}
      </ul>
    </section>
  );
}
