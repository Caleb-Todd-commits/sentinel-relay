import { Badge } from "@/components/ui/Badge";
import type { AuditTrailRecord } from "@/lib/report";

export function AuditTrailTable({ records }: { records: AuditTrailRecord[] }) {
  return (
    <section className="relay-card" aria-labelledby="audit-trail-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="audit-trail-heading" className="font-semibold">Audit Replay Record</h2>
          <p className="mt-1 text-sm leading-6 text-slate-400">The report is backed by the same ordered collaboration events shown in the War Room replay.</p>
        </div>
        <Badge tone="accent">{records.length} ordered events</Badge>
      </div>
      <div className="mt-5 overflow-hidden rounded-2xl border border-slate-700/80">
        <div className="hidden grid-cols-[72px_1fr_160px_1fr] gap-3 border-b border-slate-700 bg-slate-950/55 px-4 py-3 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500 lg:grid">
          <span>Seq</span>
          <span>Event</span>
          <span>Actor</span>
          <span>Decision impact</span>
        </div>
        <div className="divide-y divide-slate-800">
          {records.map((record) => (
            <article key={record.messageId} className="grid gap-3 bg-slate-950/25 px-4 py-4 lg:grid-cols-[72px_1fr_160px_1fr]">
              <div>
                <span className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-slate-600 bg-slate-950 text-xs font-bold text-slate-200">{record.sequence}</span>
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-semibold text-slate-100">{record.title}</p>
                  <Badge>{record.actionType}</Badge>
                </div>
                <p className="mt-1 font-mono text-[11px] text-slate-500">{record.timestamp} · {record.traceId}</p>
                {record.evidenceTitles.length ? (
                  <p className="mt-2 text-xs leading-5 text-slate-400">Evidence: {record.evidenceTitles.join("; ")}</p>
                ) : null}
                {record.targetAgents.length ? (
                  <p className="mt-1 text-xs leading-5 text-slate-500">Targets: {record.targetAgents.join(", ")}</p>
                ) : null}
              </div>
              <p className="text-sm text-slate-300">{record.actor}</p>
              <p className="text-sm leading-6 text-slate-400">{record.decisionImpact}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
