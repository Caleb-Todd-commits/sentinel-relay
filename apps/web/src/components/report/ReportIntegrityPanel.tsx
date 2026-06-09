import { Badge } from "@/components/ui/Badge";
import type { ReportIntegrityCheck } from "@/lib/report";

const toneByStatus: Record<ReportIntegrityCheck["status"], "success" | "warning" | "danger"> = {
  ready: "success",
  needs_review: "warning",
  blocked: "danger",
};

export function ReportIntegrityPanel({ checks }: { checks: ReportIntegrityCheck[] }) {
  return (
    <section className="relay-card" aria-labelledby="integrity-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="integrity-heading" className="font-semibold">Report Integrity Checks</h2>
          <p className="mt-1 text-sm leading-6 text-slate-400">These checks keep the final report tied to actual collaboration records instead of becoming freeform narrative.</p>
        </div>
        <Badge tone="accent">traceability</Badge>
      </div>
      <div className="mt-5 grid gap-3">
        {checks.map((check) => (
          <article key={check.label} className="rounded-2xl border border-slate-700/80 bg-slate-950/25 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h3 className="text-sm font-semibold text-slate-100">{check.label}</h3>
              <Badge tone={toneByStatus[check.status]}>{check.status.replace("_", " ")}</Badge>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-400">{check.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
