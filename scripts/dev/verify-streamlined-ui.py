#!/usr/bin/env python3
"""Verify the public interface stays within the three-panel product contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "apps/web/src/components/LiveInvestigationWorkspace.tsx"
LEGACY_PAGES = ["demo", "scenarios", "war-room", "report", "status"]
BANNED_VISIBLE_TERMS = ["judge", "hackathon", "band-style", "how it works"]


def main() -> int:
    text = WORKSPACE.read_text(encoding="utf-8")
    panel_count = text.count("data-product-panel=")
    if panel_count != 3:
        raise SystemExit(f"Expected exactly 3 product panels, found {panel_count}.")
    lowered = text.lower()
    for term in BANNED_VISIBLE_TERMS:
        if term in lowered:
            raise SystemExit(f"Public workspace contains banned term: {term}")
    for marker in ("role=\"dialog\"", "toast", "modal"):
        if marker in lowered:
            raise SystemExit(f"Public workspace contains disallowed popup marker: {marker}")

    for route in LEGACY_PAGES:
        page = ROOT / f"apps/web/src/app/{route}/page.tsx"
        if "redirect(" not in page.read_text(encoding="utf-8"):
            raise SystemExit(f"Legacy route does not redirect: /{route}")

    room_page = ROOT / "apps/web/src/app/scenarios/room/page.tsx"
    if "redirect(" not in room_page.read_text(encoding="utf-8"):
        raise SystemExit("Legacy scenario room route does not redirect.")

    print("Streamlined UI verification passed: 3 panels, no popup surfaces, legacy routes redirect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
