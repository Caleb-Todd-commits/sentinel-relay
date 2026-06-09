#!/usr/bin/env bash
set -euo pipefail

# Creates the first issue board for Sentinel Relay.
# Requires labels and milestones to already exist.
# Run:
#   bash scripts/github/create-labels.sh
#   bash scripts/github/create-milestones.sh
#   bash scripts/github/create-first-issues.sh

create_issue() {
  local title="$1"
  local milestone="$2"
  local labels="$3"
  local body="$4"

  if gh issue list --state all --search "$title in:title" --json title --jq '.[].title' | grep -Fxq "$title"; then
    echo "Issue already exists: $title"
  else
    gh issue create \
      --title "$title" \
      --milestone "$milestone" \
      --label "$labels" \
      --body "$body" >/dev/null
    echo "Created issue: $title"
  fi
}

create_issue "[Repo] Create public GitHub repo and push baseline" "M0 — Repo Ready" "priority:P0,area:devops,type:chore,status:ready,risk:demo-critical" "Goal: create the public repo and push the baseline.\n\nAcceptance Criteria:\n- [ ] Repo exists publicly\n- [ ] main branch exists\n- [ ] Baseline files are pushed\n- [ ] README renders correctly\n- [ ] No secrets are committed\n- [ ] Teammates can clone or access the repo"

create_issue "[Repo] Add branch protection and PR review rules" "M0 — Repo Ready" "priority:P0,area:devops,type:chore,status:ready" "Goal: protect the main branch without slowing the team down.\n\nAcceptance Criteria:\n- [ ] main has branch protection\n- [ ] Pull request template appears\n- [ ] CODEOWNERS exists\n- [ ] Force pushes are blocked\n- [ ] Review expectations are documented"

create_issue "[Repo] Create GitHub labels and milestones" "M0 — Repo Ready" "priority:P0,area:devops,type:chore,status:ready" "Goal: create the labels and milestones defined in docs/09_ISSUES_MILESTONES_AND_LABELS.md.\n\nAcceptance Criteria:\n- [ ] Priority labels exist\n- [ ] Area labels exist\n- [ ] Type labels exist\n- [ ] Status labels exist\n- [ ] Risk labels exist\n- [ ] M0-M4 milestones exist"

create_issue "[Team] Assign initial workstream owners" "M0 — Repo Ready" "priority:P0,area:docs,type:decision,status:ready" "Goal: assign owners for product, frontend, Band/backend, agents, and demo/docs.\n\nAcceptance Criteria:\n- [ ] Frontend lead assigned\n- [ ] Band/backend lead assigned\n- [ ] Agent logic lead assigned\n- [ ] Demo/data/docs lead assigned\n- [ ] Caleb confirmed as product/cybersecurity/pitch lead\n- [ ] Each person has a first issue"

create_issue "[DevEx] Verify every teammate can run the app locally" "M0 — Repo Ready" "priority:P0,area:devops,type:chore,status:ready,risk:demo-critical" "Goal: make sure every teammate can run the project.\n\nAcceptance Criteria:\n- [ ] Each teammate clones repo\n- [ ] Each teammate runs install\n- [ ] Each teammate runs dev server\n- [ ] Setup issues are documented\n- [ ] README is corrected if needed"

create_issue "[Frontend] Build war room layout shell" "M1 — Mock Demo Vertical Slice" "priority:P0,area:frontend,type:feature,status:ready,risk:demo-critical" "Goal: create the main judge-facing War Room layout.\n\nAcceptance Criteria:\n- [ ] Incident header exists\n- [ ] Agent roster exists\n- [ ] Message stream exists\n- [ ] Evidence board exists\n- [ ] Timeline exists\n- [ ] Approval gate exists\n- [ ] Report preview exists\n- [ ] Layout is readable on a laptop screen"

create_issue "[Schemas] Define shared incident and message types" "M1 — Mock Demo Vertical Slice" "priority:P0,area:schemas,area:frontend,type:feature,status:ready,risk:demo-critical" "Goal: define stable shared types before expanding logic.\n\nAcceptance Criteria:\n- [ ] IncidentCase exists\n- [ ] AgentProfile exists\n- [ ] AgentMessage exists\n- [ ] Finding exists\n- [ ] EvidenceReference exists\n- [ ] Challenge exists\n- [ ] ApprovalRequest exists\n- [ ] ApprovalDecision exists\n- [ ] RemediationTask exists\n- [ ] FinalReport exists"

create_issue "[Demo] Build mocked incident state for API key exposure scenario" "M1 — Mock Demo Vertical Slice" "priority:P0,area:demo-data,area:frontend,type:demo,status:ready,risk:demo-critical" "Goal: create one strong sample incident that can run without external APIs.\n\nAcceptance Criteria:\n- [ ] Mock case loads\n- [ ] Agent list loads\n- [ ] Initial timeline loads\n- [ ] Message sequence exists\n- [ ] Evidence references connect to sample files\n- [ ] Final report seed exists"

create_issue "[Frontend] Add Run Demo Incident and replay controls" "M1 — Mock Demo Vertical Slice" "priority:P0,area:frontend,type:feature,status:ready,risk:demo-critical" "Goal: make the sample incident replayable for judges.\n\nAcceptance Criteria:\n- [ ] Run button starts sequence\n- [ ] Messages appear step by step\n- [ ] Replay resets state\n- [ ] Final report becomes available\n- [ ] Demo does not require credentials"

create_issue "[Frontend] Build structured agent message cards" "M1 — Mock Demo Vertical Slice" "priority:P0,area:frontend,type:feature,status:ready,risk:demo-critical" "Goal: make agent collaboration visible through structured cards.\n\nAcceptance Criteria:\n- [ ] Cards show agent name\n- [ ] Cards show message type\n- [ ] Confidence appears when available\n- [ ] Evidence references appear when available\n- [ ] Challenge messages are visually distinct\n- [ ] Approval requests are visually distinct"

create_issue "[Agent] Add visible risk/compliance challenge moment" "M1 — Mock Demo Vertical Slice" "priority:P0,area:agents,area:demo-data,type:demo,status:ready,risk:demo-critical" "Goal: add the moment that proves agents are reviewing each other, not just agreeing.\n\nAcceptance Criteria:\n- [ ] Risk agent challenges a weak breach conclusion\n- [ ] Challenge references missing evidence\n- [ ] Commander assigns verification\n- [ ] Challenge appears in War Room\n- [ ] Final report mentions challenge"

create_issue "[Frontend] Build human approval gate for containment actions" "M1 — Mock Demo Vertical Slice" "priority:P0,area:frontend,area:reporting,type:feature,status:ready,risk:demo-critical" "Goal: show enterprise-safe human-in-the-loop decision making.\n\nAcceptance Criteria:\n- [ ] Approval request appears\n- [ ] User can approve containment\n- [ ] User can reject or hold action\n- [ ] Decision is added to stream\n- [ ] Report includes decision"

create_issue "[Band] Create CollaborationProvider interface and mock provider" "M2 — Band Collaboration Connected" "priority:P0,area:band,area:frontend,type:feature,status:ready,risk:integration,risk:demo-critical" "Goal: make the UI provider-based so mock and Band modes can share the same flow.\n\nAcceptance Criteria:\n- [ ] CollaborationProvider interface exists\n- [ ] Mock provider implements it\n- [ ] Band provider scaffold exists\n- [ ] UI is provider-agnostic\n- [ ] Missing Band credentials fall back safely"

create_issue "[Report] Build audit-ready final report page" "M1 — Mock Demo Vertical Slice" "priority:P0,area:reporting,area:frontend,type:feature,status:ready,risk:demo-critical" "Goal: produce the enterprise-style output judges can understand.\n\nAcceptance Criteria:\n- [ ] Executive summary appears\n- [ ] Timeline appears\n- [ ] Evidence table appears\n- [ ] Root cause appears\n- [ ] Risk assessment appears\n- [ ] Human approval record appears\n- [ ] Remediation tasks appear\n- [ ] Audit trail appears"

create_issue "[Docs] Prepare README for hackathon judges" "M4 — Demo Polish and Submission" "priority:P0,area:docs,area:submission,type:docs,status:ready,risk:demo-critical" "Goal: make the repo understandable to judges.\n\nAcceptance Criteria:\n- [ ] README explains what was built\n- [ ] README explains Band usage\n- [ ] README explains agent roles\n- [ ] README explains how to run locally\n- [ ] README includes demo link placeholder\n- [ ] README includes architecture summary\n- [ ] README includes no secrets"
