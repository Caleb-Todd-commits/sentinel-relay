import type { AgentMessage } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { formatMessageType } from "@/lib/utils/format";

export function AuditReplayPanel({ messages, totalSteps }: { messages: AgentMessage[]; totalSteps: number }) {
  const lockedCount = Math.max(0, totalSteps - messages.length);

  return (
    <section className="relay-card" aria-labelledby="audit-replay-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="audit-replay-heading" className="font-semibold">Audit Replay Trail</h2>
          <p className="mt-1 text-sm text-slate-400">A compact trace of the coordination record that becomes the final report backbone.</p>
        </div>
        <div className="flex gap-2">
          <Badge tone="success">{messages.length} recorded</Badge>
          {lockedCount > 0 ? <Badge>{lockedCount} locked</Badge> : null}
        </div>
      </div>

      <div className="mt-5 space-y-3">
        {messages.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/20 p-4 text-sm leading-6 text-slate-400">
            Start the workflow to begin recording replayable agent decisions.
          </div>
        ) : (
          messages.map((message) => (
            <article key={message.id} className="relative rounded-2xl border border-slate-700/70 bg-slate-950/25 p-3 pl-11">
              <div className="absolute left-3 top-3 flex h-6 w-6 items-center justify-center rounded-full border border-slate-600 bg-slate-950 text-xs font-bold text-slate-300">
                {message.sequence}
              </div>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-semibold text-slate-100">{message.title}</p>
                <Badge>{formatMessageType(message.type)}</Badge>
              </div>
              <p className="mt-1 text-xs leading-5 text-slate-400">{message.agentName} · {message.createdAt}</p>
              {message.correlationId ? <p className="mt-2 font-mono text-[11px] text-slate-500">trace: {message.correlationId}</p> : null}
            </article>
          ))
        )}
      </div>
    </section>
  );
}
