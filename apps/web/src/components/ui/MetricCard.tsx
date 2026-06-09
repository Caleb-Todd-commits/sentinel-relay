import { Badge } from "./Badge";

type MetricCardProps = {
  label: string;
  value: string;
  detail?: string;
  tone?: "neutral" | "success" | "warning" | "danger" | "accent";
};

export function MetricCard({ label, value, detail, tone = "neutral" }: MetricCardProps) {
  return (
    <div className="relay-card-compact space-y-2">
      <div className="flex items-center justify-between gap-3">
        <p className="relay-label">{label}</p>
        <Badge tone={tone}>{tone}</Badge>
      </div>
      <p className="text-2xl font-bold tracking-tight">{value}</p>
      {detail ? <p className="relay-muted">{detail}</p> : null}
    </div>
  );
}
