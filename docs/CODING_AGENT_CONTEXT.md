# Coding agent context

## Objective

Maintain a clear, public multi-agent incident workspace that demonstrates evidence grounding, specialist disagreement, human control, and honest integration status.

## Current workflow

1. A visitor selects `INC-1042` or `INC-1043`, or enters a sanitized fictional scenario.
2. Seeded investigations stream through `/api/agent_run` and stop at human approval.
3. Open-ended analysis streams through `/api/custom-incident` and returns only relevant specialist perspectives.
4. Seeded remediation and reporting continue only after approval.
5. Legacy product routes redirect to `/`.

## Build rules

- Preserve the three primary panel markers.
- Do not introduce popup-heavy UI.
- Keep secrets server-side.
- Preserve verified replay and evidence fixtures.
- Never imply the open-ended AI/ML API route creates a Band room.
- Never process or encourage real sensitive incident data.
- Update README, current docs, and screenshots when visible behavior changes.

## Read before editing

- `README.md`
- `docs/architecture.md`
- `docs/05_TERMINOLOGY.md`
- `SECURITY.md`
- `apps/web/src/components/LiveInvestigationWorkspace.tsx`
- `apps/web/src/app/api/agent_run/route.ts`
- `apps/web/src/app/api/custom-incident/route.ts`

## Verification

Run `corepack pnpm verify`. For UI changes, also run the browser verifier and regenerate public screenshots.
