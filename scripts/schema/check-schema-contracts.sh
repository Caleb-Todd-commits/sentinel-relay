#!/usr/bin/env bash
set -euo pipefail

required_files=(
  "packages/schemas/src/index.ts"
  "packages/schemas/src/enums.ts"
  "packages/schemas/src/messages.ts"
  "packages/schemas/json-schema/agent-message.schema.json"
  "packages/schemas/json-schema/band-envelope.schema.json"
  "packages/schemas/json-schema/demo-incident.schema.json"
  "packages/schemas/python/sentinel_relay_schemas/models.py"
  "packages/sample-data/demo_incident.json"
  "docs/21_SHARED_SCHEMA_SYSTEM.md"
  "docs/22_BAND_MESSAGE_SCHEMA.md"
  "docs/23_AGENT_INPUT_OUTPUT_CONTRACTS.md"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "Missing required schema contract file: $file" >&2
    exit 1
  fi
done

python scripts/schema/validate-sample-data.py

echo "Schema contract file check passed."
