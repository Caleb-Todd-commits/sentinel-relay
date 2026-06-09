# Remote Agent Runbook

## Purpose

The dashboard adapter can create rooms and post structured events, but live multi-agent behavior requires remote agents to stay connected through the Band/Thenvoi SDK.

The SDK path is important because agents need both:

- REST actions for sending messages/events and adding participants
- WebSocket subscriptions for receiving @mentioned messages in real time

## Install

```bash
cd agents
uv venv
uv sync
```

## Configure

Create `agents/.env` from the root `.env.example` or `agents/agent_config.yaml.example`.

Required per agent:

```env
COMMANDER_AGENT_ID=""
COMMANDER_AGENT_API_KEY=""
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

## Offline Contract Check

```bash
SENTINEL_RELAY_AGENT_OFFLINE_MODE=true uv run python commander/main.py
```

This prints the agent contract without connecting to Band.

## Start Agents

Use separate terminals:

```bash
uv run python commander/main.py
uv run python forensics/main.py
uv run python threat_intel/main.py
uv run python code_review/main.py
uv run python risk_compliance/main.py
uv run python remediation/main.py
```

## Demo Order

1. Start all remote agents.
2. Start the web app.
3. Use Band Mode only after the smoke test passes.
4. Open `/war-room`.
5. Start the incident replay.
6. Watch the local dashboard mirror and Band room.
7. Confirm messages with configured target agents are routed as @mentioned Band text messages.
8. Confirm all structured incident messages are posted as Band task events.

## Troubleshooting

### Agent starts but does not respond

Check that the message targeted the agent with a configured participant ID and handle. Band routes agent messages by explicit @mentions.

### Dashboard shows Band warnings

This usually means a participant ID is missing, a message had no routable mention, or Band returned a remote API error. The local mirror should still keep the demo usable.

### Smoke test fails

Check:

- `BAND_API_BASE_URL`
- `BAND_COMMANDER_AGENT_API_KEY`
- Whether the key belongs to a remote agent, not a human user
- Whether the account/workspace has access to the required Band API

### Human API missing

This is acceptable for the hackathon demo. The dashboard uses the local mirror.
