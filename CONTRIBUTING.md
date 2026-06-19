# Contributing to Sentinel Relay

## Start here

Read [README.md](README.md), [docs/TEAM_START_HERE.md](docs/TEAM_START_HERE.md), [docs/architecture.md](docs/architecture.md), and [SECURITY.md](SECURITY.md).

## Local setup

```bash
corepack pnpm install
corepack pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

## Branches and commits

Use a focused branch unless the repository owner explicitly coordinates a direct `main` update.

```text
feature/<task>
fix/<task>
docs/<task>
agent/<task>
band/<task>
chore/<task>
```

Use concise conventional commit messages, for example `feat: add incident clarification flow` or `docs: refresh public product guide`.

## Pull requests

Describe what changed, why it matters, how it was verified, and what could regress. Include current screenshots for visible UI changes.

## Definition of done

- No secrets or real incident data are committed.
- `corepack pnpm verify` passes.
- The seeded approval boundary still blocks remediation.
- Verified replay still works when integrations are unavailable.
- The custom-scenario path handles provider failure clearly.
- Public statements and screenshots match the deployed product.
- The production browser smoke test passes for UI changes.

## Historical documentation

Numbered files under `docs/` record the project’s build sequence. Do not treat old route names or intermediate architecture in those files as the current contract; update the authoritative documents listed in [docs/README.md](docs/README.md).
