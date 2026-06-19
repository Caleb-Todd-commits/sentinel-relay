import type { IncidentCase } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { MetricCard } from "@/components/ui/MetricCard";
import { formatSeverity, formatStatus } from "@/lib/utils/format";

export function IncidentHeader({ incident, visibleMessages, totalMessages }: { incident: IncidentCase; visibleMessages: number; totalMessages: number }) {
  return (
    <section className="relay-card space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-3xl">
          <div className="flex flex-wrap gap-2">
            <Badge tone="accent">{incident.id}</Badge>
            <Badge>Room: {incident.roomId}</Badge>
          </div>
          <h1 className="mt-4 text-3xl font-bold tracking-tight md:text-4xl">{incident.title}</h1>
          <p className="mt-3 text-sm leading-6 text-slate-300 md:text-base">{incident.summary}</p>
        </div>
        <div className="rounded-2xl border border-sky-400/30 bg-sky-400/10 p-4 text-right">
          <p className="relay-label">Workflow progress</p>
          <p className="mt-2 text-2xl font-bold">{visibleMessages}/{totalMessages}</p>
          <p className="mt-1 text-xs text-slate-400">coordination events</p>
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-4">
        <MetricCard label="Severity" value={formatSeverity(incident.severity)} detail="Escalated by evidence strength" tone="warning" />
        <MetricCard label="Status" value={formatStatus(incident.status)} detail={incident.currentPhase} tone="accent" />
        <MetricCard label="System" value={incident.affectedSystem} detail={incident.businessUnit} tone="neutral" />
        <MetricCard label="Decision gate" value={formatStatus(incident.decisionGate)} detail="High-impact actions need approval" tone={incident.decisionGate === "approved" ? "success" : incident.decisionGate === "human_required" ? "warning" : "neutral"} />
      </div>
    </section>
  );
}
