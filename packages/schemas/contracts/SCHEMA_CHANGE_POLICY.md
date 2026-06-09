# Schema Change Policy

During the hackathon, schema changes are allowed, but careless changes can break the whole project. Follow this policy.

## Safe changes

- Add optional fields.
- Add new message types if the UI can ignore unknown types.
- Add documentation examples.
- Add validation warnings.

## Risky changes

- Renaming fields.
- Changing enum values.
- Changing message IDs or evidence IDs used in the demo.
- Making optional fields required without updating all sample data and UI code.

## Required checklist for schema PRs

- Update TypeScript schema.
- Update JSON Schema if relevant.
- Update Python model if relevant.
- Update sample demo JSON if relevant.
- Run `pnpm schemas:validate`.
- Explain why the change helps the demo or Band integration.
