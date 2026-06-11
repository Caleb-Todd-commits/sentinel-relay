#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WEB_DIR="$ROOT_DIR/apps/web"

printf "\n[Sentinel Relay] Verifying baseline...\n"
printf "Root: %s\n" "$ROOT_DIR"
printf "Web:  %s\n\n" "$WEB_DIR"

if command -v corepack >/dev/null 2>&1; then
  PNPM_CMD=(corepack pnpm)
elif command -v pnpm >/dev/null 2>&1; then
  PNPM_CMD=(pnpm)
else
  echo "pnpm is not installed. Install it with Corepack or Homebrew:"
  echo "  corepack prepare pnpm@10.11.0 --activate"
  echo "  brew install pnpm"
  exit 1
fi

if [ ! -d "$WEB_DIR/node_modules" ]; then
  echo "node_modules not found in apps/web. Run: ${PNPM_CMD[*]} install"
  exit 1
fi

cd "$ROOT_DIR"
"${PNPM_CMD[@]}" schemas:validate
"${PNPM_CMD[@]}" schemas:typecheck
"${PNPM_CMD[@]}" workflow:verify
"${PNPM_CMD[@]}" typecheck
"${PNPM_CMD[@]}" build

printf "\n[Sentinel Relay] Baseline verification passed.\n"
