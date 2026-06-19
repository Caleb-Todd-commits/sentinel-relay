# Sentinel Relay

**Sentinel Relay** is a Band-powered multi-agent cybersecurity incident command center. Specialized agents coordinate through Band to investigate evidence, challenge weak conclusions, request scoped human approval, create remediation tasks, and generate an audit-ready report.

## Live Demo

**Production:** https://sentinel-relay-alpha.vercel.app

Open the War Room, run the incident, and watch six agents coordinate through Band — findings, challenges, human approval, and remediation in one shared stream.

## What it does

A Band Leader opens a shared incident room and assigns Forensics, Code Review, Threat Intel, and Risk & Compliance to a suspicious API key exposure after a Friday deployment. Each agent posts structured findings with evidence references. Risk & Compliance challenges the breach classification rather than rubber-stamping it. The Band Leader requests human approval before any high-impact containment. Remediation only acts inside the explicitly approved scope. The final report is generated from the collaboration record, not reconstructed after the fact.

## Why Band is the coordination layer

- Six specialized agents share one incident room
- Findings and evidence references are structured Band messages
- Tasks are routed to named agents, not broadcast
- Risk & Compliance challenges unsupported conclusions in the shared room
- Human approval changes collaboration state and unlocks remediation
- The final report is derived from messages, evidence, approvals, and tasks preserved in Band

Without Band these are isolated model calls. With Band they become an accountable incident-response team.

## Run it locally

```bash
pnpm install
pnpm --filter sentinel-relay-web dev
```

Then open `http://localhost:3000` and go to the War Room.

To run the full 18-step agent workflow through the app's collaboration routes:

```bash
./agents/run_demo.sh
```

This posts all agent messages, approval request, approval decision, and remediation tasks through `/api/collaboration` — no Band credentials required (dry-run mode by default).

## Run the offline agent verification

```bash
python3 agents/mock/run_mock_flow.py          # 18-step transcript + self-checks
python3 agents/mock/run_mock_flow.py --json   # full AgentMessage[] output
```

Zero network calls, zero model API calls, deterministic output.

## Repository structure

```
apps/web/          Next.js frontend and Band server adapter
agents/            Python agent workers (commander, forensics, threat_intel, code_review, risk_compliance, remediation)
packages/schemas/  Shared TypeScript + JSON Schema + Python models
data/incidents/    Synthetic evidence packets (INC-1042, INC-1043)
scripts/           Workflow runners and verification scripts
```

## Key commands

```bash
pnpm typecheck                      TypeScript check
pnpm build                          Production build
pnpm verify                         Full baseline verification
python3 agents/mock/run_mock_flow.py  Offline agent flow
./agents/run_demo.sh                  Live workflow via collaboration API
```

## Scenario

**Possible API Key Exposure After Friday Deploy** — A SaaS company detects suspicious API activity after a Friday deployment. Agents investigate whether a token was exposed, whether customer data was accessed, what actions require human approval, and what remediation should happen next.

## Agent team

| Agent | Role |
|---|---|
| Band Leader | Opens the room, assigns tasks, requests approval, generates report |
| Forensics | API and auth log analysis, evidence timeline |
| Threat Intel | Indicator confidence assessment |
| Code Review | Deployment diff and configuration review |
| Risk & Compliance | Policy review, challenge, and escalation |
| Remediation | Containment and fix planning |
| Human Security Lead | Approval gate — high-impact actions blocked without explicit sign-off |

## License

MIT
