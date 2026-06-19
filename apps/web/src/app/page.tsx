import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { Badge } from "@/components/ui/Badge";
import { mockAgents, mockIncidentCase } from "@/lib/mockIncident";

const differentiators = [
  {
    title: "Structured coordination",
    body: "Agents pass evidence, challenges, and approvals through a shared incident room — not isolated chat sessions.",
  },
  {
    title: "Human approval gate",
    body: "High-impact containment actions are blocked until a human security lead explicitly approves scope.",
  },
  {
    title: "Full audit trail",
    body: "Every handoff, challenge, and decision becomes a replayable record — who found what, who challenged it, what was approved.",
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
              <Badge tone="accent">Multi-agent incident response</Badge>
              <Badge>{mockAgents.length} specialist agents</Badge>
            </div>
            <div className="space-y-4">
              <h1 className="max-w-4xl text-5xl font-bold tracking-tight md:text-6xl">Sentinel Relay</h1>
              <p className="max-w-3xl text-lg leading-8 text-slate-300">
                Specialized agents coordinate through Band to investigate a security incident — exchanging evidence, challenging weak conclusions, and requesting human approval before any high-impact action is taken.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href="/scenarios" className="relay-button-primary">Run a live scenario</Link>
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
              <Badge tone="warning">Active scenario</Badge>
              <h2 className="mt-3 text-2xl font-bold">{mockIncidentCase.title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">{mockIncidentCase.summary}</p>
            </div>
            <dl className="grid gap-4 sm:grid-cols-2">
              <div>
                <dt className="relay-label">Affected system</dt>
                <dd className="mt-1.5 font-semibold text-slate-100">{mockIncidentCase.affectedSystem}</dd>
              </div>
              <div>
                <dt className="relay-label">Decision model</dt>
                <dd className="mt-1.5 font-semibold text-slate-100">Human approval gate</dd>
              </div>
              <div>
                <dt className="relay-label">Agent behavior</dt>
                <dd className="mt-1.5 font-semibold text-slate-100">Agents challenge each other</dd>
              </div>
              <div>
                <dt className="relay-label">Final artifact</dt>
                <dd className="mt-1.5 font-semibold text-slate-100">Audit report</dd>
              </div>
            </dl>
          </aside>
        </div>
      </section>
    </main>
  );
}
