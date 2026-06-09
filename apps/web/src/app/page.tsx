import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { Badge } from "@/components/ui/Badge";
import { mockAgents, mockIncidentCase } from "@/lib/mockIncident";

const differentiators = [
  {
    title: "Band as the command layer",
    body: "Agents are designed to pass structured context, evidence, assignments, challenges, and approvals through Band rather than acting as isolated chatbots.",
  },
  {
    title: "High-stakes workflow",
    body: "The demo focuses on cyber incident response where traceability, review, and escalation matter more than raw automation speed.",
  },
  {
    title: "Judge-readable product",
    body: "The War Room makes every handoff visible: who found evidence, who challenged it, who approved action, and what changed because of it.",
  },
];

export default function HomePage() {
  return (
    <main className="relay-page">
      <SiteHeader />
      <section className="relay-shell py-10">
        <div className="grid gap-8 lg:grid-cols-[1.08fr_0.92fr] lg:items-center">
          <div className="space-y-7">
            <div className="flex flex-wrap gap-2">
              <Badge tone="accent">Band Hackathon</Badge>
              <Badge tone="warning">Track 3 · regulated/high-stakes</Badge>
              <Badge>{mockAgents.length} specialist agents</Badge>
            </div>
            <div className="space-y-4">
              <h1 className="max-w-4xl text-5xl font-bold tracking-tight md:text-6xl">Sentinel Relay</h1>
              <p className="max-w-3xl text-lg leading-8 text-slate-300">
                A multi-agent cybersecurity incident command center where specialized agents coordinate through Band, exchange structured evidence, challenge weak conclusions, request human approval, and generate audit-ready incident reports.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href="/demo" className="relay-button-primary">Start demo incident</Link>
              <Link href="/war-room" className="relay-button-secondary">Open War Room</Link>
              <Link href="/report" className="relay-button-secondary">View report</Link>
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              {differentiators.map((item) => (
                <article key={item.title} className="relay-card-compact">
                  <h2 className="font-semibold">{item.title}</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-400">{item.body}</p>
                </article>
              ))}
            </div>
          </div>
          <aside className="relay-card space-y-5">
            <div>
              <Badge tone="warning">Current demo case</Badge>
              <h2 className="mt-3 text-2xl font-bold">{mockIncidentCase.title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">{mockIncidentCase.summary}</p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="relay-card-compact">
                <p className="relay-label">Affected system</p>
                <p className="mt-2 font-semibold">{mockIncidentCase.affectedSystem}</p>
              </div>
              <div className="relay-card-compact">
                <p className="relay-label">Decision model</p>
                <p className="mt-2 font-semibold">Human approval gate</p>
              </div>
              <div className="relay-card-compact">
                <p className="relay-label">Visible proof</p>
                <p className="mt-2 font-semibold">Agent disagreement</p>
              </div>
              <div className="relay-card-compact">
                <p className="relay-label">Final artifact</p>
                <p className="mt-2 font-semibold">Audit report</p>
              </div>
            </div>
          </aside>
        </div>
      </section>
    </main>
  );
}
