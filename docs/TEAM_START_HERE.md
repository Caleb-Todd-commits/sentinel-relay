# Team start here

Sentinel Relay is a Band-powered multi-agent cybersecurity incident workspace. The deployed product combines a seeded, evidence-backed approval workflow with an open-ended security-problem field.

## Current product

- One public workspace at `/`.
- Three primary panels: Incident, Agents, and Decision/Result.
- Two verified scenarios: `INC-1042` and `INC-1043`.
- Six specialized AI roles and one human approval role.
- Live Band execution when available, labeled honestly in the interface.
- Verified replay when the live seeded workflow cannot complete.
- Open-ended incident analysis through `/api/custom-incident` and AI/ML API.

Legacy product routes redirect to the current workspace. Do not build new features against the retired multi-page interface.

## Non-negotiable behavior

1. Evidence and uncertainty stay visible.
2. Risk & Compliance may challenge other agents.
3. High-impact seeded actions require a human decision.
4. Remediation cannot appear before approval.
5. Provider secrets stay server-side.
6. Integration degradation must be labeled; it must not masquerade as live execution.
7. Custom incident descriptions must be fictional or sanitized.

## Read next

1. [README.md](../README.md)
2. [architecture.md](architecture.md)
3. [05_TERMINOLOGY.md](05_TERMINOLOGY.md)
4. [SECURITY.md](../SECURITY.md)
5. [57_EVIDENCE_DRIVEN_AI_ML_API_WORKFLOW.md](57_EVIDENCE_DRIVEN_AI_ML_API_WORKFLOW.md)

The older numbered step documents are retained as build history. See [docs/README.md](README.md) before relying on them.

## Verify a change

```bash
corepack pnpm verify
node scripts/dev/verify-streamlined-browser.mjs http://127.0.0.1:3000
```

For production-facing documentation or UI changes, regenerate screenshots with:

```bash
node scripts/submission/capture-demo.mjs https://sentinel-relay-alpha.vercel.app submission/screenshots
```
