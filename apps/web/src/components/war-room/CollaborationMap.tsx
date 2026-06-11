"use client";

import type { AgentProfile } from "@/lib/types";
import type { WorkflowHandoff, WorkflowStepDefinition } from "@/lib/workflow";
import { Badge } from "@/components/ui/Badge";

const statusTone: Record<WorkflowHandoff["status"], "neutral" | "success" | "warning" | "danger" | "accent"> = {
  locked: "neutral",
  visible: "accent",
  complete: "success",
};

const AGENT_POSITIONS: Record<string, { x: number; y: number }> = {
  commander: { x: 50, y: 12 },
  forensics: { x: 18, y: 42 },
  threat_intel: { x: 82, y: 42 },
  code_review: { x: 18, y: 72 },
  risk_compliance: { x: 82, y: 72 },
  remediation: { x: 50, y: 90 },
};

function getAgentPos(agentId: string, index: number, total: number) {
  if (AGENT_POSITIONS[agentId]) return AGENT_POSITIONS[agentId];
  const angle = (index / total) * 2 * Math.PI - Math.PI / 2;
  return {
    x: 50 + 38 * Math.cos(angle),
    y: 50 + 38 * Math.sin(angle),
  };
}

export function CollaborationMap({
  agents,
  handoffs,
  currentStep,
}: {
  agents: AgentProfile[];
  handoffs: WorkflowHandoff[];
  currentStep: WorkflowStepDefinition;
}) {
  const activeIds = new Set(currentStep.activeAgentIds);
  const activeHandoffs = handoffs.filter((h) => h.status !== "locked");
  const agentName = (id: string) => agents.find((a) => a.id === id)?.shortName ?? id;

  const agentPositions = agents.map((agent, i) => ({
    agent,
    pos: getAgentPos(agent.id, i, agents.length),
  }));

  const posMap = Object.fromEntries(agentPositions.map(({ agent, pos }) => [agent.id, pos]));

  return (
    <section className="relay-card" aria-labelledby="collaboration-map-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="collaboration-map-heading" className="font-semibold">Agent Collaboration Map</h2>
          <p className="mt-1 text-sm text-slate-400">Live handoff graph — active agents and coordination edges update as the workflow advances.</p>
        </div>
        <Badge tone="accent">{activeHandoffs.length} handoffs unlocked</Badge>
      </div>

      <div className="mt-5 w-full overflow-hidden rounded-2xl border border-slate-700/60 bg-slate-950/40">
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="xMidYMid meet"
          className="w-full"
          style={{ height: "clamp(220px, 28vw, 380px)" }}
          aria-hidden="true"
        >
          <defs>
            <radialGradient id="node-active" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(56,189,248,0.35)" />
              <stop offset="100%" stopColor="rgba(56,189,248,0)" />
            </radialGradient>
            <radialGradient id="node-complete" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(52,211,153,0.28)" />
              <stop offset="100%" stopColor="rgba(52,211,153,0)" />
            </radialGradient>
            <marker id="arrow" markerWidth="4" markerHeight="4" refX="3" refY="2" orient="auto">
              <path d="M0,0 L4,2 L0,4 Z" fill="rgba(148,163,184,0.5)" />
            </marker>
            <marker id="arrow-active" markerWidth="4" markerHeight="4" refX="3" refY="2" orient="auto">
              <path d="M0,0 L4,2 L0,4 Z" fill="rgba(56,189,248,0.9)" />
            </marker>
            <marker id="arrow-complete" markerWidth="4" markerHeight="4" refX="3" refY="2" orient="auto">
              <path d="M0,0 L4,2 L0,4 Z" fill="rgba(52,211,153,0.9)" />
            </marker>
          </defs>

          {activeHandoffs.map((handoff) => {
            const from = posMap[handoff.fromAgentId];
            const to = posMap[handoff.toAgentId];
            if (!from || !to) return null;
            const isComplete = handoff.status === "complete";
            const mx = (from.x + to.x) / 2 + (to.y - from.y) * 0.18;
            const my = (from.y + to.y) / 2 - (to.x - from.x) * 0.18;
            return (
              <path
                key={handoff.id}
                d={`M ${from.x} ${from.y} Q ${mx} ${my} ${to.x} ${to.y}`}
                fill="none"
                stroke={isComplete ? "rgba(52,211,153,0.7)" : "rgba(56,189,248,0.55)"}
                strokeWidth="0.8"
                strokeDasharray={isComplete ? "none" : "2 1.2"}
                markerEnd={isComplete ? "url(#arrow-complete)" : "url(#arrow-active)"}
              />
            );
          })}

          {agentPositions.map(({ agent, pos }) => {
            const isActive = activeIds.has(agent.id);
            const isComplete = agent.status === "complete";
            const isBlocked = agent.status === "blocked";
            const nodeColor = isActive
              ? "rgba(56,189,248,0.9)"
              : isComplete
              ? "rgba(52,211,153,0.85)"
              : isBlocked
              ? "rgba(248,113,113,0.85)"
              : "rgba(100,116,139,0.6)";
            const glowId = isActive ? "url(#node-active)" : isComplete ? "url(#node-complete)" : undefined;

            return (
              <g key={agent.id} transform={`translate(${pos.x}, ${pos.y})`}>
                {glowId && <circle r="7" fill={glowId} />}
                <circle
                  r="4.2"
                  fill="rgba(6,16,31,0.92)"
                  stroke={nodeColor}
                  strokeWidth={isActive ? "1.2" : "0.8"}
                />
                <circle r="1.8" fill={nodeColor} />
                <text
                  y="7.5"
                  textAnchor="middle"
                  fontSize="2.8"
                  fill={isActive ? "rgba(224,242,254,0.95)" : "rgba(148,163,184,0.8)"}
                  fontWeight={isActive ? "700" : "400"}
                >
                  {agent.shortName}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <div className="mt-4 space-y-2">
        {activeHandoffs.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/20 p-4 text-sm leading-6 text-slate-400">
            Handoffs unlock after the commander assigns specialist work and agents start sharing evidence.
          </div>
        ) : (
          activeHandoffs.map((handoff) => (
            <article
              key={handoff.id}
              className="grid gap-3 rounded-2xl border border-slate-700/70 bg-slate-950/25 p-3 md:grid-cols-[160px_1fr_120px] md:items-center"
            >
              <div className="text-xs font-semibold text-slate-200">
                {agentName(handoff.fromAgentId)} → {agentName(handoff.toAgentId)}
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-100">{handoff.title}</p>
                <p className="mt-1 text-xs leading-5 text-slate-400">{handoff.summary}</p>
              </div>
              <Badge tone={statusTone[handoff.status]}>{handoff.status}</Badge>
            </article>
          ))
        )}
      </div>
    </section>
  );
}