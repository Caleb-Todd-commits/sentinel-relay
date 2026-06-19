"use client";

import Link from "next/link";
import { useState } from "react";
import { SiteHeader } from "@/components/SiteHeader";
import { Badge } from "@/components/ui/Badge";

type RunState = "idle" | "running" | "done" | "error";

const scenarios = [
  {
    id: "INC-1042",
    title: "Possible API Key Exposure After Friday Deploy",
    summary:
      "A suspicious usage spike appeared shortly after a Friday deployment. Agents determine whether a fallback service token was exposed, what customer data was accessed, what actions require approval, and what remediation should happen next.",
    rootCause: "Fallback token path introduced by deploy",
    recordsAffected: "10,227 customer records",
    credentials: "Service API token (fallback path)",
    tone: "warning" as const,
    tag: "Credential exposure",
  },
  {
    id: "INC-1043",
    title: "OIDC Trust Regression Exposed Analytics Exporter Token",
    summary:
      "An IAM trust-policy change widened GitHub OIDC access from the protected main branch to a repo-wide wildcard. A CI workflow minted a federated token that was used to export customer records from an unprotected ref.",
    rootCause: "OIDC trust policy widened to unprotected refs",
    recordsAffected: "3,636 customer records",
    credentials: "GitHub Actions OIDC token (federated)",
    tone: "danger" as const,
    tag: "IAM trust regression",
  },
];

function ScenarioCard({ scenario }: { scenario: typeof scenarios[number] }) {
  const [state, setState] = useState<RunState>("idle");
  const [result, setResult] = useState<{ roomId?: string; messagesPosted?: number; error?: string } | null>(null);

  async function runScenario() {
    setState("running");
    setResult(null);
    try {
      const res = await fetch("/api/run-scenario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ incidentId: scenario.id }),
      });
      const body = await res.json();
      if (!res.ok || !body.ok) {
        setResult({ error: body.error ?? "Workflow failed." });
        setState("error");
        return;
      }
      setResult({
        roomId: body.roomId,
        messagesPosted: body.messagesPosted,
      });
      setState("done");
    } catch (err) {
      setResult({ error: err instanceof Error ? err.message : "Network error." });
      setState("error");
    }
  }

  return (
    <article className="relay-card space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="flex flex-wrap gap-2">
            <Badge tone={scenario.tone}>{scenario.id}</Badge>
            <Badge>{scenario.tag}</Badge>
          </div>
          <h2 className="text-xl font-bold tracking-tight">{scenario.title}</h2>
        </div>
        {state === "done" ? (
          <Badge tone="success">Complete</Badge>
        ) : state === "running" ? (
          <Badge tone="accent">Running…</Badge>
        ) : state === "error" ? (
          <Badge tone="danger">Error</Badge>
        ) : null}
      </div>

      <p className="text-sm leading-6 text-slate-300">{scenario.summary}</p>

      <dl className="grid gap-3 sm:grid-cols-3">
        <div>
          <dt className="relay-label">Root cause</dt>
          <dd className="mt-1.5 text-sm font-semibold text-slate-100">{scenario.rootCause}</dd>
        </div>
        <div>
          <dt className="relay-label">Records affected</dt>
          <dd className="mt-1.5 text-sm font-semibold text-slate-100">{scenario.recordsAffected}</dd>
        </div>
        <div>
          <dt className="relay-label">Credential type</dt>
          <dd className="mt-1.5 text-sm font-semibold text-slate-100">{scenario.credentials}</dd>
        </div>
      </dl>

      {state === "idle" && (
        <div className="rounded-2xl border border-slate-700/80 bg-slate-950/25 p-4">
          <p className="text-sm leading-6 text-slate-400">
            Six agents will investigate this incident live — Forensics, Code Review, Threat Intel, Risk &amp; Compliance, Remediation, and Band Leader. Each derives findings from the evidence files. The War Room will populate as they post.
          </p>
        </div>
      )}

      {state === "running" && (
        <div className="rounded-2xl border border-sky-400/25 bg-sky-400/10 p-4">
          <p className="text-sm font-semibold text-sky-100">Running workflow…</p>
          <p className="mt-1 text-sm leading-6 text-slate-300">
            Posting 18 agent messages — findings, challenge, approval, and remediation — into the incident room.
          </p>
        </div>
      )}

      {state === "done" && result && (
        <div className="rounded-2xl border border-emerald-400/30 bg-emerald-400/10 p-4 space-y-3">
          <p className="text-sm font-semibold text-emerald-100">
            {result.messagesPosted} agent messages posted.
          </p>
          <p className="text-xs text-slate-400 font-mono">Room: {result.roomId}</p>
          <Link
            href={`/scenarios/room?room=${encodeURIComponent(result.roomId ?? "")}&incident=${scenario.id}`}
            className="relay-button-primary inline-flex"
          >
            View live results →
          </Link>
        </div>
      )}

      {state === "error" && result?.error && (
        <div className="rounded-2xl border border-red-400/30 bg-red-400/10 p-4">
          <p className="text-sm font-semibold text-red-100">Workflow failed</p>
          <p className="mt-1 text-xs leading-5 text-slate-300">{result.error}</p>
          <p className="mt-2 text-xs text-slate-500">Make sure the app is running locally with the Python venv installed.</p>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        {state === "idle" || state === "error" ? (
          <button
            type="button"
            onClick={runScenario}
            className="relay-button-primary"
          >
            Run {scenario.id} live
          </button>
        ) : state === "running" ? (
          <button type="button" disabled className="relay-button-primary disabled:cursor-not-allowed disabled:opacity-50">
            Running…
          </button>
        ) : (
          <button type="button" onClick={runScenario} className="relay-button-secondary">
            Run again
          </button>
        )}
        {state !== "running" && (
          <Link href="/war-room" className="relay-button-secondary">
            Open War Room
          </Link>
        )}
      </div>
    </article>
  );
}

export default function ScenariosPage() {
  return (
    <main className="relay-page">
      <SiteHeader />
      <section className="relay-shell space-y-6 py-8">
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <Badge tone="accent">Live agent workflows</Badge>
            <Badge>2 incident scenarios</Badge>
          </div>
          <h1 className="text-3xl font-bold tracking-tight md:text-4xl">Incident Scenarios</h1>
          <p className="max-w-3xl text-sm leading-6 text-slate-300 md:text-base">
            Each scenario runs the full six-agent workflow against a different evidence packet. Agents derive their findings from the evidence — not from a script — so each incident produces genuinely different analysis.
          </p>
        </div>

        <div className="space-y-5">
          {scenarios.map((scenario) => (
            <ScenarioCard key={scenario.id} scenario={scenario} />
          ))}
        </div>

        <div className="relay-card space-y-3">
          <h2 className="font-semibold">What makes these different</h2>
          <div className="grid gap-4 md:grid-cols-3 text-sm leading-6 text-slate-300">
            <div>
              <p className="font-semibold text-slate-100">Different root causes</p>
              <p className="mt-1 text-slate-400">INC-1042 is a committed fallback token path. INC-1043 is an OIDC trust-policy regression. The agents read the actual evidence to figure out which.</p>
            </div>
            <div>
              <p className="font-semibold text-slate-100">Different findings</p>
              <p className="mt-1 text-slate-400">Forensics, Code Review, and Threat Intel each derive different facts, different record counts, and different containment steps from each evidence packet.</p>
            </div>
            <div>
              <p className="font-semibold text-slate-100">Same coordination pattern</p>
              <p className="mt-1 text-slate-400">Both incidents go through the same Band workflow: evidence → challenge → approval gate → remediation → audit report. The structure is the product.</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
