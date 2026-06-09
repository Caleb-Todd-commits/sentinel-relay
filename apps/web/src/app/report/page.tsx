import { SiteHeader } from "@/components/SiteHeader";
import { ApprovalDecisionRecord } from "@/components/report/ApprovalDecisionRecord";
import { AuditTrailTable } from "@/components/report/AuditTrailTable";
import { EvidenceMatrix } from "@/components/report/EvidenceMatrix";
import { OpenQuestionsCard } from "@/components/report/OpenQuestionsCard";
import { RemediationReportCard } from "@/components/report/RemediationReportCard";
import { ReportExportPanel } from "@/components/report/ReportExportPanel";
import { ReportHero } from "@/components/report/ReportHero";
import { ReportIntegrityPanel } from "@/components/report/ReportIntegrityPanel";
import { ReportMetricsGrid } from "@/components/report/ReportMetricsGrid";
import { ReportSectionCard } from "@/components/report/ReportSectionCard";
import { sentinelRelayDemo } from "@/lib/demo/sentinelRelayDemo";
import { buildAuditReportModel } from "@/lib/report";

export default function ReportPage() {
  const model = buildAuditReportModel(sentinelRelayDemo);

  return (
    <main className="relay-page">
      <SiteHeader />
      <section className="relay-shell space-y-5 py-8">
        <ReportHero caseFile={sentinelRelayDemo.case} model={model} />
        <ReportMetricsGrid metrics={model.metrics} />

        <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
          <section className="relay-card" aria-labelledby="report-sections-heading">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 id="report-sections-heading" className="font-semibold">Report Sections</h2>
                <p className="mt-1 text-sm leading-6 text-slate-400">Each section carries the evidence IDs and source messages required for audit review.</p>
              </div>
            </div>
            <div className="mt-5 grid gap-4">
              {model.report.sections.map((section) => <ReportSectionCard key={section.id} section={section} />)}
            </div>
          </section>

          <div className="space-y-5">
            <ReportIntegrityPanel checks={model.integrityChecks} />
            <ApprovalDecisionRecord approval={model.approval} />
          </div>
        </div>

        <AuditTrailTable records={model.auditTrail} />
        <EvidenceMatrix rows={model.evidenceMatrix} />
        <RemediationReportCard rows={model.remediationRows} />

        <div className="grid gap-5 lg:grid-cols-2">
          <OpenQuestionsCard questions={model.report.openQuestions} limitations={model.primaryLimitations} />
          <ReportExportPanel checklist={model.exportChecklist} />
        </div>
      </section>
    </main>
  );
}
