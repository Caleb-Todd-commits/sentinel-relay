# Sentinel Relay — Submission Copy

## Project title

Sentinel Relay

## Short description

Sentinel Relay is a Band-powered cybersecurity incident command center where specialized agents investigate evidence, challenge weak conclusions, request scoped human approval, coordinate remediation, and produce an audit-ready report.

## One-line hook

Security agents should not merely agree—they should verify, challenge, escalate, and leave an accountable decision trail.

## Long description

Security incidents are not single-prompt problems. Investigation, engineering review, threat assessment, compliance judgment, approval, containment, and reporting are separate responsibilities that must share context without collapsing into one opaque answer.

Sentinel Relay turns that process into a visible multi-agent workflow. A Band Leader opens a shared incident room and delegates work to Forensics, Code Review, Threat Intelligence, Risk & Compliance, and Remediation agents. Each specialist posts structured findings and evidence references into Band. Risk & Compliance can challenge unsupported claims, and high-impact containment remains blocked until a human Security Lead approves a precisely scoped action.

Band is the coordination layer—not a notification wrapper. It carries agent identity, task handoffs, shared room context, challenges, approval state, remediation updates, and the collaboration record used to generate the final report. The War Room makes that coordination legible in seconds through a message stream, evidence board, collaboration map, decision state, and audit replay.

The demo investigates a synthetic API-key exposure after a Friday deployment. Agents correlate API access, authentication events, code changes, incident policy, and customer-impact evidence. They distinguish proven unauthorized access from unsupported exfiltration claims, request approval for issuer-first containment, and preserve the decision boundary that customer notification remains held pending scope verification.

Sentinel Relay includes a production-deployed Next.js interface, typed shared schemas, Python agent workers, a server-side Band adapter, AI/ML API reasoning for the policy gate and Band Leader synthesis, deterministic replay for demo reliability, two generalization fixtures, and verification gates covering build, schema integrity, evidence grounding, dissent, approval controls, routing, and report traceability.

## Why Band is essential

- At least six specialized agents participate in one shared incident workflow.
- Findings and evidence references are posted as structured Band messages.
- Tasks are delegated and routed to named agents rather than broadcast blindly.
- Risk & Compliance challenges the current conclusion inside the shared room.
- Human approval changes the collaboration state and unlocks remediation.
- The final report is derived from messages, evidence, approvals, and tasks preserved by the workflow.

Without Band, these would be isolated model calls. With Band, they become an accountable incident-response team.

## Business value

- Faster triage without flattening separation of duties.
- Fewer missed handoffs between security, engineering, risk, and leadership.
- Better evidence quality through explicit challenge and peer review.
- Safer containment through scoped human approval.
- Audit-ready reporting built from the decision trail rather than reconstructed afterward.

## Technology tags

- Band Integrations
- Band Agentic Mesh
- AI/ML API
- Next.js
- TypeScript
- Python
- Vercel
- Cybersecurity
- Multi-agent systems
- Human in the loop
- Regulated & High-Stakes Workflows

## Submission links

- Application: https://sentinel-relay-alpha.vercel.app
- Repository: https://github.com/Caleb-Todd-commits/sentinel-relay
- Track: Regulated & High-Stakes Workflows

## Suggested category tags

Cybersecurity, Enterprise, Communication, Developer Tool, Productivity

## Closing line

Sentinel Relay shows what becomes possible when enterprise agents carry context forward, challenge one another, keep humans in control, and leave behind a report the company can trust.
