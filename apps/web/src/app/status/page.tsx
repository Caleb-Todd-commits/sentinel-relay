import { SiteHeader } from "@/components/SiteHeader";
import { Badge } from "@/components/ui/Badge";

const checks = [
  { name: "Next.js app routes", status: "ready", detail: "/, /demo, /war-room, /report, /status" },
  { name: "Shared schema package", status: "ready", detail: "Canonical TypeScript, JSON Schema, Python-style models, and Band envelope contracts" },
  { name: "Mock incident workflow", status: "ready", detail: "Replayable 10-step flow with challenge, approval gate, remediation unlock, and report readiness" },
  { name: "Collaboration provider", status: "scaffolded", detail: "Mock provider supports local state; Band provider remains a safe scaffold for real integration" },
  { name: "External secrets", status: "safe", detail: "No committed secrets; .env.example only" },
  { name: "Demo fallback", status: "ready", detail: "War Room remains usable without live Band credentials or hosted agents" },
];

export default function StatusPage() {
  return (
    <main className="relay-page">
      <SiteHeader />
      <section className="relay-shell space-y-5 py-8">
        <div className="relay-card">
          <Badge tone="success">Step 5 baseline</Badge>
          <h1 className="mt-4 text-3xl font-bold tracking-tight">Project Baseline Status</h1>
          <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-300">
            This page lets teammates quickly confirm that the app routes, schema contract, mock workflow, collaboration layer, and demo fallback are present before deeper Band and agent work begins.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {checks.map((check) => (
            <article key={check.name} className="relay-card">
              <div className="flex items-start justify-between gap-3">
                <h2 className="font-semibold">{check.name}</h2>
                <Badge tone={check.status === "ready" || check.status === "safe" ? "success" : "accent"}>{check.status}</Badge>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-300">{check.detail}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
