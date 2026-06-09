#!/usr/bin/env bash
set -euo pipefail

# Creates Sentinel Relay milestones.
# Requires GitHub CLI authenticated with `gh auth login`.

create_milestone() {
  local title="$1"
  local description="$2"

  if gh api repos/:owner/:repo/milestones --paginate --jq '.[].title' | grep -Fxq "$title"; then
    echo "Milestone exists: $title"
  else
    gh api repos/:owner/:repo/milestones \
      -f title="$title" \
      -f description="$description" >/dev/null
    echo "Created milestone: $title"
  fi
}

create_milestone "M0 — Repo Ready" "Repo, templates, labels, branch rules, team assignments, and local setup verification."
create_milestone "M1 — Mock Demo Vertical Slice" "War Room, mock incident flow, evidence, timeline, approval, replay, and final report without live APIs."
create_milestone "M2 — Band Collaboration Connected" "Band room creation, agent registration, structured Band messages, and real collaboration layer."
create_milestone "M3 — Agent Intelligence and Structured Handoffs" "Specialized agent prompts, structured outputs, handoffs, challenge moment, remediation tasks."
create_milestone "M4 — Demo Polish and Submission" "Hosted app, final README, video, pitch, architecture diagram, smoke test, and submission copy."
