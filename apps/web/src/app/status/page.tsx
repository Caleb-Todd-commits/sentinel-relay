import { SiteHeader } from "@/components/SiteHeader";
import { Badge } from "@/components/ui/Badge";

const checks = [
  { name: "App routes", status: "ready", detail: "/, /war-room, /report" },
  { name: "Multi-agent workflow", status: "ready", detail: "10-step incident flow: triage, evidence, challenge, approval, remediation, report" },
  { name: "Collaboration layer", status: "ready", detail: "Band provider with in-memory fallback — switches via environment variable" },
  { name: "Human approval gate", status: "ready", detail: "Containment blocked until security lead records an explicit scoped decision" },
  { name: "Audit report", status: "ready", detail: "Generated from the structured collaboration record — traceable to source messages" },
  { name: "Credentials", status: "safe", detail: "No secrets in source control" },
];

export default function StatusPage() {
  return (
    <main className="relay-page">
      <SiteHeader />
      <section className="relay-shell space-y-5 py-8">
        <div className="relay-card">
          <h1 className="text-3xl font-bold tracking-tight">System Status</h1>
          <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-300">
            Runtime readiness across the coordination layer, workflow engine, and output artifacts.
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
