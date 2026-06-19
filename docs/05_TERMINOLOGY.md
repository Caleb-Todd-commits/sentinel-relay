# Terminology

Use these terms in current UI, documentation, and repository metadata.

## Product terms

- **Sentinel Relay** — the multi-agent cybersecurity incident workspace.
- **Workspace** — the single deployed interface containing Incident, Agents, Decision/Result, and the open-ended scenario section.
- **Seeded scenario** — an evidence-backed scenario with a known transcript and approval boundary (`INC-1042` or `INC-1043`).
- **Open-ended scenario** — a fictional or sanitized incident description analyzed by the specialist roles through AI/ML API.
- **Band room** — the shared Band collaboration space used by the live seeded path.
- **Verified replay** — the evidence-backed fallback used when live seeded execution cannot complete.
- **Finding** — an evidence-grounded specialist claim with confidence and decision impact.
- **Challenge** — a structured objection that separates proven facts from assumptions.
- **Human approval gate** — the explicit decision required before seeded remediation and reporting continue.
- **Scoped containment** — only the actions listed in the approval request; notification and closure remain separate decisions.
- **Audit trail** — the ordered messages, evidence references, challenge, approval, and remediation record.

## Participant names

- Band Leader
- Forensics
- Code Review
- Threat Intel
- Risk & Compliance
- Remediation
- Human Security Lead / Security Lead

Say **six specialized agents plus a human Security Lead**, not “seven specialist agents.”

## Execution labels

- `Live · Band + AI` — live Band-backed seeded execution completed.
- `Live · agent runtime` — server-side agents ran while an integration degraded.
- `Verified replay` — the bundled evidence transcript supplied the seeded result.

## Avoid in current product claims

- “War Room” as a current page name
- “fully automated response” or “autopilot security”
- “confirmed breach” when evidence establishes access but not downstream misuse
- “live Band” for the open-ended AI/ML API route
- “seven specialist agents”
- “mock” when the accurate term is verified replay

Historical build documents may retain retired terms when clearly labeled as history.
