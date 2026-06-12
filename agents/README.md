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
