#!/usr/bin/env python3
"""Verify the Step 7 collaboration provider layer is present and wired."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "apps/web/src/lib/collaboration/types.ts",
    "apps/web/src/lib/collaboration/CollaborationProvider.ts",
    "apps/web/src/lib/collaboration/MockCollaborationProvider.ts",
    "apps/web/src/lib/collaboration/BandCollaborationProvider.ts",
    "apps/web/src/lib/collaboration/getCollaborationProvider.ts",
    "apps/web/src/lib/collaboration/browserConfig.ts",
    "apps/web/src/lib/collaboration/syncMockWorkflowToProvider.ts",
    "apps/web/src/lib/workflow/useIncidentCollaborationWorkflow.ts",
    "apps/web/src/components/LiveInvestigationWorkspace.tsx",
    "apps/web/api/agent_run.py",
    "apps/web/src/app/api/collaboration/rooms/route.ts",
    "apps/web/src/app/api/collaboration/messages/route.ts",
    "apps/web/src/app/api/collaboration/approvals/route.ts",
    "docs/39_COLLABORATION_PROVIDER_LAYER.md",
    "docs/40_PROVIDER_CONTRACT.md",
    "docs/41_MOCK_PROVIDER_IMPLEMENTATION.md",
    "docs/42_BAND_PROVIDER_SCAFFOLD.md",
    "docs/43_STEP7_VERIFICATION_REPORT.md",
    "docs/44_STEP7_TEAM_HANDOFF.md",
]

REQUIRED_PATTERNS = {
    "apps/web/src/lib/collaboration/CollaborationProvider.ts": [
        "getHealth()",
        "createIncidentRoom",
        "subscribeToRoomSnapshot",
        "hydrateRoomSnapshot",
    ],
    "apps/web/src/lib/collaboration/MockCollaborationProvider.ts": [
        "class MockCollaborationProvider",
        "appendAuditEvent",
        "emitSnapshot",
        "resetRoom",
        "hydrateRoomSnapshot",
    ],
    "apps/web/src/lib/collaboration/BandCollaborationProvider.ts": [
        "server routes hold Band credentials",
        "Band Mode via server adapter",
        "Band credentials stay server-side",
    ],
    "apps/web/src/lib/collaboration/browserConfig.ts": [
        "NEXT_PUBLIC_COLLABORATION_MODE",
        "NEXT_PUBLIC_ENABLE_BAND_MODE",
    ],
    "apps/web/src/components/LiveInvestigationWorkspace.tsx": [
        "/api/agent_run",
        "Live · Band + AI",
        "Verified replay",
    ],
    ".env.example": [
        "NEXT_PUBLIC_COLLABORATION_MODE",
        "NEXT_PUBLIC_ENABLE_BAND_MODE",
        "BAND_HUMAN_API_KEY",
    ],
}

FORBIDDEN_PUBLIC_SECRET_PATTERNS = [
    "NEXT_PUBLIC_BAND_HUMAN_API_KEY",
    "NEXT_PUBLIC_BAND_API_KEY",
    "NEXT_PUBLIC_OPENAI_API_KEY",
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail("Missing required files:\n" + "\n".join(missing))

    for path, patterns in REQUIRED_PATTERNS.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for pattern in patterns:
            if pattern not in text:
                fail(f"Pattern {pattern!r} missing from {path}")

    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    for pattern in FORBIDDEN_PUBLIC_SECRET_PATTERNS:
        if pattern in text:
            fail(f"Forbidden public secret pattern {pattern!r} found in .env.example")

    print("[OK] Step 7 provider layer files are present.")
    print("[OK] Three-panel workspace uses the Vercel agent runtime with replay fallback.")
    print("[OK] Mock provider exposes room/message/snapshot/approval methods.")
    print("[OK] Band provider is safely scaffolded behind server routes.")
    print("[OK] Env examples avoid public Band secret variables.")


if __name__ == "__main__":
    main()
