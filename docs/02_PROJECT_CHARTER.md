# 02 — Project Charter

This charter defines the product direction, team responsibilities, and decision-making principles for Sentinel Relay.

---

## Project Title

**Sentinel Relay**

---

## Project Category

**Primary:** Regulated & High-Stakes Workflows  
**Secondary:** Multi-Agent Software Development

---

## Mission

Build a working, judge-readable multi-agent incident command center that proves Band can coordinate specialized agents through a real enterprise security workflow.

---

## Product Vision

Sentinel Relay should feel like the first version of a real enterprise incident response platform.

It should not merely summarize a security alert. It should coordinate a process:

- Investigation
- Evidence collection
- Code/config review
- Risk evaluation
- Challenge and verification
- Human approval
- Remediation planning
- Audit-ready reporting

---

## Target User

### Primary User

Security lead, incident commander, or technical manager responsible for triaging and coordinating a possible cyber incident.

### Secondary Users

- Security analyst
- Engineering lead
- Compliance/risk reviewer
- Executive stakeholder
- Customer support manager

---

## User Problem

During a potential incident, teams need speed and discipline at the same time.

They need to know:

- What happened?
- Who verified it?
- What evidence exists?
- What remains uncertain?
- What actions are approved?
- What should be done next?
- What can be shown later as an audit trail?

Traditional tools scatter this information. Single-agent AI tools can summarize but often lack structured handoffs, clear review boundaries, and traceable decision paths.

---

## Product Goal

Create a Band-powered workflow where multiple agents coordinate as a visible incident response team.

---

## Key Product Outcomes

By the end of the hackathon, the project should demonstrate:

1. At least 3 agents collaborating through Band.
2. Structured context sharing.
3. Task handoffs.
4. Agent role specialization.
5. Agent challenge/disagreement.
6. Human approval for high-impact actions.
7. Audit trail generation.
8. A polished web dashboard.
9. A replayable demo.
10. A clear final report.

---

## Product Principles

### 1. Coordination Over Conversation

The agents should not simply chat. They should coordinate work.

### 2. Evidence Over Confidence Alone

A high-confidence claim still needs evidence. Claims should reference logs, diffs, policies, or timeline events.

### 3. Human Control Over Dangerous Actions

The system may recommend containment or communication, but human approval gates should control high-impact decisions.

### 4. One Excellent Scenario Over Many Weak Ones

The project should focus on one polished incident scenario.

### 5. Demo Reliability Over Technical Vanity

Live integrations are valuable, but the project should remain demoable through stable sample data and replay mode.

### 6. Visible Band Value

If a judge cannot tell how Band is being used, the UI and demo script need improvement.

---

## Main Use Case

A suspicious API token is used from an unusual region after a Friday deployment. The system launches a Band incident room. Agents investigate logs, inspect code changes, assess threat confidence, challenge unsupported conclusions, request approval, and generate a final report.

---

## MVP Scope

### In Scope

- Web dashboard
- Sample incident selector
- War Room UI
- Mock agent flow
- Band integration layer
- Python agent placeholders
- Structured messages
- Evidence board
- Timeline
- Human approval card
- Remediation checklist
- Final report page
- Replay mode

### Out of Scope for MVP

- Production security integrations
- Full authentication
- Billing
- Multi-tenant admin
- Real customer notifications
- Real production containment
- Real secret rotation
- Mobile client
- Multiple unrelated scenarios

---

## Team Roles

### Product / Cybersecurity Lead

Owns product direction, security scenario, judging strategy, demo script, and final pitch.

### Frontend Lead

Owns web UI, page structure, dashboard polish, responsive layout, and visual clarity.

### Band / Backend Lead

Owns Band room integration, message flow, provider abstraction, agent connection points, and backend routing.

### Agent Logic Lead

Owns prompts, agent behavior, structured outputs, evidence rules, and role boundaries.

### Demo / Data / Docs Lead

Owns sample incident files, README quality, architecture diagram, demo video flow, and submission package.

---

## Decision-Making Rule

When choosing between two build options, prefer the option that makes the final demo:

1. More reliable.
2. Easier to understand.
3. More visibly Band-native.
4. More enterprise-realistic.
5. More polished.

Avoid choices that add complexity without improving the judge experience.

---

## Final Submission Goal

The final submission should make a judge think:

> This is not just a hackathon chatbot. This is a believable new pattern for enterprise incident response using multi-agent coordination.
