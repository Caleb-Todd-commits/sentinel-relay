"use client";

import { AgentRoster } from "@/components/AgentRoster";
import { ApprovalGate } from "@/components/ApprovalGate";
import { EvidenceBoard } from "@/components/EvidenceBoard";
import { MessageStream } from "@/components/MessageStream";
import { ReportPreview } from "@/components/ReportPreview";
import { SiteHeader } from "@/components/SiteHeader";
import { TimelinePanel } from "@/components/TimelinePanel";
import { AuditReplayPanel } from "@/components/war-room/AuditReplayPanel";
import { CollaborationMap } from "@/components/war-room/CollaborationMap";
import { CriticalMomentCard } from "@/components/war-room/CriticalMomentCard";
import { DecisionPanel } from "@/components/war-room/DecisionPanel";
import { HandoffPanel } from "@/components/war-room/HandoffPanel";
import { IncidentHeader } from "@/components/war-room/IncidentHeader";
import { JudgeBriefingPanel } from "@/components/war-room/JudgeBriefingPanel";
import { RemediationList } from "@/components/war-room/RemediationList";
import { StateMachinePanel } from "@/components/war-room/StateMachinePanel";
import { WarRoomCommandBar } from "@/components/war-room/WarRoomCommandBar";
import { WarRoomSectionHeader } from "@/components/war-room/WarRoomSectionHeader";
import { WorkflowControls } from "@/components/war-room/WorkflowControls";
import { useIncidentCollaborationWorkflow } from "@/lib/workflow";

export default function WarRoomPage() {
  const workflow = useIncidentCollaborationWorkflow();

  return (
    <main className="relay-page">
      <SiteHeader />
      <section className="relay-shell space-y-6 py-5">
        <WarRoomCommandBar workflow={workflow} />

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_430px]">
          <IncidentHeader incident={workflow.case} visibleMessages={workflow.messages.length} totalMessages={workflow.totalSteps} />
          <JudgeBriefingPanel workflow={workflow} />
        </div>

        <WorkflowControls
          workflow={workflow}
          onStart={workflow.actions.start}
          onAdvance={workflow.actions.advance}
          onApprove={workflow.actions.approveContainment}
          onReplay={workflow.actions.replay}
          onComplete={workflow.actions.completeDemo}
        />

        <CriticalMomentCard workflow={workflow} />
        <CollaborationMap agents={workflow.agents} handoffs={workflow.handoffs} currentStep={workflow.currentStep} />

        <div className="grid gap-5 2xl:grid-cols-[320px_minmax(0,1fr)_420px]">
          <aside className="space-y-5">
            <WarRoomSectionHeader eyebrow="Control plane" title="State and agents" />
            <StateMachinePanel workflow={workflow} />
            <AgentRoster agents={workflow.agents} />
            <HandoffPanel handoffs={workflow.handoffs} agents={workflow.agents} />
          </aside>

          <section className="space-y-5">
            <WarRoomSectionHeader eyebrow="Band room" title="Structured collaboration stream" />
            <MessageStream messages={workflow.messages} evidence={workflow.evidence} agents={workflow.agents} />
            {workflow.approvalRequest ? (
              <ApprovalGate
                request={workflow.approvalRequest}
                decision={workflow.approvalDecision}
                approved={workflow.approvalState === "approved"}
                onApprove={workflow.canApprove ? workflow.actions.approveContainment : undefined}
              />
            ) : null}
            <AuditReplayPanel messages={workflow.messages} totalSteps={workflow.totalSteps} />
          </section>

          <aside className="space-y-5">
            <WarRoomSectionHeader eyebrow="Evidence and output" title="Decision artifacts" />
            <DecisionPanel decisions={workflow.decisions} />
            <EvidenceBoard evidence={workflow.evidence} lockedCount={workflow.lockedEvidenceCount} />
            <TimelinePanel events={workflow.timeline} />
            <RemediationList tasks={workflow.remediationTasks} agents={workflow.agents} lockedCount={workflow.lockedTaskCount} />
            <ReportPreview ready={workflow.reportReady} report={workflow.finalReport} />
          </aside>
        </div>
      </section>
    </main>
  );
}
