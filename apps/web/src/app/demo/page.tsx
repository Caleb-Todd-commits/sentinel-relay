import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { Badge } from "@/components/ui/Badge";
import { mockAgents, mockEvidence, mockIncidentCase, mockMessages } from "@/lib/mockIncident";

const flow = [
  "Band Leader opens a shared incident room.",
  "Forensics and Code Review agents collect and post evidence.",
  "Threat Intel assesses confidence without overclaiming.",
  "Risk & Compliance challenges the breach classification.",
  "A human security lead approves containment scope.",
  "Remediation tasks and a final audit report are generated.",
];

export default function DemoPage() {
  return (
    <main className="relay-page">
      <SiteHeader />
      <section className="relay-shell space-y-6 py-8">
        <div className="relay-card space-y-4">
          <div className="flex flex-wrap gap-2">
            <Badge tone="warning">Active scenario</Badge>
            <Badge tone="accent">Band-powered coordination</Badge>
          </div>
          <h1 className="text-3xl font-bold tracking-tight md:text-4xl">{mockIncidentCase.title}</h1>
          <p className="max-w-4xl text-sm leading-6 text-slate-300 md:text-base">{mockIncidentCase.summary}</p>
          <dl className="grid gap-4 md:grid-cols-4">
            <div>
              <dt className="relay-label">Messages</dt>
              <dd className="mt-1.5 text-2xl font-bold text-slate-100">{mockMessages.length}</dd>
            </div>
            <div>
              <dt className="relay-label">Agents</dt>
              <dd className="mt-1.5 text-2xl font-bold text-slate-100">{mockAgents.length}</dd>
            </div>
            <div>
              <dt className="relay-label">Evidence items</dt>
              <dd className="mt-1.5 text-2xl font-bold text-slate-100">{mockEvidence.length}</dd>
            </div>
            <div>
              <dt className="relay-label">Core proof</dt>
              <dd className="mt-1.5 text-lg font-bold text-slate-100">Challenge + approval</dd>
            </div>
          </dl>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link href="/war-room" className="relay-button-primary">Open War Room</Link>
            <Link href="/report" className="relay-button-secondary">View Final Report</Link>
          </div>
        </div>

        <section className="relay-card">
          <h2 className="font-semibold">What happens in the War Room</h2>
          <ol className="mt-4 space-y-3">
            {flow.map((item, index) => (
              <li key={item} className="flex gap-3">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-sky-400/10 text-sm font-bold text-sky-100">{index + 1}</span>
                <span className="text-sm leading-6 text-slate-300 pt-0.5">{item}</span>
              </li>
            ))}
          </ol>
        </section>

        <section className="relay-card relay-card-highlight space-y-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <Badge tone="accent">Live agents</Badge>
              <h2 className="mt-3 text-lg font-semibold">Run a second incident — different evidence, different findings</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
                A second scenario (INC-1043) covers an IAM trust-policy regression that exposed a GitHub OIDC token — a completely different root cause, different record count, and different containment steps. The same six agents investigate it live from the evidence files.
              </p>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 text-sm">
            <div className="rounded-xl border border-slate-700/70 bg-slate-950/25 p-3">
              <p className="relay-label">INC-1042 — this scenario</p>
              <p className="mt-1.5 font-semibold text-slate-100">Fallback API token · 10,227 records</p>
            </div>
            <div className="rounded-xl border border-slate-700/70 bg-slate-950/25 p-3">
              <p className="relay-label">INC-1043 — alternate scenario</p>
              <p className="mt-1.5 font-semibold text-slate-100">OIDC trust regression · 3,636 records</p>
            </div>
          </div>
          <Link href="/scenarios" className="relay-button-primary inline-flex">
            Run live scenarios →
          </Link>
        </section>
      </section>
    </main>
  );
}
