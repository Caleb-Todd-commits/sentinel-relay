# Evidence-driven Band and AI/ML API workflow

## Purpose

Sentinel Relay now exposes two complementary production paths:

- Seeded evidence scenarios use the Band-backed `/api/agent_run` workflow with verified replay as a labeled fallback.
- Open-ended fictional scenarios use `/api/custom-incident` for server-side AI/ML API reasoning across six specialist roles.

The Python agent implementations, synthetic evidence packets, and verification runners remain the evidence-quality foundation for both seeded scenarios.

## Seeded evidence

`data/incidents/inc-1042/` and `data/incidents/inc-1043/` contain synthetic manifests, API and authentication activity, cloud events, code/configuration artifacts, external indicators, and incident policy.

The workflow derives record counts, exposure windows, introducing changes, threat confidence, and policy gates from those files. It does not use real customer data, credentials, or incident telemetry.

## Seeded execution

The UI posts `{ action: "investigate", scenarioId }` to `/api/agent_run`. The server attempts live Band execution and streams agent messages. It stops at `approval_required`. A later approved continuation unlocks remediation and the final report.

When live execution cannot complete, the route emits `Verified replay` from the evidence-backed transcript. The interface exposes this mode.

## Open-ended execution

The custom route receives a sanitized description and calls AI/ML API with role-specific prompts:

1. Band Leader frames the incident or asks one clarifying question.
2. Forensics, Code Review, and Threat Intel assess the same framing in parallel.
3. Risk & Compliance and Remediation receive the accumulated findings.
4. Agents without a useful perspective skip instead of repeating prior output.

This path does not claim Band-room execution. It demonstrates generalization and cross-agent context sharing through server-side model orchestration.

## Required environment

```text
BAND_PROVIDER_ENABLED="true"
BAND_API_BASE_URL
BAND_LEADER_AGENT_API_KEY
BAND_LEADER_AGENT_ID
FORENSICS_AGENT_ID
THREAT_INTEL_AGENT_ID
CODE_REVIEW_AGENT_ID
RISK_COMPLIANCE_AGENT_ID
REMEDIATION_AGENT_ID

AIMLAPI_API_KEY
AIMLAPI_BASE_URL="https://api.aimlapi.com/v1"
AIMLAPI_MODEL
SENTINEL_RELAY_AIMLAPI_ENABLED="true"
SENTINEL_RELAY_RUN_SIGNING_SECRET
```

All credentials are server-only. Visitors never enter keys.

## Verification

```bash
corepack pnpm verify
python3 scripts/demo/verify-agent-run-api.py
node scripts/dev/verify-streamlined-browser.mjs https://sentinel-relay-alpha.vercel.app
```

The model guardrails reject fake evidence IDs, constrain severity, preserve notification holds, and fall back to deterministic evidence-derived summaries where configured.
