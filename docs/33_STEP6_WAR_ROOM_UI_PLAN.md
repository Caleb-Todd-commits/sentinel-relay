# Step 6 — War Room UI Plan and Completion

Step 5 made the War Room functional and workflow-driven. Step 6 made it visually stronger, more judge-readable, and easier to understand quickly.

## Main objective

Make the War Room feel like an enterprise incident command center, not just a web page with cards.

## Completed improvements

1. **Risk challenge is visually dominant**
   - Added a critical moment spotlight.
   - Upgraded challenge message styling.
   - Kept challenge and approval state visible in workflow controls and state panels.

2. **Human approval gate is impossible to miss**
   - Added stronger pending/approved states.
   - Clearly separated approved scope from explicitly not-approved scope.
   - Kept remediation visually blocked until approval is recorded.

3. **Audit replay trail exists**
   - Added a compact audit replay panel based on visible structured messages.
   - Included message sequence, sender, type, timestamp, and trace ID.

4. **Layout hierarchy improved**
   - Added a command bar.
   - Added judge briefing panel.
   - Added collaboration map.
   - Reorganized the War Room into state/stream/artifact zones.

5. **Responsive polish improved**
   - Main layout now uses wider desktop space but remains usable at narrower widths.
   - Cards use wrap-friendly controls and sections.

6. **Report path remains visible**
   - Report CTA remains in the right artifact rail and top navigation.

7. **Mock mode is framed properly**
   - The UI uses “Mock Mode · Band contract replay,” keeping the demo honest while avoiding the word “fake.”

## What was not done in Step 6

- No real Band connection yet.
- No auth.
- No random incident generation.
- No database.
- No unrelated dashboard surfaces.

## Definition of done

Step 6 is complete because a judge can understand the core product in less than 30 seconds by looking at the War Room alone.

## Next step

Step 7 should add the Collaboration Provider Layer so the UI can receive events from either mock replay or real Band room messages without changing page components.
