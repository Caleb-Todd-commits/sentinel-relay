# Sentinel Relay Remote Agents

These folders contain the six remote agent workers used by Sentinel Relay:

- `Band Leader`
- `forensics`
- `threat_intel`
- `code_review`
- `risk_compliance`
- `remediation`

Each worker is designed to run in your infrastructure and connect to Band/Thenvoi through the Python SDK. The SDK path matters because Band uses REST for agent actions and WebSocket subscriptions for real-time messages. The dashboard server adapter can create rooms and post structured events, but the live agent workers should stay connected with the SDK so they can receive @mentions.

## Install

From this folder:

```bash
uv venv
uv sync
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install "thenvoi-sdk[langgraph]" langchain-openai langgraph python-dotenv
```

## Configure

Copy the root `.env.example` to `.env` and fill the per-agent values:

```env
BAND_LEADER_AGENT_ID=""
BAND_LEADER_AGENT_API_KEY=""
FORENSICS_AGENT_ID=""
FORENSICS_AGENT_API_KEY=""
THREAT_INTEL_AGENT_ID=""
THREAT_INTEL_AGENT_API_KEY=""
CODE_REVIEW_AGENT_ID=""
CODE_REVIEW_AGENT_API_KEY=""
RISK_COMPLIANCE_AGENT_ID=""
RISK_COMPLIANCE_AGENT_API_KEY=""
REMEDIATION_AGENT_ID=""
REMEDIATION_AGENT_API_KEY=""
OPENAI_API_KEY=""
```

## Run one agent

```bash
uv run python commander/main.py
```

## Run all agents in separate terminals

```bash
uv run python commander/main.py
uv run python forensics/main.py
uv run python threat_intel/main.py
uv run python code_review/main.py
uv run python risk_compliance/main.py
uv run python remediation/main.py
```

For the final demo, start the agents before running the live Band workflow so the agents are already connected when the dashboard creates the incident room and posts @mentioned tasks.

## Run via the Sentinel Relay collaboration API

For the most deterministic live-demo path, run each Python worker against the
app's collaboration API. The worker polls the room mirror, answers routed task
assignments through `common/turn_adapter.py`, and posts the validated response
back through `/api/collaboration/messages`. The Next.js route then stores the
message in the local mirror and publishes it to Band.

```bash
export SENTINEL_RELAY_AGENT_RUNTIME="collaboration-api"
export SENTINEL_RELAY_APP_URL="http://127.0.0.1:3000"
export SENTINEL_RELAY_AGENT_ROOM_ID="paste-room-id-from-war-room"

uv run python commander/main.py
uv run python forensics/main.py
uv run python threat_intel/main.py
uv run python code_review/main.py
uv run python risk_compliance/main.py
uv run python remediation/main.py
```

Use `SENTINEL_RELAY_AGENT_ONCE=true` to process at most one routed turn for
debugging. The worker keeps replay state in the system temp directory by default;
set `SENTINEL_RELAY_AGENT_STATE_FILE` to override it.

## Mock / offline flow (zero network, zero model calls)

The six agents are implemented as pure `handle_turn(ctx) -> AgentMessage` functions
in each `*/agent.py`, decoupled from Band behind `common/interface.py`. The mock
runner drives the full 18-step Commander-led @mention chain using only synthetic
fixtures and the standard library — no API key needed:

```bash
python3 agents/mock/run_mock_flow.py                         # INC-1042 transcript + self-checks
python3 agents/mock/run_mock_flow.py --incident-id INC-1043  # OIDC trust-regression transcript
python3 agents/mock/run_mock_flow.py --json                  # full AgentMessage[] for the frontend
python3 agents/mock/verify_evidence_analysis.py
python3 agents/mock/verify_agent_quality.py
python3 agents/mock/verify_fixture_generalization.py
```

The evidence workflow runner can post either validated transcript through the
app collaboration routes:

```bash
python3 scripts/demo/run-evidence-band-workflow.py --incident-id INC-1042
python3 scripts/demo/run-evidence-band-workflow.py --incident-id INC-1043
```

Every message is schema-validated (with retry) against `AgentMessage` v0.4.0 before it
is routed. The same `handle_turn` seam is what Person 2's Band transport calls in live
mode; only the transport and an optional LLM enrichment layer change.

The discipline agents also share `common/evidence_analysis.py`, which derives the
major incident facts from raw fixture files: unauthorized record counts, source IPs,
exposure-window timestamps, code/config changes, secret-scan status, threat timing,
and policy gates. This keeps agent claims tied to evidence instead of frozen prose.

`verify_agent_quality.py` is the higher-level behavior gate: it checks evidence
grounding, Risk's challenge posture, held customer-notification approval, AI/ML API
partner-tool metadata, and overclaim prevention across the full room transcript.

`verify_fixture_generalization.py` runs the same 18-step mock room workflow for
`INC-1043`, covering GitHub OIDC trust-policy misuse. It proves the agents can
switch from the fallback-token incident to a federated-credential incident
without leaking primary-demo wording.

## AI/ML API enrichment

Risk & Compliance and Band Leader can use AI/ML API for the partner-prize path:

- Risk & Compliance: policy-gate challenge over specialist findings and evidence facts.
- Band Leader: final room synthesis over the Band trail and evidence facts.

The enrichment is guarded. It sends only evidence-derived facts and message summaries,
expects JSON back, sanitizes severity/evidence IDs/notification posture/confidence, and
falls back deterministically when disabled or unavailable.

```bash
export SENTINEL_RELAY_AIMLAPI_ENABLED="true"
export AIMLAPI_API_KEY="..."
export AIMLAPI_BASE_URL="https://api.aimlapi.com/v1"
export AIMLAPI_MODEL="gpt-4o-mini"
```

For a partner-prize rehearsal that should fail if the provider is unavailable:

```bash
export SENTINEL_RELAY_AIMLAPI_REQUIRE_LIVE="true"
```

Offline guardrail check:

```bash
python3 agents/mock/verify_aimlapi_enrichment.py
```

## Band turn adapter contract

`common/turn_adapter.py` is the live-worker bridge from Band to the agent lane. It
accepts a `CollaborationRoomSnapshot` plus the inbound routed message, derives the
agent task, assembles `AgentTurnContext`, calls the correct `handle_turn`, validates
the `AgentMessage`, and returns the exact JSON body for:

```txt
POST /api/collaboration/messages
```

Verify that contract offline:

```bash
python3 agents/mock/verify_turn_adapter.py
python3 agents/mock/verify_collaboration_api_worker.py
```

These checks prove routed task assignments, approval-to-remediation handoff, live
room ID preservation, case-id-based fixture loading, schema validation, API
post-body construction, worker orchestration, and duplicate suppression without
touching Band, Vercel, OpenAI, or any secrets.
