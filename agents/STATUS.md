# Agents Lane — Status (Person 3)

**Scope:** `agents/` only (Python). Demo incident: `INC-1042` (API-key leak after a Friday deploy).
**Branch:** `person3/agents` → PR #2.
**Last updated:** 2026-06-15.

## Current state

- ✅ **Six agents + offline mock flow complete.** Commander/Band Leader, Forensics, Threat Intel, Code Review, Risk & Compliance, Remediation are implemented as pure `handle_turn(ctx) -> AgentMessage` functions behind the transport seam.
- ✅ **SOC-grade analyst enrichment complete.** Every agent's canned mock output and matching `prompt.md` system prompt was rewritten to read like a real incident responder in its discipline (credential-type-aware blast radius, issuer-verified exposure window, sibling-credential hunt, GDPR/CCPA breach-threshold reasoning, issuer-first containment). Schema, `payload.kind` set, message types, routing, and the 14-step flow are unchanged.
- ✅ **Mock flow green:** `python3 agents/mock/run_mock_flow.py` → `OK: 14/14 messages schema-valid, @mention routing verified, human approval gate present, final report generated.` Deterministic, zero network, zero model calls.
- ⏳ **Live mode** (real AI/ML API enrichment over `handle_turn`) — deferred; seam is ready, AIMLAPI key not yet available.

## How to run

```bash
python3 agents/mock/run_mock_flow.py          # human-readable transcript + 14/14 self-check
python3 agents/mock/run_mock_flow.py --json    # full AgentMessage[] (canonical v0.4.0)
```

## Open cross-lane sign-offs

- ⏳ **Person 1 (frontend):** confirm the `payload.kind` set renders — `finding | risk_assessment | challenge | approval_request | remediation_task | report_section | case_opened | task_assignment | approval_decision`.
- ⏳ **Person 2 (shared schema + Band transport):** confirm the Band transport will call per-agent `handle_turn(ctx) -> AgentMessage`, own `AgentTurnContext` assembly + mention→handle mapping, and register `agent-human-approver` as a Band participant.

## Fixture gaps flagged to the scenario owner (Person 4 / `data/incidents`)

These would materially sharpen the analysis but are **not** the agents lane to edit:

1. **No introducing commit SHA, repo name, or branch** in the packet — only diff blob hashes (`61bf8b2→e248d7a`) and the new `.env.release`. Commander/Code Review mark the commit SHA as "to confirm." A `commit`/`author`/`branch` field would let them pin the introducing change and trace propagation.
2. **No container image digest / deploy artifact ID** beyond `release-9814`. An image digest would let Remediation prove the fallback value is purged from built images.
3. **No customer-residency / jurisdiction breakdown** on the exported rows. Risk & Compliance cannot size GDPR vs CCPA notification scope without an EU/CA resident split of the 10,227 records.
4. **No explicit repo-visibility signal** (public vs private), and whether the secret reached forks/PRs/CI. Threat Intel's exposure-velocity argument and Commander's severity triage both hinge on it.
5. **No controller/processor designation** for Payments Platform. A `dataController`/`dataProcessor` fact in `incident_policy.json` would let Risk resolve the notification matrix instead of leaving it open.
