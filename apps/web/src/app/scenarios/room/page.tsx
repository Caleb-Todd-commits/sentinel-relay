"use client";

import Link from "next/link";
import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { SiteHeader } from "@/components/SiteHeader";
import { Badge } from "@/components/ui/Badge";
import { AgentRoster } from "@/components/AgentRoster";
import { EvidenceBoard } from "@/components/EvidenceBoard";
import { MessageStream } from "@/components/MessageStream";
import { ApprovalGate } from "@/components/ApprovalGate";
import { AuditReplayPanel } from "@/components/war-room/AuditReplayPanel";
import type { CollaborationRoomSnapshot } from "@/lib/collaboration/types";
import type { AgentProfile, AgentMessage, EvidenceReference, ApprovalRequest, ApprovalDecision } from "@/lib/types";
import { SCENARIOS } from "@/lib/scenarios";

function useRoomSnapshot(roomId: string | null): CollaborationRoomSnapshot | null {
  const [snapshot, setSnapshot] = useState<CollaborationRoomSnapshot | null>(null);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!roomId) return;

    // First fetch the snapshot immediately
    fetch(`/api/collaboration/rooms?roomId=${encodeURIComponent(roomId)}`)
      .then((r) => r.json())
      .then((body) => {
        if (body.snapshot) setSnapshot(body.snapshot);
      })
      .catch(() => {});

    // Then subscribe to SSE for live updates
    const es = new EventSource(`/api/collaboration/stream?roomId=${encodeURIComponent(roomId)}`);
    esRef.current = es;
    es.addEventListener("snapshot", (event) => {
      try {
        const parsed = JSON.parse((event as MessageEvent<string>).data);
        if (parsed.snapshot) setSnapshot(parsed.snapshot);
      } catch {}
    });
    return () => {
      es.close();
      esRef.current = null;
    };
  }, [roomId]);

  return snapshot;
}

// Minimal agent profiles for display — derived from scenario data
const AGENT_PROFILES: AgentProfile[] = [
  { id: "agent-commander", name: "Band Leader", shortName: "Band Leader", kind: "ai_agent", role: "Case coordination", responsibility: "Coordinates the incident room", capability: "case_command", status: "complete", allowedDecisions: [], requiresHumanApprovalFor: [], createdAt: "" },
  { id: "agent-forensics", name: "Forensics Agent", shortName: "Forensics", kind: "ai_agent", role: "Log analysis", responsibility: "Evidence timeline", capability: "log_forensics", status: "complete", allowedDecisions: [], requiresHumanApprovalFor: [], createdAt: "" },
  { id: "agent-threat-intel", name: "Threat Intel Agent", shortName: "Threat Intel", kind: "ai_agent", role: "Indicator assessment", responsibility: "Confidence assessment", capability: "threat_assessment", status: "complete", allowedDecisions: [], requiresHumanApprovalFor: [], createdAt: "" },
  { id: "agent-code-review", name: "Code Review Agent", shortName: "Code Review", kind: "ai_agent", role: "Deployment review", responsibility: "Code and config review", capability: "code_review", status: "complete", allowedDecisions: [], requiresHumanApprovalFor: [], createdAt: "" },
  { id: "agent-risk-compliance", name: "Risk & Compliance Agent", shortName: "Risk", kind: "ai_agent", role: "Policy and challenge", responsibility: "Challenge and escalation", capability: "risk_compliance", status: "complete", allowedDecisions: [], requiresHumanApprovalFor: [], createdAt: "" },
  { id: "agent-remediation", name: "Remediation Agent", shortName: "Remediation", kind: "ai_agent", role: "Containment planning", responsibility: "Fix planning", capability: "remediation", status: "complete", allowedDecisions: [], requiresHumanApprovalFor: [], createdAt: "" },
  { id: "agent-human-approver", name: "Human Security Lead", shortName: "Security Lead", kind: "human_actor", role: "Approval authority", responsibility: "High-impact approval decisions", capability: "human_approval", status: "complete", allowedDecisions: [], requiresHumanApprovalFor: [], createdAt: "" },
];

function ScenarioRoomContent() {
  const params = useSearchParams();
  const roomId = params.get("room");
  const incidentId = params.get("incident") ?? "INC-1042";
  const snapshot = useRoomSnapshot(roomId);
  const scenario = SCENARIOS[incidentId as keyof typeof SCENARIOS];

  const messages: AgentMessage[] = snapshot?.messages ?? [];
  const approvalRequest: ApprovalRequest | undefined = snapshot?.approvalRequests?.[0];
  const approvalDecision: ApprovalDecision | undefined = snapshot?.approvalDecisions?.[0];
  const approved = Boolean(approvalDecision);
  const evidence: EvidenceReference[] = [];

  if (!roomId || !scenario) {
    return (
      <main className="relay-page">
        <SiteHeader />
        <section className="relay-shell py-10">
          <div className="relay-card space-y-4">
            <p className="text-slate-400">No scenario room specified.</p>
            <Link href="/scenarios" className="relay-button-primary inline-flex">Back to scenarios</Link>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="relay-page">
      <SiteHeader />
      <section className="relay-shell space-y-6 py-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link href="/scenarios" className="text-sm text-slate-400 transition hover:text-white">← Scenarios</Link>
          <Link href="/war-room" className="relay-button-secondary text-sm">Step-through War Room</Link>
        </div>

        <div className="relay-card space-y-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="flex flex-wrap gap-2">
                <Badge tone="warning">{scenario.id}</Badge>
                <Badge tone="accent">Live run</Badge>
                <Badge>{messages.length} messages</Badge>
              </div>
              <h1 className="mt-3 text-2xl font-bold tracking-tight">{scenario.title}</h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">{scenario.summary}</p>
            </div>
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <dt className="relay-label">Records affected</dt>
                <dd className="mt-1 font-semibold text-slate-100">{scenario.recordsAffected}</dd>
              </div>
              <div>
                <dt className="relay-label">Root cause</dt>
                <dd className="mt-1 font-semibold text-slate-100">{scenario.rootCause}</dd>
              </div>
            </dl>
          </div>
        </div>

        <div className="grid gap-5 xl:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="space-y-5">
            <AgentRoster agents={AGENT_PROFILES} />
          </aside>
          <section className="space-y-5">
            <MessageStream messages={messages} evidence={evidence} agents={AGENT_PROFILES} />
            {approvalRequest ? (
              <ApprovalGate
                request={approvalRequest}
                decision={approvalDecision}
                approved={approved}
              />
            ) : null}
            <AuditReplayPanel messages={messages} totalSteps={18} />
          </section>
        </div>
      </section>
    </main>
  );
}

function ScenarioRoomFallback() {
  return (
    <main className="relay-page">
      <SiteHeader />
      <section className="relay-shell py-10">
        <div className="relay-card">
          <p className="text-sm text-slate-400">Loading incident room…</p>
        </div>
      </section>
    </main>
  );
}

export default function ScenarioRoomPage() {
  return (
    <Suspense fallback={<ScenarioRoomFallback />}>
      <ScenarioRoomContent />
    </Suspense>
  );
}
