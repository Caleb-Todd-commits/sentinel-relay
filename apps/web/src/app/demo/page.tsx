import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { Badge } from "@/components/ui/Badge";
import { mockAgents, mockEvidence, mockIncidentCase, mockMessages } from "@/lib/mockIncident";

const flow = [
  "Commander opens a Band incident room.",
  "Forensics and Code Review agents collect evidence.",
  "Threat Intel verifies confidence without overclaiming.",
  "Risk & Compliance challenges the breach classification.",
  "A human security lead approves containment.",
  "Remediation tasks and final audit report are generated.",
];

export default function DemoPage() {
  return (
    <main className="relay-page">
      <SiteHeader />
      <section className="relay-shell space-y-6 py-8">
        <div className="relay-card space-y-4">
          <div className="flex flex-wrap gap-2">
            <Badge tone="warning">Sample incident</Badge>
            <Badge>Mock Mode</Badge>
            <Badge tone="accent">Band-ready architecture</Badge>
          </div>
          <h1 className="text-3xl font-bold tracking-tight md:text-4xl">{mockIncidentCase.title}</h1>
          <p className="max-w-4xl text-sm leading-6 text-slate-300 md:text-base">{mockIncidentCase.summary}</p>
          <div className="grid gap-3 md:grid-cols-4">
            <div className="relay-card-compact"><p className="relay-label">Messages</p><p className="mt-2 text-2xl font-bold">{mockMessages.length}</p></div>
            <div className="relay-card-compact"><p className="relay-label">Agents</p><p className="mt-2 text-2xl font-bold">{mockAgents.length}</p></div>
            <div className="relay-card-compact"><p className="relay-label">Evidence</p><p className="mt-2 text-2xl font-bold">{mockEvidence.length}</p></div>
            <div className="relay-card-compact"><p className="relay-label">Core proof</p><p className="mt-2 text-lg font-bold">Challenge + approval</p></div>
          </div>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link href="/war-room" className="relay-button-primary">Launch War Room</Link>
            <Link href="/report" className="relay-button-secondary">Preview Final Report</Link>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <section className="relay-card">
            <h2 className="font-semibold">Demo flow</h2>
            <ol className="mt-4 space-y-3">
              {flow.map((item, index) => (
                <li key={item} className="flex gap-3 rounded-xl border border-slate-700/80 bg-slate-950/25 p-3">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-sky-400/10 text-sm font-bold text-sky-100">{index + 1}</span>
                  <span className="text-sm leading-6 text-slate-300">{item}</span>
                </li>
              ))}
            </ol>
          </section>
          <section className="relay-card">
            <h2 className="font-semibold">Why this baseline matters</h2>
            <div className="mt-4 space-y-3 text-sm leading-6 text-slate-300">
              <p>The baseline is intentionally demoable before real APIs are connected. That protects the team from losing the pitch because an external integration fails during a live judge review.</p>
              <p>The code structure is already shaped around the final product: structured messages, provider abstraction, agent roster, evidence references, approval gates, remediation tasks, and final report output.</p>
              <p>When Band integration is added, the UI should not need to be rebuilt. The mock collaboration stream is the contract that the real Band provider must satisfy.</p>
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
