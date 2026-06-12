# 01 — Project Vision Lock

This document is the source of truth for what Sentinel Relay is, what it is not, why it should win, and how the team should make decisions while building it.

This file completes Step 1 from `docs/01_BIGGEST_10_FIRST.md`: **Lock the Project Vision**.

---

## 1. Product Name

**Sentinel Relay**

### Name Meaning

- **Sentinel**: a watcher, guard, or security monitor.
- **Relay**: a handoff system where information moves from one role to the next.

The name communicates the core product clearly: a coordinated security-response system where specialized agents pass context, verify evidence, escalate decisions, and produce a traceable outcome.

---

## 2. One-Sentence Description

**Sentinel Relay is a Band-powered multi-agent cybersecurity incident command center where specialized agents investigate suspicious activity, challenge weak conclusions, request human approval, create remediation tasks, and generate an audit-ready incident report.**

---

## 3. 30-Second Explanation

Enterprise security incidents are not solved by one person or one AI assistant. They require investigation, engineering review, risk judgment, approvals, and documentation.

Sentinel Relay creates a shared Band incident room where multiple specialized agents work together like an incident response team. A Band Leader coordinates the case, a forensics agent reviews logs, a code review agent checks recent changes, a threat intel agent assesses indicators, a risk and compliance agent challenges conclusions, and a remediation agent prepares the fix plan.

Band is the coordination layer. Agents pass structured evidence, assign tasks, challenge each other, request human approval, and produce a final audit trail.

---

## 4. 10-Second Demo Pitch

**Sentinel Relay turns a suspicious security alert into a coordinated, audit-ready incident response by letting specialized agents collaborate through Band instead of acting alone.**

---

## 5. Hackathon Track Positioning

### Primary Track

**Track 3: Regulated & High-Stakes Workflows**

### Reason

Cybersecurity incident response is high-stakes because wrong conclusions can create legal, operational, financial, and customer-trust consequences. A system in this space needs review, traceability, escalation, and human approval.

### Secondary Track Influence

**Track 2: Multi-Agent Software Development**

Sentinel Relay includes a remediation/code-review component. The Code Review Agent inspects a recent diff or configuration change. The Remediation Agent prepares a technical fix plan or mock PR summary.

This gives us the strength of Track 3 while still showing technical depth from Track 2.

---

## 6. Core Thesis

Most agent systems fail to model how enterprise work actually happens.

Enterprise work is not:

```txt
Prompt → Answer
```

Enterprise work is closer to:

```txt
Signal detected
→ Case opened
→ Roles assigned
→ Evidence collected
→ Hypotheses formed
→ Claims challenged
→ Risk assessed
→ Human approval requested
→ Actions taken
→ Report generated
→ Audit trail preserved
```

Sentinel Relay exists to show that Band enables this second pattern.

---

## 7. The Problem

When a company receives a suspicious security alert, the work usually spreads across multiple people and systems:

- Security reviews logs.
- Engineering checks recent code or configuration changes.
- Risk/compliance evaluates severity and obligations.
- Leadership may need a clear summary.
- A human must approve high-impact actions.
- Someone must write a final report.

The pain is not just the investigation itself. The pain is coordination:

- Evidence gets scattered.
- Context gets lost between teams.
- People act before the risk level is clear.
- Reports are written after the fact from incomplete notes.
- Audit trails are weak.
- The team wastes time deciding what has already been verified.

---

## 8. The Solution

Sentinel Relay creates a structured incident room where specialized agents collaborate through Band.

Each agent has a defined role, defined output format, and defined decision limits. The agents do not merely produce independent summaries. They coordinate.

They can:

- Open a case.
- Join a shared incident room.
- Receive assigned tasks.
- Submit findings.
- Attach evidence references.
- Challenge another agent's conclusion.
- Request additional verification.
- Escalate to a human.
- Generate remediation tasks.
- Build a final report from the full event trail.

The final result is not just an answer. It is a traceable response process.

---

## 9. Why Band Is Central

Band must be the collaboration layer, not a cosmetic integration.

In Sentinel Relay, Band is used for:

1. Creating the incident room.
2. Registering specialized agents.
3. Passing structured context between agents.
4. Assigning tasks.
5. Updating case state.
6. Challenging weak findings.
7. Requesting human approval.
8. Capturing final decisions.
9. Preserving an audit trail.
10. Enabling replay of the incident workflow.

A judge should be able to remove Band from the architecture and immediately see the workflow break.

If Band is only used to send the final report, we failed.

---

## 10. Product Promise

Sentinel Relay promises to help teams answer four questions during a security incident:

1. **What happened?**
2. **What evidence supports that conclusion?**
3. **What actions are approved?**
4. **What can we prove afterward?**

---

## 11. The Demo Scenario

### Scenario Name

**Possible API Key Exposure After Friday Deploy**

### Scenario Summary

A SaaS company receives suspicious API usage alerts after a Friday deployment. The system needs to determine whether an API token was exposed, whether the token was used, whether customer data may have been accessed, what actions should be approved, and what report should be created.

### Demo Inputs

Located in `packages/sample-data/`:

- `api_gateway_logs.json`
- `auth_logs.csv`
- `recent_diff.patch`
- `incident_policy.md`
- `customer_ticket.txt`

### Intended Demo Discovery

The agents should discover or infer the following:

- Suspicious API activity occurred after deployment.
- A token was used from an unusual region.
- A recent diff appears to include unsafe token exposure or unsafe config handling.
- The evidence initially suggests suspicious access but does not immediately prove customer exposure.
- Risk/compliance requires approval before containment or external communication.
- The approved remediation path includes token revocation, secret rotation, config cleanup, secret-scanning checks, and a final report.

---

## 12. Required Agent Cast

The product should demonstrate at least 3 agents, but the target design uses 6.

### 1. Band Leader

**Purpose:** Own the case flow.

Primary responsibilities:

- Open the case.
- Create or join the Band incident room.
- Assign tasks to specialized agents.
- Track current incident phase.
- Request human approval when required.
- Determine when the report can be produced.

Cannot do:

- Declare customer exposure without supporting evidence.
- Bypass human approval for high-impact actions.
- Invent evidence not present in the case file.

### 2. Forensics Agent

**Purpose:** Determine what happened from logs and raw evidence.

Primary responsibilities:

- Review API gateway logs.
- Review auth logs.
- Build a timeline.
- Identify suspicious activity.
- Submit evidence-backed findings.

Cannot do:

- Decide legal/compliance obligations.
- Approve containment.
- Claim confirmed breach without enough evidence.

### 3. Threat Intel Agent

**Purpose:** Assess suspicious indicators and confidence.

Primary responsibilities:

- Evaluate suspicious IPs, regions, tokens, timestamps, and behavior.
- Assign confidence levels.
- Support or weaken the active hypothesis.
- Recommend additional checks.

Cannot do:

- Treat weak indicators as proof.
- Overstate threat severity.
- Approve communications or containment.

### 4. Code Review Agent

**Purpose:** Check whether recent code/config changes caused or contributed to the incident.

Primary responsibilities:

- Review `recent_diff.patch`.
- Identify exposed secrets or unsafe configuration.
- Link code/config evidence to runtime behavior.
- Produce remediation tasks.

Cannot do:

- Modify production directly in the demo.
- Claim logs prove code exposure unless connected by evidence.
- Approve merge or deployment alone.

### 5. Risk & Compliance Agent

**Purpose:** Challenge conclusions and apply policy.

Primary responsibilities:

- Read `incident_policy.md`.
- Evaluate severity.
- Identify required approvals.
- Challenge unsupported findings.
- Decide whether evidence supports escalation.

Cannot do:

- Ignore policy.
- Approve technical fixes alone.
- Generate customer notification without approved evidence state.

### 6. Remediation Agent

**Purpose:** Convert verified findings into safe technical actions.

Primary responsibilities:

- Create a remediation checklist.
- Draft a mock PR summary.
- Recommend tests.
- Suggest secret rotation and prevention controls.

Cannot do:

- Claim remediation is complete without approval.
- Take destructive action automatically.
- Skip validation steps.

---

## 13. Required Human Role

### Human Incident Lead

A human reviewer must approve high-impact actions.

Actions requiring approval:

- Marking containment as approved.
- Declaring confirmed customer exposure.
- Drafting external customer communication as final.
- Marking the incident ready for closure.

The human role can be represented through the frontend UI at first. It does not need full authentication in the hackathon MVP.

---

## 14. Required Collaboration Moments

The final demo must include these moments:

### Moment 1 — Band Leader Opens Case

The Incident Band Leader creates the case and assigns investigation tasks.

### Moment 2 — Forensics Finds Suspicious Activity

Forensics submits evidence-backed findings from logs.

### Moment 3 — Code Review Finds Technical Cause

Code Review identifies unsafe token/config exposure in the recent diff.

### Moment 4 — Risk Agent Challenges a Claim

Risk & Compliance refuses to confirm customer exposure until stronger evidence exists.

### Moment 5 — Threat Intel Adjusts Confidence

Threat Intel adds confidence scoring and points out uncertainty.

### Moment 6 — Human Approval Gate

Band Leader requests approval before containment/remediation actions are marked approved.

### Moment 7 — Remediation Plan

Remediation Agent creates concrete technical tasks.

### Moment 8 — Audit Report

The final report is generated from structured messages and timeline events.

### Moment 9 — Replay

The system can replay the incident sequence so the judge sees collaboration clearly.

---

## 15. Structured Message Types

Sentinel Relay should use structured messages. Avoid vague agent paragraphs.

Core message types:

- `CaseOpened`
- `TaskAssignment`
- `Finding`
- `EvidenceReference`
- `TimelineEvent`
- `Challenge`
- `ConfidenceAssessment`
- `RiskAssessment`
- `ApprovalRequest`
- `ApprovalDecision`
- `RemediationTask`
- `ReportSection`
- `CaseStatusUpdate`

Each message should answer:

- Who sent it?
- What type is it?
- What claim does it make?
- What evidence supports it?
- What confidence level applies?
- What should happen next?

---

## 16. The Winning Differentiator

The differentiator is not simply cybersecurity.

The differentiator is **structured, visible, traceable multi-agent coordination in a high-stakes workflow**.

The system should feel less like a chatbot and more like an incident command center.

---

## 17. What We Are Building First

The first version should be a polished vertical slice:

- Landing page.
- Demo start page.
- War Room page.
- Agent roster.
- Message stream.
- Evidence board.
- Timeline.
- Human approval card.
- Remediation task list.
- Final report page.
- Replay button.
- Mock collaboration provider.
- Band provider scaffold.

This gives the team a stable demo path even before every live integration is complete.

---

## 18. What We Are Not Building First

Do not build these in the first baseline:

- Real SOC/SIEM integrations.
- Full user authentication.
- Multi-tenant enterprise admin dashboard.
- Real customer notifications.
- Real destructive containment actions.
- Production secret rotation.
- Complex database architecture.
- Mobile app.
- Browser extension.
- Five unrelated demo scenarios.

Those may be future extensions, but they are not needed to win the hackathon.

---

## 19. Non-Negotiable Product Rules

1. **Band must be central.**
2. **Every agent must have a defined role.**
3. **Important claims need evidence.**
4. **Weak evidence should be challenged.**
5. **High-impact actions require human approval.**
6. **The final report should come from the workflow, not be pasted on at the end.**
7. **The demo must work even if live model calls are unreliable.**
8. **No real secrets or sensitive data are committed.**
9. **One excellent scenario beats many incomplete scenarios.**
10. **The UI must make coordination visible.**

---

## 20. Product Tone

The product should feel:

- Serious.
- Enterprise-ready.
- Clear.
- Controlled.
- Trustworthy.
- Fast to understand.
- Built around evidence.

Avoid making it feel:

- Gimmicky.
- Like a chatbot wrapper.
- Like a fake terminal demo.
- Like a generic task manager.
- Like a compliance dashboard with no real agent collaboration.

---

## 21. UI North Star

The main screen should feel like a **security incident war room**.

Required visual sections:

- Case title and severity.
- Current phase.
- Agent roster.
- Band message stream.
- Evidence board.
- Timeline.
- Open decisions.
- Human approval gate.
- Remediation checklist.
- Report preview.

A judge should know what happened without reading the code.

---

## 22. MVP Definition

The MVP is complete when a judge can do this:

1. Open the hosted app.
2. Click into the sample incident.
3. Watch agents collaborate.
4. See a disagreement/challenge.
5. Approve a containment decision.
6. See remediation tasks appear.
7. Open the final report.
8. Replay the audit trail.
9. Understand why Band mattered.

---

## 23. Demo Success Criteria

A successful demo should make these statements obviously true:

- This is a real multi-agent workflow.
- Agents have specialized responsibilities.
- Agents coordinate through Band.
- The system captures evidence and decisions.
- A human remains in control of high-impact actions.
- The final report is traceable.
- The workflow would be hard to reproduce with one isolated chatbot.

---

## 24. Judge-Facing Story

The judge-facing story should be:

> Security incidents are high-stakes collaborative workflows. Sentinel Relay shows how Band turns isolated agents into a coordinated incident-response team. Agents investigate logs, review code, assess risk, challenge unsupported claims, request human approval, and create a final audit-ready report from the shared Band workflow.

---

## 25. Product Risks

### Risk 1 — It looks like a generic chatbot

Mitigation:

- Use structured cards.
- Show clear agent roles.
- Show the Band room/message flow.
- Include agent disagreement.

### Risk 2 — Band feels bolted on

Mitigation:

- Make the message stream central.
- Route handoffs through the collaboration provider.
- Generate audit report from collaboration events.

### Risk 3 — The scope gets too large

Mitigation:

- Build one polished scenario.
- Avoid live enterprise integrations.
- Use sample data.

### Risk 4 — The demo breaks

Mitigation:

- Keep mock mode.
- Add replay mode.
- Avoid relying on randomness.

### Risk 5 — The cybersecurity story is confusing

Mitigation:

- Use a simple API key exposure scenario.
- Avoid advanced jargon in the demo.
- Show evidence visually.

---

## 26. Future Expansion Ideas

Only after MVP:

- GitHub PR integration.
- Slack/Jira handoff.
- Multiple incident templates.
- Dynamic agent recruitment.
- Live Band dashboard overlay.
- Open-source model agent through Featherless.
- AI/ML API provider comparison.
- Compliance-specific templates for SOC 2, HIPAA, or PCI-style workflows.

---

## 27. Final Vision Lock Statement

We are building Sentinel Relay as a polished, evidence-driven, Band-native cybersecurity incident command center.

The goal is not to show that agents can talk. The goal is to show that agents can coordinate serious enterprise work: investigation, review, challenge, approval, remediation, and reporting.

Every major build decision should support that goal.
