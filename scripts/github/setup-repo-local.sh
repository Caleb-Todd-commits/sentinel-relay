#!/usr/bin/env bash
set -euo pipefail

# Sentinel Relay local GitHub setup helper.
# Run from repo root after installing GitHub CLI and logging in with `gh auth login`.

REPO_NAME="${REPO_NAME:-sentinel-relay}"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required. Install git first."
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI is required for automated repo creation. Install gh or create the repo manually."
  exit 1
fi

if [ ! -d ".git" ]; then
  git init
fi

git branch -M "$DEFAULT_BRANCH"

git add .

if git diff --cached --quiet; then
  echo "No staged changes to commit."
else
  git commit -m "chore: initialize Sentinel Relay baseline"
fi

if gh repo view "$REPO_NAME" >/dev/null 2>&1; then
  echo "GitHub repo $REPO_NAME already exists or is accessible."
else
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
fi

echo "Repo setup complete. Next recommended commands:"
echo "  bash scripts/github/create-labels.sh"
echo "  bash scripts/github/create-milestones.sh"
echo "  bash scripts/github/create-first-issues.sh"
