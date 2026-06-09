# Step 8 Team Handoff

## What Changed

Step 8 connects the architecture to real Band concepts while keeping Mock Mode safe.

The project now has:

- Band REST client
- Band env validation
- Band room server route
- Band message server route
- Band approval server route
- Band health endpoint
- SSE local mirror stream
- Python remote agent SDK runner scaffolds
- Band env/smoke scripts

## Who Should Own What Next

### Band Lead

- Create/register remote agents in Band.
- Fill participant IDs and API keys.
- Run `pnpm band:smoke`.
- Test Band dry run and live mode.

### Agent Lead

- Start with `agents/common/sentinel_agent_runtime.py`.
- Replace generic LangGraph behavior with role-aware graph prompts/tools.
- Make each agent emit structured `AgentMessage` payloads.

### Frontend Lead

- Keep `/war-room` stable.
- Improve ProviderStatusPanel if live warnings need clearer display.
- Do not put secrets in client code.

### Demo Lead

- Keep Mock Mode as the backup path.
- Record at least one dry-run Band Mode demo.
- Record one Mock Mode demo in case live credentials fail.

## Next Step

Step 9 is the final report and audit replay hardening pass.

Focus on:

- turning provider audit events into a cleaner report section,
- making the Band/local mirror distinction explainable,
- improving export/download/copy behavior,
- ensuring the final report feels audit-ready.
