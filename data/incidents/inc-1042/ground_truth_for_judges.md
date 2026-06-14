# INC-1042 Judge Ground Truth

This file is not used by the workflow runner. It exists so the team can verify
whether the agents are producing useful conclusions from the evidence packet.

Expected high-signal findings:

- The suspicious spike starts at `2026-06-12T21:04:59Z`.
- The fallback token path was introduced by the Friday deploy.
- Two unexpected source IPs used the fallback token.
- Customer export endpoints returned `10227` records before rotation.
- The evidence supports suspected exposure, but not a final legal breach claim.
- Risk & Compliance should block customer notification until scope is verified.
- Human approval should allow credential rotation and temporary export throttling.
- AI/ML API should synthesize the cross-agent findings and explicitly cite evidence IDs.
