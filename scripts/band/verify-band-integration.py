#!/usr/bin/env python3
"""Static verification for Step 8 Band integration files."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "apps/web/src/lib/band/bandConfig.ts",
    "apps/web/src/lib/band/bandRestClient.ts",
    "apps/web/src/lib/band/bandMappers.ts",
    "apps/web/src/lib/band/bandRoomStore.ts",
    "apps/web/src/app/api/collaboration/rooms/route.ts",
    "apps/web/src/app/api/collaboration/messages/route.ts",
    "apps/web/src/app/api/collaboration/approvals/route.ts",
    "apps/web/src/app/api/collaboration/health/route.ts",
    "apps/web/src/app/api/collaboration/stream/route.ts",
    "apps/web/src/lib/collaboration/BandCollaborationProvider.ts",
    "docs/45_REAL_BAND_INTEGRATION.md",
    "docs/46_BAND_ENVIRONMENT_SETUP.md",
    "docs/47_REMOTE_AGENT_RUNBOOK.md",
]

REQUIRED_SNIPPETS = {
    "apps/web/src/lib/band/bandRestClient.ts": [
        "/chats",
        "/participants",
        "/messages",
        "/events",
        "X-API-Key",
    ],
    "apps/web/src/app/api/collaboration/messages/route.ts": [
        "toBandEventFromAgentMessage",
        "sendAgentTextMessage",
        "buildMentions",
    ],
    "apps/web/src/lib/collaboration/BandCollaborationProvider.ts": [
        "EventSource",
        "/stream",
        "server adapter",
    ],
}


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        print("Missing files:")
        for path in missing:
            print(f"- {path}")
        return 1

    for path, snippets in REQUIRED_SNIPPETS.items():
        text = (ROOT / path).read_text()
        for snippet in snippets:
            if snippet not in text:
                print(f"Missing snippet {snippet!r} in {path}")
                return 1

    print("Step 8 Band integration static verification passed.")
    print(f"Checked {len(REQUIRED_FILES)} required files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
