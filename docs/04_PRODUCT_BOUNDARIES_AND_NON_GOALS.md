# 04 — Product Boundaries and Non-Goals

This document prevents scope creep. If the team is unsure whether to build something, check here first.

---

## The Product Boundary

Sentinel Relay is a hackathon MVP for a multi-agent cybersecurity incident command workflow.

It is designed to prove:

- Multi-agent collaboration through Band.
- Structured evidence and task handoffs.
- Role-specific reasoning.
- Human approval in high-stakes workflows.
- Audit-ready reporting.

It is not designed to become a full production SOC platform during the hackathon.

---

## In Scope

### Product

- Landing page.
- Demo page.
- War Room page.
- Final report page.
- Replay mode.

### Workflow

- One sample incident.
- One case room.
- Six agent roles.
- Structured messages.
- Evidence board.
- Timeline.
- Agent challenge.
- Human approval.
- Remediation tasks.
- Final report.

### Data

- Safe fake logs.
- Safe fake diff.
- Safe fake policy.
- Safe fake support ticket.

### Technical

- Next.js frontend.
- TypeScript types.
- Python agent scaffolds.
- Band provider scaffold.
- Mock provider fallback.
- Environment variable examples only.

---

## Out of Scope

### Do Not Build First

- Full login system.
- Organization management.
- Real SIEM integration.
- Real GitHub write access.
- Real token revocation.
- Real customer notification sending.
- Real ticketing integration.
- Real compliance legal advice.
- Live malware analysis.
- Production incident database.
- Multi-scenario marketplace.
- Mobile app.

---

## Reasons These Are Out of Scope

### They increase failure risk

The hackathon is short. Complex integrations create more ways for the demo to fail.

### They distract from Band

If the app becomes about dashboards, auth, or integrations, judges may miss the Band coordination story.

### They do not improve the core proof

The core proof is agent collaboration through Band. The demo can prove this with sample data.

---

## Safe Demo Rules

- Use fake data only.
- Do not include real customer data.
- Do not include real API keys.
- Do not execute real containment actions.
- Do not claim legal/compliance authority.
- Keep human approval visible.
- Make uncertainty visible.

---

## Scope Creep Test

Before building a feature, ask:

1. Does this make Band's value more visible?
2. Does this improve the judge's understanding?
3. Does this strengthen the high-stakes workflow?
4. Can it be built reliably before submission?
5. Does it support the single perfect demo scenario?

If the answer is mostly no, do not build it yet.
