# 03 — Judge Pitch and Positioning

This document gives the exact story the team should tell judges.

---

## Short Pitch

Sentinel Relay is a Band-powered cybersecurity incident command center where specialized agents investigate suspicious activity, challenge weak conclusions, request human approval, create remediation tasks, and generate an audit-ready final report.

---

## Longer Pitch

Security incidents are high-stakes collaborative workflows. A single AI assistant can summarize a log file, but enterprise response requires multiple specialized roles: investigation, engineering review, risk judgment, approval, remediation, and reporting.

Sentinel Relay uses Band as the shared coordination layer where agents exchange structured evidence, assign tasks, challenge assumptions, escalate decisions, and preserve an audit trail. The result is a visible incident response process, not a one-shot answer.

---

## Why This Fits the Hackathon

The hackathon is about cross-framework multi-agent systems where agents collaborate through Band across planning, execution, review, decision-making, and task handoff.

Sentinel Relay demonstrates exactly that:

- Planning: Commander opens the case and assigns investigation tasks.
- Execution: Forensics, Code Review, and Threat Intel agents investigate.
- Review: Risk & Compliance challenges unsupported claims.
- Decision-making: Human approval controls high-impact actions.
- Handoff: Remediation receives verified findings and creates fix tasks.
- Audit: The final report is generated from structured collaboration events.

---

## Main Differentiator

Many projects will show agents producing output. Sentinel Relay shows agents coordinating a controlled process.

The strongest differentiator is the combination of:

- High-stakes cybersecurity scenario.
- Structured evidence handoffs.
- Agent disagreement/challenge.
- Human approval gate.
- Audit replay.
- Final report generated from the workflow.

---

## 3-Minute Demo Outline

### 0:00–0:20 — Problem

Enterprise incidents do not fail only because people lack information. They fail because context, approvals, evidence, and accountability are scattered across teams.

### 0:20–0:40 — Product Intro

Sentinel Relay creates a Band incident room where specialized agents coordinate the response.

### 0:40–1:15 — Start Incident

Show the sample case: Possible API Key Exposure After Friday Deploy.

### 1:15–1:55 — Agent Collaboration

Show the Commander assigning tasks, Forensics submitting evidence, Code Review finding possible token exposure, and Threat Intel adding confidence.

### 1:55–2:20 — Challenge and Approval

Show Risk & Compliance challenging the breach classification. Then show the Commander requesting human approval before containment.

### 2:20–2:45 — Remediation and Report

Show remediation tasks and the final audit-ready report.

### 2:45–3:00 — Why Band Matters

Without Band, these would be isolated agents. With Band, they become a coordinated incident response team with shared context, handoffs, review, approval, and auditability.

---

## Exact Closing Line

Sentinel Relay shows what becomes possible when enterprise agents are not trapped in separate tools. They can coordinate through Band, carry context forward, challenge each other, keep humans in control, and leave behind a report the company can trust.

---

## Questions Judges May Ask

### Why not just use one agent?

Because incident response requires separation of duties. One agent summarizing everything creates a single point of failure. Sentinel Relay gives agents different roles, different decision boundaries, and a shared evidence trail.

### How is Band central?

Band is the incident room and coordination layer. Agents use it to pass structured findings, assign tasks, challenge claims, request approval, and preserve the audit trail.

### Is this safe?

The demo does not execute destructive production actions. High-impact actions require human approval. The system recommends and documents, but does not blindly contain or notify.

### Why cybersecurity?

Cybersecurity is a high-stakes environment where review, traceability, escalation, and careful decision-making matter. That aligns strongly with the regulated/high-stakes track.

### What is the business value?

Faster triage, fewer missed handoffs, better evidence quality, safer approvals, cleaner reports, and stronger post-incident accountability.

---

## Words to Use

Use these phrases consistently:

- Incident command center
- Shared Band incident room
- Structured evidence handoff
- Agent-to-agent challenge
- Human approval gate
- Audit-ready report
- Traceable response workflow
- Separation of duties
- High-stakes workflow

---

## Words to Avoid

Avoid framing the project as:

- A chatbot
- A log summarizer
- A dashboard only
- An automation bot
- A fake SOC replacement
- A tool that handles everything automatically

The correct framing is a **coordinated decision-support workflow**.
