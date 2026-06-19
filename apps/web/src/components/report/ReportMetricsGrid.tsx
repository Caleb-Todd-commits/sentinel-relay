import type { ReportMetric } from "@/lib/report";

const toneBorder: Record<ReportMetric["tone"], string> = {
  neutral: "border-slate-700/80",
  success: "border-emerald-400/30",
  warning: "border-amber-400/30",
  danger: "border-red-400/30",
  accent: "border-sky-400/30",
};

export function ReportMetricsGrid({ metrics }: { metrics: ReportMetric[] }) {
  return (
    <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3" aria-label="Report metrics">
      {metrics.map((metric) => (
        <article key={metric.label} className={`relay-card-compact space-y-2 ${toneBorder[metric.tone]}`}>
          <p className="relay-label">{metric.label}</p>
          <p className="mt-1 text-2xl font-bold tracking-tight">{metric.value}</p>
          <p className="mt-2 text-sm leading-6 text-slate-400">{metric.detail}</p>
        </article>
      ))}
    </section>
  );
}
