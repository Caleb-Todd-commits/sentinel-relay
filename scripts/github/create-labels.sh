#!/usr/bin/env bash
set -euo pipefail

# Creates or updates the recommended Sentinel Relay labels.
# Requires GitHub CLI authenticated with `gh auth login`.

labels=(
  "priority:P0|b60205|Demo-critical; must be done or project may fail"
  "priority:P1|d93f0b|Important; strongly improves demo or judging score"
  "priority:P2|fbca04|Nice-to-have after core work is stable"
  "area:frontend|1d76db|Next.js pages, components, UI state"
  "area:band|5319e7|Band SDK/API integration and collaboration layer"
  "area:agents|0052cc|Agent prompts, logic, runners, structured outputs"
  "area:demo-data|0e8a16|Sample logs, incident packets, seeded demo data"
  "area:schemas|006b75|Shared types, message contracts, structured objects"
  "area:reporting|7057ff|Final report, audit trail, replay, timeline"
  "area:docs|0075ca|README, architecture, onboarding, pitch docs"
  "area:submission|c5def5|Final lablab submission, video, slide/pitch assets"
  "area:ui-polish|bfd4f2|Visual polish and judge-facing clarity"
  "area:devops|d4c5f9|Vercel, scripts, CI, environments"
  "type:feature|a2eeef|New behavior or product surface"
  "type:bug|d73a4a|Broken behavior or demo instability"
  "type:docs|0075ca|Documentation work"
  "type:chore|ffffff|Config, cleanup, repo management"
  "type:decision|fef2c0|Decision needed from team"
  "type:research|e4e669|Need to verify docs, API, or approach"
  "type:demo|c2e0c6|Demo flow, sample data, or video support"
  "status:ready|0e8a16|Ready to work"
  "status:in-progress|fbca04|Someone is actively working"
  "status:blocked|b60205|Cannot continue without help or decision"
  "status:needs-review|5319e7|Needs review or testing"
  "risk:demo-critical|ff0000|Affects the final demo path"
  "risk:security-sensitive|8b0000|Could touch secrets, credentials, or sensitive data"
  "risk:integration|d4c5f9|Depends on external API or runtime behavior"
  "risk:large-change|f9d0c4|Broad change that should be reviewed carefully"
)

for entry in "${labels[@]}"; do
  IFS='|' read -r name color description <<< "$entry"
  if gh label list --limit 200 | cut -f1 | grep -Fxq "$name"; then
    gh label edit "$name" --color "$color" --description "$description" >/dev/null
    echo "Updated label: $name"
  else
    gh label create "$name" --color "$color" --description "$description" >/dev/null
    echo "Created label: $name"
  fi
done
