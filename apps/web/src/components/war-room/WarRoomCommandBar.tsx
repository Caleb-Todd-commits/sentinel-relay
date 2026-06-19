import type { WorkflowViewModel } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";
import { formatSeverity, formatStatus } from "@/lib/utils/format";

export function WarRoomCommandBar({ workflow }: { workflow: WorkflowViewModel }) {
  const activeAgents = workflow.agents.filter((agent) => ["working", "challenging", "waiting", "blocked"].includes(agent.status)).length;
  const approvalVisible = workflow.approvalState !== "hidden";
  const decisionTone = workflow.approvalState === "approved" ? "success" : "warning";

  return (
    <section className="relay-command-bar" aria-label="War room command summary">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="accent">Incident command</Badge>
          <Badge>{workflow.case.id}</Badge>
          {approvalVisible && (
            <Badge tone={decisionTone}>
              {workflow.approvalState === "approved" ? "Containment approved" : "Approval pending"}
            </Badge>
          )}
        </div>
        <h1 className="mt-3 truncate text-xl font-bold tracking-tight md:text-2xl">Sentinel Relay War Room</h1>
        <p className="mt-1 max-w-4xl text-sm leading-6 text-slate-400">
          Agents coordinate through a shared Band-style incident room — findings, challenges, approvals, and remediation in one stream.
        </p>
      </div>

      <dl className="grid min-w-full grid-cols-2 gap-2 sm:min-w-[460px] sm:grid-cols-4">
        <div className="relay-mini-stat">
          <dt>Severity</dt>
          <dd>{formatSeverity(workflow.case.severity)}</dd>
        </div>
        <div className="relay-mini-stat">
          <dt>Status</dt>
          <dd>{formatStatus(workflow.case.status)}</dd>
        </div>
        <div className="relay-mini-stat">
          <dt>Active agents</dt>
          <dd>{workflow.stepIndex === 0 ? "—" : `${activeAgents}/${workflow.agents.length}`}</dd>
        </div>
        <div className="relay-mini-stat">
          <dt>Messages</dt>
          <dd>{workflow.stepIndex === 0 ? "—" : `${workflow.messages.length}/${workflow.totalSteps}`}</dd>
        </div>
      </dl>
    </section>
  );
}
