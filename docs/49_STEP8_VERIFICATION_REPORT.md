# Step 8 Verification Report

## Static Checks Added

```bash
pnpm band:verify
```

This confirms all Step 8 files exist and that the server adapter contains the expected Band route concepts.

## Env Checks Added

```bash
pnpm band:env
```

This prints whether required/optional env vars are present without exposing secret values.

## Live Smoke Test Added

```bash
pnpm band:smoke
```

This calls:

```txt
GET /api/v1/agent/me
GET /api/v1/me/profile  # only if BAND_HUMAN_API_KEY is set
```

It does not create a chat room.

## Local Checks Run During Package Build

The following checks were run while creating Step 8:

```bash
python scripts/band/verify-band-integration.py
python scripts/workflow/verify-mock-flow.py
python scripts/schema/validate-sample-data.py
bash scripts/schema/check-schema-contracts.sh
cd packages/schemas && tsc --noEmit
python -m py_compile agents/common/sentinel_agent_runtime.py agents/*/main.py
```

## Checks Still Required Locally

Because dependencies are not installed in the artifact environment, run these after unzipping:

```bash
pnpm install
pnpm typecheck
pnpm build
```

With real Band credentials:

```bash
pnpm band:env
pnpm band:smoke
```
