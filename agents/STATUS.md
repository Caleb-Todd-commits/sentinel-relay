# Agents Lane — Status (Person 3)

**Scope:** `agents/` only (Python). Demo incident: `INC-1042` (API-key leak after a Friday deploy).
**Branch:** `person3/agents` → PR #2.
**Last updated:** 2026-06-17.

## Current state

- ✅ **Six agents + offline mock flow complete.** Commander/Band Leader, Forensics, Threat Intel, Code Review, Risk & Compliance, Remediation are implemented as pure `handle_turn(ctx) -> AgentMessage` functions behind the transport seam.
- ✅ **SOC-grade analyst enrichment complete.** Every agent's canned mock output and matching `prompt.md` system prompt was rewritten to read like a real incident responder in its discipline (credential-type-aware blast radius, issuer-verified exposure window, sibling-credential hunt, GDPR/CCPA breach-threshold reasoning, issuer-first containment). Schema, `payload.kind` set, message types, routing, and the 14-step flow are unchanged.
- ✅ **Mock flow green:** `python3 agents/mock/run_mock_flow.py` → `OK: 14/14 messages schema-valid, @mention routing verified, human approval gate present, final report generated.` Deterministic, zero network, zero model calls. Unchanged by the live-mode work — still 14/14.
- ✅ **Live mode built and verified.** Real AI/ML API enrichment runs over the same `handle_turn` seam, the same schema validator (with the same bounded retry), and the same inc-1042 fixtures — only the transport input and the per-agent LLM call differ. The `SENTINEL_RELAY_AGENT_OFFLINE_MODE` toggle selects mock (canned) vs live; both are fully working. Full inc-1042 flow verified live against the real key: **13/14 turns produced live** by `gpt-4o-mini` (the step-11 human-approval gate is a human actor, not an LLM, so it stays the canned deterministic decision in both modes), 0 errored, 14/14 schema-valid. Four new files, all in the agents lane:
  - `agents/common/aimlapi_client.py` — thin OpenAI-compatible client (stdlib `urllib` only; no new dependency). Config from the existing `.env` keys (`AIMLAPI_API_KEY`/`AIMLAPI_BASE_URL`/`AIMLAPI_MODEL`).
  - `agents/common/live_agent.py` — LLM enrichment layer: builds the turn from `prompt.md` + `AgentTurnContext`, parses the reply into an `AgentMessage`, and plugs into the existing `run_agent_turn` seam.
  - `agents/live/run_live_flow.py` — toggle-aware runner; tags every message `LIVE` / `CANNED` / `ERROR` in the console without changing the schema.
  - `agents/mock/run_mock_flow.py` — minimal refactor only (extracted `build_steps()` + `CANNED_TURNS` so the live runner reuses the one 14-step flow); CLI and behaviour unchanged.
- ✅ **No-fallback error handling.** A failed live turn (API error, timeout, or off-schema after the seam's retries) is never replaced by canned data. The runner prints the real exception and the offending output, marks that turn `ERROR`, continues past it so every failure is visible in one run, and exits non-zero. Verified with a deliberately bad key: all live turns reported the real HTTP 401, only the canned human-gate message reached the transcript, `No canned substitution was made.`, exit 1.
  - Run live: `python3 agents/live/run_live_flow.py` (needs a real `AIMLAPI_API_KEY`); `--json` emits the raw `AgentMessage[]`.

## How to run

```bash
python3 agents/mock/run_mock_flow.py          # human-readable transcript + 14/14 self-check
python3 agents/mock/run_mock_flow.py --json    # full AgentMessage[] (canonical v0.4.0)

python3 agents/live/run_live_flow.py           # LIVE: real AI/ML API calls (needs AIMLAPI_API_KEY)
python3 agents/live/run_live_flow.py --json    # raw live AgentMessage[]
SENTINEL_RELAY_AGENT_OFFLINE_MODE=true python3 agents/live/run_live_flow.py   # same runner, canned
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
