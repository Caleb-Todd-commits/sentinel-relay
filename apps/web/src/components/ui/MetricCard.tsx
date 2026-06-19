type MetricCardProps = {
  label: string;
  value: string;
  detail?: string;
  tone?: "neutral" | "success" | "warning" | "danger" | "accent";
};

const toneBorder: Record<NonNullable<MetricCardProps["tone"]>, string> = {
  neutral: "border-slate-700/80",
  success: "border-emerald-400/30",
  warning: "border-amber-400/30",
  danger: "border-red-400/30",
  accent: "border-sky-400/30",
};

export function MetricCard({ label, value, detail, tone = "neutral" }: MetricCardProps) {
  return (
    <div className={`relay-card-compact space-y-2 ${toneBorder[tone]}`}>
      <p className="relay-label">{label}</p>
      <p className="text-2xl font-bold tracking-tight">{value}</p>
      {detail ? <p className="relay-muted">{detail}</p> : null}
    </div>
  );
}
