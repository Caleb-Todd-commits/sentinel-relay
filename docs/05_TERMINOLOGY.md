# 05 — Terminology

This file standardizes language across docs, UI, agents, and demo scripts.

---

## Sentinel Relay

The project name. A multi-agent cybersecurity incident command center powered by Band.

---

## Incident

A suspicious security event that requires investigation, review, decision-making, and documentation.

Example:

- Possible API key exposure after a deployment.

---

## Case

The structured record of one incident inside Sentinel Relay.

A case includes:

- Title
- Severity
- Status
- Agents
- Messages
- Findings
- Evidence
- Timeline
- Approvals
- Remediation tasks
- Final report

---

## Band Incident Room

The shared collaboration space where agents coordinate around a case.

This is where agents should pass structured context, assign tasks, challenge findings, and preserve the audit trail.

---

## Agent

A specialized AI worker with a defined role, allowed actions, and output format.

Agents in this project:

- Band Leader
- Forensics Agent
- Threat Intel Agent
- Code Review Agent
- Risk & Compliance Agent
- Remediation Agent

---

## Finding

A claim made by an agent based on evidence.

Example:

- The API token was used from an unusual region after deployment.

A finding should include:

- Claim
- Evidence references
- Confidence
- Agent source
- Recommended next step

---

## Evidence Reference

A pointer to the source supporting a finding.

Examples:

- File name
- Log line
- Timestamp
- Diff section
- Policy section

---

## Challenge

A structured objection or request for more evidence.

Example:

- Risk & Compliance challenges whether suspicious access is enough to declare confirmed customer exposure.

Challenges are good. They prove the system is reviewing claims rather than blindly agreeing.

---

## Confidence Assessment

An agent's probability-like evaluation of how strong a claim is.

Confidence should not replace evidence. It should explain uncertainty.

---

## Human Approval Gate

A required human decision before high-impact actions are marked approved.

Examples:

- Approve token revocation.
- Approve customer notification draft.
- Approve closure.

---

## Remediation Task

A concrete fix or prevention step.

Examples:

- Revoke exposed token.
- Rotate API secrets.
- Remove unsafe config.
- Add secret scanning test.
- Review deploy process.

---

## Audit Trail

The structured history of messages, findings, challenges, approvals, and tasks that explains what happened and why decisions were made.

---

## Final Report

The enterprise-readable report generated from the case workflow.

It should include:

- Executive summary
- Timeline
- Evidence
- Root cause
- Risk assessment
- Approval record
- Remediation plan
- Remaining uncertainty

---

## Replay Mode

A demo feature that replays the incident timeline so judges can see how agents coordinated.

---

## Mock Mode

A local stable simulation of the workflow using fake data.

Mock Mode exists so the demo remains reliable.

---

## Band Mode

The real connected mode where agent communication flows through Band.

---

## Phrase Standardization

Use:

- Band incident room
- Human approval gate
- Structured evidence handoff
- Agent-to-agent challenge
- Audit-ready incident report

Avoid:

- Chatbot
- Autopilot security
- Fully automated incident response
- Replacing the security team
