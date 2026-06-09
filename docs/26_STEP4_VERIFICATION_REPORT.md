# 26 — Step 4 Verification Report

## Step completed

Step 4: Define the shared data schemas.

## Files added

Schema package:

```txt
packages/schemas/package.json
packages/schemas/tsconfig.json
packages/schemas/README.md
packages/schemas/src/*.ts
packages/schemas/json-schema/*.schema.json
packages/schemas/python/sentinel_relay_schemas/*.py
packages/schemas/examples/demo_incident.json
packages/schemas/contracts/*.md
```

Sample data:

```txt
packages/sample-data/demo_incident.json
```

Scripts:

```txt
scripts/schema/validate-sample-data.py
scripts/schema/check-schema-contracts.sh
```

Docs:

```txt
docs/21_SHARED_SCHEMA_SYSTEM.md
docs/22_BAND_MESSAGE_SCHEMA.md
docs/23_AGENT_INPUT_OUTPUT_CONTRACTS.md
docs/24_SAMPLE_DATA_AND_REPORT_SCHEMA.md
docs/25_SCHEMA_VALIDATION_AND_VERSIONING.md
docs/26_STEP4_VERIFICATION_REPORT.md
docs/27_STEP4_TEAM_HANDOFF.md
```

## Files updated

```txt
apps/web/src/lib/types.ts
apps/web/src/lib/demo/sentinelRelayDemo.ts
apps/web/package.json
apps/web/next.config.ts
pnpm-workspace.yaml
package.json
README.md
docs/TEAM_START_HERE.md
docs/01_BIGGEST_10_FIRST.md
docs/06_DECISION_LOG.md
```

## Verification performed here

The following checks were run successfully in this build environment:

```bash
python scripts/schema/validate-sample-data.py
bash scripts/schema/check-schema-contracts.sh
cd packages/schemas && tsc --noEmit
python -m py_compile packages/schemas/python/sentinel_relay_schemas/models.py
python -m py_compile scripts/schema/validate-sample-data.py
```

The sample incident passed lightweight schema validation, the schema contract files are present, the TypeScript schema package type-checked, and the Python model files compiled.

Because this build environment does not include the repository's installed Next.js dependencies, full `pnpm install`, web app typecheck, and Next.js production build still need to be run locally by the team.

## Expected local checks

Run:

```bash
pnpm install
pnpm schemas:validate
pnpm schemas:typecheck
pnpm typecheck
pnpm build
```

If there is a dependency issue, run:

```bash
pnpm install --force
```

Then retry the checks.
