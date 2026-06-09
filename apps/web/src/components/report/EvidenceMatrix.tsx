import { Badge } from "@/components/ui/Badge";
import type { EvidenceMatrixRow } from "@/lib/report";

export function EvidenceMatrix({ rows }: { rows: EvidenceMatrixRow[] }) {
  return (
    <section className="relay-card" aria-labelledby="evidence-matrix-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="evidence-matrix-heading" className="font-semibold">Evidence Matrix</h2>
          <p className="mt-1 text-sm leading-6 text-slate-400">Every report claim needs traceable evidence, source location, and known limitations.</p>
        </div>
        <Badge tone="success">{rows.length} linked items</Badge>
      </div>
      <div className="mt-5 grid gap-3">
        {rows.map((row) => (
          <article key={row.id} className="rounded-2xl border border-slate-700/80 bg-slate-950/25 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-slate-100">{row.title}</p>
                <p className="mt-1 text-xs text-slate-500">{row.source} · {row.id}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge>{row.kind}</Badge>
                <Badge>{row.confidenceLabel}</Badge>
                <Badge>{row.sensitivity}</Badge>
              </div>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-3">
              <div className="rounded-xl border border-slate-700/70 bg-slate-950/35 p-3">
                <p className="relay-label">Used by sections</p>
                <ul className="mt-2 space-y-1 text-xs leading-5 text-slate-300">
                  {(row.usedBySections.length ? row.usedBySections : ["Not cited by final sections"]).map((item) => <li key={item}>• {item}</li>)}
                </ul>
              </div>
              <div className="rounded-xl border border-slate-700/70 bg-slate-950/35 p-3">
                <p className="relay-label">Cited by messages</p>
                <ul className="mt-2 space-y-1 text-xs leading-5 text-slate-300">
                  {(row.citedByMessages.length ? row.citedByMessages : ["No message citation found"]).slice(0, 4).map((item) => <li key={item}>• {item}</li>)}
                </ul>
              </div>
              <div className="rounded-xl border border-slate-700/70 bg-slate-950/35 p-3">
                <p className="relay-label">Limitations</p>
                <ul className="mt-2 space-y-1 text-xs leading-5 text-slate-300">
                  {(row.limitations.length ? row.limitations : ["No limitation recorded"]).map((item) => <li key={item}>• {item}</li>)}
                </ul>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
