# Local Development Troubleshooting

## Baseline command path

From the repository root:

```bash
pnpm install
pnpm dev
```

Open:

```txt
http://localhost:3000
```

## If `pnpm` is not installed

Install it globally:

```bash
npm install -g pnpm
```

Then run:

```bash
pnpm install
pnpm dev
```

## If the app starts on another port

Next.js may start on another port if `3000` is taken. Watch the terminal output. It may say something like:

```txt
Local: http://localhost:3001
```

Use that URL instead.

## If dependencies are missing

Run from the repo root:

```bash
pnpm install
```

Then:

```bash
pnpm dev
```

## If TypeScript path aliases fail

Check:

```txt
apps/web/tsconfig.json
```

It should include:

```json
"baseUrl": ".",
"paths": {
  "@/*": ["./src/*"]
}
```

## If Tailwind styles do not load

Check these files:

```txt
apps/web/src/app/globals.css
apps/web/tailwind.config.ts
apps/web/postcss.config.mjs
```

Make sure `globals.css` is imported in:

```txt
apps/web/src/app/layout.tsx
```

## If `pnpm verify` fails because `node_modules` is missing

That is expected. Run:

```bash
pnpm install
```

Then:

```bash
pnpm verify
```

## If `next lint` fails unexpectedly

For a hackathon, do not spend hours fighting lint configuration unless it blocks build or typecheck. Run:

```bash
pnpm typecheck
pnpm build
```

If those pass, document the lint issue in the PR and continue. The final repo can tighten lint later.

## If the UI seems frozen

The demo is step-based, not automatic yet.

On `/war-room`, use:

- `Run next step`
- `Complete demo`
- `Replay`

## If the approval gate does not appear

The approval gate appears after the approval request message. Press `Run next step` until message 7 is visible.

## If the final report preview is locked

The report preview unlocks after all demo messages are visible. Press `Complete demo`.

## If someone wants to connect real Band immediately

Do not replace the UI. Use the provider architecture:

```txt
src/lib/collaboration/CollaborationProvider.ts
src/lib/collaboration/BandCollaborationProvider.ts
```

The goal is for real Band messages to satisfy the existing `AgentMessage` contract.
