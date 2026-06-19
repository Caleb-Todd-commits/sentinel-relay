# Sentinel Relay — current submission copy

## Short description

Sentinel Relay is a Band-powered cybersecurity incident workspace where six specialized agents investigate evidence, challenge weak conclusions, stop for scoped human approval, coordinate remediation, and preserve an audit-ready result.

## One-line hook

Security agents should not merely agree—they should verify, challenge, escalate, and leave an accountable decision trail.

## Long description

Security incidents are not single-prompt problems. Investigation, engineering review, threat assessment, compliance judgment, approval, containment, and reporting are separate responsibilities that must share context without collapsing into one opaque answer.

Sentinel Relay makes that process visible in one workspace. A Band Leader coordinates Forensics, Code Review, Threat Intel, Risk & Compliance, and Remediation. Seeded scenarios stream evidence-backed findings, expose integration mode, and stop before high-impact action until a human Security Lead approves a precise containment scope. The final Summary, Evidence, and Audit views remain traceable to the collaboration trail.

The production application includes two verified evidence scenarios and an open-ended field for fictional or sanitized security problems. On the open-ended path, only agents with a useful perspective respond; later agents receive prior findings so they can challenge or extend them. This route uses server-side AI/ML API orchestration and is not represented as a Band room.

Band is the coordination layer for live seeded execution—not a notification wrapper. Verified replay remains available and is labeled honestly when the live path cannot complete.

## Business value

- Faster triage without flattening separation of duties.
- Better evidence quality through explicit challenge and peer review.
- Safer containment through scoped human approval.
- Fewer lost handoffs between security, engineering, risk, and leadership.
- An audit-ready result built from the decision trail.

## Technology

Band, AI/ML API, Next.js, TypeScript, Python, Vercel, structured schemas, synthetic evidence, NDJSON streaming, and human-in-the-loop controls.

## Links

- Application: https://sentinel-relay-alpha.vercel.app
- Repository: https://github.com/Caleb-Todd-commits/sentinel-relay
