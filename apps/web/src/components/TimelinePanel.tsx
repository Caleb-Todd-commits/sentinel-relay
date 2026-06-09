import type { TimelineEvent } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";

export function TimelinePanel({ events }: { events: TimelineEvent[] }) {
  return (
    <section className="relay-card" aria-labelledby="timeline-heading">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 id="timeline-heading" className="font-semibold">Incident Timeline</h2>
          <p className="mt-1 text-xs text-slate-500">Chronology derived from visible evidence and agent decisions.</p>
        </div>
        <Badge>{events.length} events</Badge>
      </div>
      <div className="mt-4 space-y-4">
        {events.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-700 bg-slate-950/20 p-4 text-sm leading-6 text-slate-400">
            Timeline events appear after the first evidence-backed finding is submitted.
          </div>
        ) : events.map((event, index) => (
          <article key={event.id} className="relative border-l border-slate-700 pl-5">
            <div className="absolute -left-[11px] top-0 flex h-5 w-5 items-center justify-center rounded-full border border-sky-300/60 bg-slate-950 text-[10px] font-bold text-sky-100">{index + 1}</div>
            <p className="text-xs font-semibold text-sky-200">{event.timestamp}</p>
            <h3 className="mt-1 text-sm font-semibold">{event.title}</h3>
            <p className="mt-1 text-xs leading-5 text-slate-400">{event.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
