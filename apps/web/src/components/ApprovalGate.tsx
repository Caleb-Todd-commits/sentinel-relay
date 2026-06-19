import type { ApprovalDecision, ApprovalRequest } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";

type ApprovalGateProps = {
  request: ApprovalRequest;
  decision?: ApprovalDecision;
  approved: boolean;
  onApprove?: () => void;
};

export function ApprovalGate({ request, decision, approved, onApprove }: ApprovalGateProps) {
  return (
    <section className="relay-card relay-approval-card" aria-labelledby="approval-gate-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Badge tone={approved ? "success" : "warning"}>Human approval gate</Badge>
          <h2 id="approval-gate-heading" className="mt-3 text-xl font-semibold">
            Containment approval required
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            The workflow intentionally pauses before high-impact production action.
          </p>
        </div>
        <Badge tone={approved ? "success" : "warning"}>{approved ? "approved" : "pending"}</Badge>
      </div>

      <p className="mt-4 rounded-2xl border border-slate-700/80 bg-slate-950/30 p-4 text-sm leading-6 text-slate-200">
        {request.action}
      </p>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div className="rounded-xl border border-slate-700 bg-slate-950/30 p-3">
          <p className="relay-label">Reason</p>
          <p className="mt-2 text-sm text-slate-300">{request.reason}</p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-950/30 p-3">
          <p className="relay-label">Required approver</p>
          <p className="mt-2 text-sm text-slate-300">{request.requiredApprover}</p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-950/30 p-3">
          <p className="relay-label">Risk if approved</p>
          <p className="mt-2 text-sm text-slate-300">{request.riskIfApproved}</p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-950/30 p-3">
          <p className="relay-label">Risk if rejected</p>
          <p className="mt-2 text-sm text-slate-300">{request.riskIfRejected}</p>
        </div>
      </div>

      {approved && decision ? (
        <div className="mt-4 rounded-2xl border border-emerald-400/30 bg-emerald-400/10 p-4 transition-all duration-500">
          <p className="text-sm font-semibold text-emerald-100">
            {decision.decidedBy}: approved with scoped limits
          </p>
          <p className="mt-1 text-sm leading-6 text-slate-300">{decision.rationale}</p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <div className="rounded-xl border border-emerald-400/20 bg-emerald-400/5 p-3">
              <p className="relay-label text-emerald-100">Approved scope</p>
              <ul className="mt-2 space-y-1 text-xs leading-5 text-slate-300">
                {decision.approvedActionScope.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl border border-red-400/20 bg-red-400/5 p-3">
              <p className="relay-label text-red-100">Not approved</p>
              <ul className="mt-2 space-y-1 text-xs leading-5 text-slate-300">
                {decision.explicitlyNotApproved.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-4 flex flex-wrap items-center gap-3 rounded-2xl border border-amber-400/30 bg-amber-400/10 p-4">
          <p className="flex-1 text-sm leading-6 text-slate-300">
            Remediation stays blocked until this decision is recorded. High-impact production actions require explicit human approval.
          </p>
          {onApprove ? (
            <button
              type="button"
              onClick={onApprove}
              className="relay-button-primary min-w-[160px] bg-emerald-400 text-slate-950 transition-all duration-300 hover:bg-emerald-300 hover:shadow-[0_0_20px_rgba(52,211,153,0.35)]"
            >
              Approve containment
            </button>
          ) : null}
        </div>
      )}
    </section>
  );
}
