import { Badge } from "@/components/ui/Badge";
import type { ReportMetric } from "@/lib/report";

export function ReportMetricsGrid({ metrics }: { metrics: ReportMetric[] }) {
  return (
    <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3" aria-label="Report metrics">
      {metrics.map((metric) => (
        <article key={metric.label} className="relay-card-compact">
          <div className="flex items-center justify-between gap-3">
            <p className="relay-label">{metric.label}</p>
            <Badge tone={metric.tone}>{metric.tone}</Badge>
          </div>
          <p className="mt-3 text-2xl font-bold tracking-tight">{metric.value}</p>
          <p className="mt-2 text-sm leading-6 text-slate-400">{metric.detail}</p>
        </article>
      ))}
    </section>
  );
}
