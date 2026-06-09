import { Badge } from "@/components/ui/Badge";
import type { RemediationReportRow } from "@/lib/report";
import { readableStatus } from "@/lib/report";

const statusTone: Record<RemediationReportRow["status"], "neutral" | "success" | "warning" | "danger" | "accent"> = {
  blocked: "danger",
  todo: "neutral",
  in_progress: "warning",
  review: "accent",
  done: "success",
  deferred: "warning",
};

export function RemediationReportCard({ rows }: { rows: RemediationReportRow[] }) {
  return (
    <section className="relay-card" aria-labelledby="remediation-report-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="remediation-report-heading" className="font-semibold">Remediation Control Plan</h2>
          <p className="mt-1 text-sm leading-6 text-slate-400">Every fix item links back to evidence, acceptance criteria, test plan, and rollback plan.</p>
        </div>
        <Badge tone="warning">{rows.length} tasks</Badge>
      </div>
      <div className="mt-5 grid gap-4">
        {rows.map((row) => (
          <article key={row.id} className="rounded-2xl border border-slate-700/80 bg-slate-950/25 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-slate-100">{row.title}</p>
                <p className="mt-1 text-xs text-slate-500">{row.id} · owner: {row.owner}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge tone={statusTone[row.status]}>{readableStatus[row.status]}</Badge>
                <Badge>{row.severity}</Badge>
              </div>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-3">
              <div className="rounded-xl border border-slate-700/70 bg-slate-950/35 p-3">
                <p className="relay-label">Acceptance criteria</p>
                <ul className="mt-2 space-y-1 text-xs leading-5 text-slate-300">
                  {row.acceptanceCriteria.map((item) => <li key={item}>• {item}</li>)}
                </ul>
              </div>
              <div className="rounded-xl border border-slate-700/70 bg-slate-950/35 p-3">
                <p className="relay-label">Test plan</p>
                <ul className="mt-2 space-y-1 text-xs leading-5 text-slate-300">
                  {row.testPlan.map((item) => <li key={item}>• {item}</li>)}
                </ul>
              </div>
              <div className="rounded-xl border border-slate-700/70 bg-slate-950/35 p-3">
                <p className="relay-label">Evidence and rollback</p>
                <p className="mt-2 text-xs leading-5 text-slate-300">{row.evidenceTitles.join("; ")}</p>
                <p className="mt-2 text-xs leading-5 text-slate-500">Rollback: {row.rollbackPlan}</p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
