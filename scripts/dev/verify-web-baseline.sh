#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WEB_DIR="$ROOT_DIR/apps/web"

printf "\n[Sentinel Relay] Verifying baseline...\n"
printf "Root: %s\n" "$ROOT_DIR"
printf "Web:  %s\n\n" "$WEB_DIR"

if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm is not installed. Install it with: npm install -g pnpm"
  exit 1
fi

if [ ! -d "$WEB_DIR/node_modules" ]; then
  echo "node_modules not found in apps/web. Run: pnpm install"
  exit 1
fi

cd "$ROOT_DIR"
pnpm schemas:validate
pnpm schemas:typecheck
pnpm workflow:verify
pnpm typecheck
pnpm build

printf "\n[Sentinel Relay] Baseline verification passed.\n"
