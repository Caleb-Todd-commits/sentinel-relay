# Coding Agent Context — Sentinel Relay

Use this file when asking an AI coding assistant to work on the project.

---

## Project

Sentinel Relay is a Band-powered multi-agent cybersecurity incident command center.

---

## Primary Goal

Build a polished, stable, judge-readable hackathon project showing agents coordinating through Band during a high-stakes cybersecurity incident workflow.

---

## Main Scenario

Possible API Key Exposure After Friday Deploy.

---

## Required Workflow

1. Band Leader opens the case.
2. Forensics reviews logs and submits evidence.
3. Code Review checks recent diff/config.
4. Threat Intel assesses confidence.
5. Risk & Compliance challenges unsupported claims.
6. Band Leader requests human approval.
7. Human approves containment/remediation.
8. Remediation creates fix tasks.
9. Final report is generated.
10. Incident can be replayed as an audit trail.

---

## Build Rules

- Do not remove mock mode.
- Do not commit secrets.
- Do not add full auth unless explicitly requested.
- Do not add real destructive security actions.
- Keep one polished scenario.
- Use structured message types.
- Make Band collaboration visible.
- Preserve existing docs and project direction.

---

## Key Files to Read Before Coding

- `docs/01_PROJECT_VISION_LOCK.md`
- `docs/02_PROJECT_CHARTER.md`
- `docs/04_PRODUCT_BOUNDARIES_AND_NON_GOALS.md`
- `apps/web/src/lib/types.ts`
- `apps/web/src/lib/mockIncident.ts`
- `apps/web/src/lib/collaboration/CollaborationProvider.ts`

---

## Preferred Implementation Style

- Stable before clever.
- Clear TypeScript types.
- Small components.
- Safe fallbacks.
- Visible error states.
- No fragile live-only demo path.
- Thorough comments where integration is incomplete.
