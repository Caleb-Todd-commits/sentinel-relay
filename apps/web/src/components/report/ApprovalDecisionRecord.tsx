import { Badge } from "@/components/ui/Badge";
import type { ApprovalNarrative } from "@/lib/report";

export function ApprovalDecisionRecord({ approval }: { approval?: ApprovalNarrative }) {
  return (
    <section className="relay-card" aria-labelledby="approval-record-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="approval-record-heading" className="font-semibold">Human Approval Record</h2>
          <p className="mt-1 text-sm leading-6 text-slate-400">High-impact containment actions are separated from unapproved external notification decisions.</p>
        </div>
        <Badge tone={approval ? "success" : "danger"}>{approval ? "decision recorded" : "missing decision"}</Badge>
      </div>
      {approval ? (
        <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_0.9fr]">
          <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/5 p-4">
            <p className="relay-label">Decision</p>
            <h3 className="mt-2 text-xl font-semibold capitalize text-emerald-100">{approval.decision}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-300">{approval.rationale}</p>
            <p className="mt-3 text-xs text-slate-500">{approval.decidedBy} · {approval.decidedAt}</p>
          </div>
          <div className="grid gap-3">
            <div className="rounded-2xl border border-slate-700/80 bg-slate-950/25 p-4">
              <p className="relay-label">Approved scope</p>
              <ul className="mt-2 space-y-1 text-sm leading-6 text-slate-300">
                {approval.approvedScope.map((item) => <li key={item}>• {item}</li>)}
              </ul>
            </div>
            <div className="rounded-2xl border border-amber-400/20 bg-amber-400/5 p-4">
              <p className="relay-label">Explicitly not approved</p>
              <ul className="mt-2 space-y-1 text-sm leading-6 text-slate-300">
                {approval.notApproved.map((item) => <li key={item}>• {item}</li>)}
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <p className="mt-5 rounded-2xl border border-rose-400/20 bg-rose-400/5 p-4 text-sm leading-6 text-slate-300">No approval record was found. A production report should not be considered complete.</p>
      )}
    </section>
  );
}
