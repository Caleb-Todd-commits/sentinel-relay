# Step 3 — Next.js Baseline Running

## Status

**Completed baseline.**

The web app has been upgraded from rough placeholders into a stable, product-shaped Next.js baseline. It is still intentionally mock-first, but the structure now matches the final Sentinel Relay experience closely enough that the team can build on it without guessing.

## Goal of Step 3

The goal was not to build the full application. The goal was to make the frontend reliable enough that every teammate can run it, understand it, and contribute without breaking the demo foundation.

Step 3 needed to achieve five things:

1. Make the app route structure clear.
2. Make the UI look like a real product.
3. Make the mocked incident data match the final product story.
4. Make the TypeScript data contract strong enough for later Band integration.
5. Add teammate-facing documentation and verification scripts.

## Completed Web Routes

The app now includes these routes:

| Route | Purpose | Current status |
|---|---|---|
| `/` | Product landing page and judge-facing value proposition | Complete baseline |
| `/demo` | Explains the sample incident and launches the demo | Complete baseline |
| `/war-room` | Main incident command dashboard | Complete baseline |
| `/report` | Final audit-ready incident report | Complete baseline |
| `/status` | Local readiness/status check page | Complete baseline |

## Main UI Surfaces

The War Room now has the essential baseline surfaces:

- Incident header
- Demo progress tracker
- Agent roster
- Band-style collaboration stream
- Structured message cards
- Evidence board
- Incident timeline
- Human approval gate
- Remediation task list
- Final report preview
- Replay controls
- Complete-demo control

This gives the team a visible product shell before real Band messages are connected.

## Local Run Commands

From the repository root:

```bash
pnpm install
pnpm dev
```

Open:

```txt
http://localhost:3000
```

Useful commands:

```bash
pnpm typecheck
pnpm build
pnpm verify
```

`pnpm verify` runs the baseline verification script. It expects dependencies to already be installed.

## Expected Local Behavior

When the app is running:

1. `/` should load the Sentinel Relay landing page.
2. `/demo` should explain the sample incident.
3. `/war-room` should show 3 initial messages.
4. `Run next step` should reveal the next structured agent message.
5. `Replay` should reset the stream to the first message.
6. `Complete demo` should reveal the whole incident flow.
7. The approval gate should appear after the approval request step.
8. The remediation list should appear after the approval decision.
9. The report preview should unlock after the final message.
10. `/report` should show the final audit report.

## Files Added or Upgraded

### App configuration

- `apps/web/package.json`
- `apps/web/next.config.ts`
- `apps/web/tailwind.config.ts`
- `apps/web/tsconfig.json`
- `apps/web/postcss.config.mjs`
- `apps/web/.eslintrc.json`
- `apps/web/README.md`

### App routes

- `apps/web/src/app/page.tsx`
- `apps/web/src/app/demo/page.tsx`
- `apps/web/src/app/war-room/page.tsx`
- `apps/web/src/app/report/page.tsx`
- `apps/web/src/app/status/page.tsx`
- `apps/web/src/app/layout.tsx`
- `apps/web/src/app/globals.css`

### Components

- `apps/web/src/components/SiteHeader.tsx`
- `apps/web/src/components/AgentRoster.tsx`
- `apps/web/src/components/MessageStream.tsx`
- `apps/web/src/components/EvidenceBoard.tsx`
- `apps/web/src/components/TimelinePanel.tsx`
- `apps/web/src/components/ApprovalGate.tsx`
- `apps/web/src/components/ReportPreview.tsx`
- `apps/web/src/components/ui/Badge.tsx`
- `apps/web/src/components/ui/MetricCard.tsx`
- `apps/web/src/components/war-room/IncidentHeader.tsx`
- `apps/web/src/components/war-room/RemediationList.tsx`

### Data and contracts

- `apps/web/src/lib/types.ts`
- `apps/web/src/lib/demo/sentinelRelayDemo.ts`
- `apps/web/src/lib/mockIncident.ts`
- `apps/web/src/lib/utils/format.ts`
- `apps/web/src/lib/collaboration/CollaborationProvider.ts`
- `apps/web/src/lib/collaboration/MockCollaborationProvider.ts`
- `apps/web/src/lib/collaboration/BandCollaborationProvider.ts`
- `apps/web/src/lib/collaboration/getCollaborationProvider.ts`

### Developer experience

- `.vscode/extensions.json`
- `.vscode/settings.json`
- `scripts/dev/verify-web-baseline.sh`

## Current Architecture

The frontend is still mock-first, but it is no longer throwaway.

```txt
UI pages
  -> React components
    -> TypeScript demo data
      -> Shared message/evidence/approval/report types
        -> CollaborationProvider contract
          -> Mock provider now
          -> Band provider later
```

The important architectural decision is that the UI is built around structured messages, not arbitrary paragraphs. That means real Band messages can later satisfy the same shape.

## Stability Rules Added in Step 3

- The app must run without Band credentials.
- The demo must not depend on live external services yet.
- Mock Mode is not a hack; it is the reliability layer and frontend contract.
- Real Band integration should not require rewriting UI components.
- TypeScript types are the source of truth for frontend data shape.
- The War Room must always remain demoable.

## What Step 3 Does Not Do Yet

This step does **not** connect real Band.

It also does not add:

- Database persistence
- Real auth
- Real agent execution
- Live API calls
- File upload
- Real SIEM/security integrations
- Production incident tooling

Those are intentionally later. The project is currently optimized for a stable hackathon baseline and judge-readable demo shell.

## Definition of Done for Step 3

Step 3 is considered done when:

- The app has working route files for the required demo pages.
- The app has a clear landing page, demo page, War Room, report page, and status page.
- The War Room can replay a realistic incident flow from structured mock data.
- The message stream visibly shows agent coordination and disagreement.
- The approval gate visibly shows human-in-loop control.
- The report page has a credible audit-ready shape.
- The repo includes clear instructions for teammates to run the web app.

All of those are now represented in the baseline package.
