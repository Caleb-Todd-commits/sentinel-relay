import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import type { AuditReportModel } from "@/lib/report";
import type { IncidentCase } from "@/lib/types";

export function ReportHero({ caseFile, model }: { caseFile: IncidentCase; model: AuditReportModel }) {
  return (
    <header className="relay-card relative overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-300/70 to-transparent" />
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <Badge tone="warning">{caseFile.id}</Badge>
            <Badge tone="accent">{caseFile.affectedSystem}</Badge>
            <Badge tone="success">Audit-ready report</Badge>
            <Badge>{model.generatedByName}</Badge>
          </div>
          <div>
            <p className="relay-label">Final Incident Report</p>
            <h1 className="mt-2 max-w-5xl text-3xl font-bold tracking-tight md:text-5xl">{model.report.title}</h1>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link href="/war-room" className="relay-button-secondary">Back to War Room</Link>
          <Link href="/demo" className="relay-button-primary">Restart Demo</Link>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[1.4fr_0.8fr]">
        <p className="text-base leading-7 text-slate-300">{model.report.executiveSummary}</p>
        <div className="rounded-2xl border border-slate-700/80 bg-slate-950/35 p-4">
          <p className="relay-label">Report posture</p>
          <dl className="mt-3 grid gap-3 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Generated</dt>
              <dd className="font-mono text-slate-300">{model.report.generatedAt}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Severity</dt>
              <dd className="font-semibold text-amber-200">{model.report.severity.toUpperCase()}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Decision gate</dt>
              <dd className="font-semibold text-emerald-200">Human approved containment</dd>
            </div>
          </dl>
        </div>
      </div>
    </header>
  );
}
