# Evidence-Driven AI/ML API Workflow

## Purpose

This is the prize-path workflow for Sentinel Relay.

The original War Room remains a stable scripted demo. This workflow adds a
realistic evidence packet and makes the agents derive findings from that packet
before posting the collaboration trail through the Band-backed app routes.

It also gives the AI/ML API partner prize a concrete role:

- Risk & Compliance uses AI/ML API as a policy gate over specialist findings.
- Band Leader uses AI/ML API to synthesize the Band room into a judge-ready
  status update with evidence IDs, next actions, open questions, and the value
  of Band coordination.

## Files

```txt
data/incidents/inc-1042/
  evidence_manifest.json
  api_gateway_logs.jsonl
  auth_events.jsonl
  cloudtrail_events.jsonl
  git_diff.patch
  secret_scan.json
  suspicious_ips.json
  incident_policy.json
  ground_truth_for_judges.md

scripts/demo/
  run-evidence-band-workflow.py
  verify-evidence-pack.py
```

## Safety

The evidence packet is synthetic lab evidence using realistic log formats.

It does not contain live secrets, real customer personal data, or real incident
telemetry. IP addresses use documentation ranges, and token-like values are
redacted labels only.

## Environment

The workflow uses the same root `.env` as the app.

Required for live Band:

```txt
BAND_PROVIDER_ENABLED="true"
NEXT_PUBLIC_ENABLE_BAND_MODE="true"
BAND_LEADER_AGENT_API_KEY
BAND_LEADER_AGENT_ID
FORENSICS_AGENT_ID
THREAT_INTEL_AGENT_ID
CODE_REVIEW_AGENT_ID
RISK_COMPLIANCE_AGENT_ID
REMEDIATION_AGENT_ID
```

Required for live AI/ML API partner usage:

```txt
AIMLAPI_API_KEY
AIMLAPI_BASE_URL="https://api.aimlapi.com/v1"
AIMLAPI_MODEL="gpt-4o-mini"
```

`BAND_HUMAN_API_KEY` is still optional. Without it, Sentinel Relay uses the
local server mirror for judge-facing room history.

## Run The Live Prize Rehearsal

Terminal 1:

```bash
set -a
. ./.env
set +a
corepack pnpm dev
```

Terminal 2:

```bash
corepack pnpm workflow:evidence:live
```

The live command fails if AI/ML API cannot be called. That is intentional for
the partner-prize rehearsal.

For deterministic local testing without the partner API:

```bash
corepack pnpm workflow:evidence --skip-aimlapi
```

For static checks only:

```bash
corepack pnpm workflow:evidence:verify
```

## What The Runner Posts To Band

1. Band Leader assigns the evidence packet to specialists.
2. Forensics posts suspicious fallback-token reads and record counts.
3. Code Review links the behavior to the Friday deploy fallback path.
4. Threat Intel confirms suspicious behavior without overclaiming attribution.
5. Risk & Compliance uses AI/ML API to challenge external notification and
   recommend containment-only approval.
6. Human Security Lead approval is recorded.
7. Remediation task status is posted.
8. Band Leader uses AI/ML API to synthesize the Band room into a final status.

Each structured message includes evidence IDs and is routed through the existing
`/api/collaboration` server routes, so Band remains the coordination layer.

## Judge Framing

Use this workflow to show that Sentinel Relay is more than a project frame:

- Agents do not merely narrate. They read evidence and produce findings.
- Band is not a notification sink. It carries room creation, handoffs, task
  state, approvals, audit events, and shared context.
- AI/ML API is not decorative. It performs cross-agent policy reasoning and
  final synthesis over the Band room trail.
- Risk & Compliance actively blocks overclaiming and keeps the incident
  enterprise-safe.

The strongest live moment is the Risk gate: the system finds enough evidence for
urgent containment, but refuses to claim customer notification is ready until
scope and Legal review are complete.
