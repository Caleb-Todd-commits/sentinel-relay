# 25 — Schema Validation and Versioning

## Current version

```txt
0.4.0
```

The version is intentionally tied to Step 4 because this is the first full shared schema baseline.

## Validation commands

From repo root:

```bash
pnpm schemas:validate
```

This runs the lightweight stdlib validator:

```bash
python scripts/schema/validate-sample-data.py
```

It checks:

- required top-level fields,
- known agents,
- known evidence references,
- message sequence order,
- ISO timestamps,
- confidence range,
- message type validity,
- required challenge message,
- required approval decision,
- required remediation task,
- final report audit references.

Additional checks:

```bash
pnpm schemas:contract
pnpm schemas:typecheck
```

## Versioning policy

During the hackathon, prefer additive changes.

### Patch version

Use for:

- adding optional fields,
- improving docs,
- adding examples,
- strengthening validation warnings.

### Minor version

Use for:

- adding a new message type,
- adding new required fields with all callers updated,
- adding major new report sections.

### Avoid major version changes

A major schema change during a one-week hackathon is usually a warning sign. It means the product direction is unstable.

## PR checklist for schema changes

Before merging a schema change:

- Update TypeScript types.
- Update Python models if agents use the field.
- Update JSON Schema if Band payloads use the field.
- Update sample demo JSON if needed.
- Run `pnpm schemas:validate`.
- Update docs if the field changes how agents communicate.

## Demo stability rule

The demo must remain runnable after every schema change.

If a schema change breaks the War Room or report page, do not merge it until the app is repaired.
