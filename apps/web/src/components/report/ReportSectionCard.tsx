import { Badge } from "@/components/ui/Badge";
import type { ReportSection } from "@/lib/types";

function label(value: string): string {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function ReportSectionCard({ section }: { section: ReportSection }) {
  return (
    <article className="rounded-2xl border border-slate-700/80 bg-slate-950/25 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Badge tone="accent">{label(section.type)}</Badge>
          <h3 className="mt-3 text-lg font-semibold tracking-tight">{section.title}</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge>{section.evidenceIds.length} evidence</Badge>
          <Badge>{section.sourceMessageIds.length} messages</Badge>
        </div>
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-300">{section.content}</p>
      <div className="mt-4 grid gap-3 text-xs text-slate-400 md:grid-cols-2">
        <div className="rounded-xl border border-slate-700/70 bg-slate-950/35 p-3">
          <p className="font-semibold text-slate-200">Evidence IDs</p>
          <p className="mt-2 font-mono leading-5">{section.evidenceIds.join(", ") || "none"}</p>
        </div>
        <div className="rounded-xl border border-slate-700/70 bg-slate-950/35 p-3">
          <p className="font-semibold text-slate-200">Source Messages</p>
          <p className="mt-2 font-mono leading-5">{section.sourceMessageIds.join(", ") || "none"}</p>
        </div>
      </div>
    </article>
  );
}
