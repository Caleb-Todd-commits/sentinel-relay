import Link from "next/link";
import type { FinalReport } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";

export function ReportPreview({ ready, report }: { ready: boolean; report: FinalReport }) {
  return (
    <section className="relay-card" aria-labelledby="report-preview-heading">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 id="report-preview-heading" className="font-semibold">Final Report</h2>
          <p className="mt-1 text-sm text-slate-400">Audit-ready output generated from structured collaboration records.</p>
        </div>
        <Badge tone={ready ? "success" : "neutral"}>{ready ? "ready" : "locked"}</Badge>
      </div>
      {ready ? (
        <div className="mt-4 space-y-4">
          <p className="text-sm leading-6 text-slate-300">{report.executiveSummary}</p>
          <div className="grid gap-2 text-xs text-slate-400">
            <div className="flex justify-between gap-3 rounded-xl border border-slate-700/70 bg-slate-950/30 p-3">
              <span>Audit events</span>
              <span className="font-semibold text-slate-200">{report.auditTrailMessageIds.length}</span>
            </div>
            <div className="flex justify-between gap-3 rounded-xl border border-slate-700/70 bg-slate-950/30 p-3">
              <span>Report sections</span>
              <span className="font-semibold text-slate-200">{report.sections.length}</span>
            </div>
          </div>
          <Link href="/report" className="relay-button-primary w-full">Open full audit report</Link>
        </div>
      ) : (
        <p className="mt-4 text-sm leading-6 text-slate-400">Report unlocks after the approval decision, remediation task generation, and report-section event appear in the collaboration stream.</p>
      )}
    </section>
  );
}
