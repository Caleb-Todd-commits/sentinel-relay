import type { EvidenceReference } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { asPercent } from "@/lib/utils/format";

const sensitivityTone: Record<EvidenceReference["sensitivity"], "neutral" | "success" | "warning" | "danger" | "accent"> = {
  public_demo: "success",
  internal: "accent",
  confidential: "warning",
  restricted: "danger",
};

export function EvidenceBoard({ evidence, lockedCount = 0 }: { evidence: EvidenceReference[]; lockedCount?: number }) {
  return (
    <section className="relay-card" aria-labelledby="evidence-board-heading">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 id="evidence-board-heading" className="font-semibold">Evidence Board</h2>
          <p className="mt-1 text-xs text-slate-500">Evidence unlocks only when cited by structured agent messages.</p>
        </div>
        <div className="flex gap-2">
          <Badge>{evidence.length} visible</Badge>
          {lockedCount > 0 ? <Badge tone="neutral">{lockedCount} locked</Badge> : null}
        </div>
      </div>
      <div className="mt-4 space-y-3">
        {evidence.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-700 bg-slate-950/20 p-4 text-sm leading-6 text-slate-400">
            Evidence unlocks as agents submit structured findings into the collaboration stream.
          </div>
        ) : evidence.map((item) => (
          <article key={item.id} className="rounded-2xl border border-slate-700/80 bg-slate-950/25 p-3">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="text-sm font-semibold leading-5">{item.title}</p>
                <p className="mt-1 text-xs text-slate-500">{item.source}{item.location ? ` · ${item.location}` : ""}</p>
              </div>
              <div className="flex flex-wrap gap-1.5">
                <Badge>{asPercent(item.confidence)}</Badge>
                <Badge tone={sensitivityTone[item.sensitivity]}>{item.sensitivity}</Badge>
              </div>
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-300">{item.summary}</p>
            {item.excerpt ? <p className="mt-3 overflow-x-auto rounded-lg bg-slate-950/70 p-2 font-mono text-[11px] leading-5 text-slate-400">{item.excerpt}</p> : null}
            {item.limitations?.length ? (
              <div className="mt-3 rounded-xl border border-amber-400/20 bg-amber-400/5 p-2">
                <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-amber-100">Limitations</p>
                <ul className="mt-1 space-y-1 text-[11px] leading-4 text-slate-400">
                  {item.limitations.map((limitation) => <li key={limitation}>• {limitation}</li>)}
                </ul>
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
