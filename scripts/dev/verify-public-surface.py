#!/usr/bin/env python3
"""Check current public documentation, links, terminology, and screenshots."""

from __future__ import annotations

import re
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUTHORITATIVE = [
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "apps/web/README.md",
    "docs/README.md",
    "docs/TEAM_START_HERE.md",
    "docs/architecture.md",
    "docs/05_TERMINOLOGY.md",
    "docs/CODING_AGENT_CONTEXT.md",
    "docs/demo-script.md",
    "docs/judging-notes.md",
    "docs/57_EVIDENCE_DRIVEN_AI_ML_API_WORKFLOW.md",
    "submission/README.md",
    "submission/submission-copy.md",
]
FORBIDDEN = {
    r"\b7 specialist agents\b": "Use six specialized agents plus a human Security Lead.",
    r"\bfully mocked baseline\b": "Describe verified replay or the current live path.",
    r"\bopen the war room\b": "The retired page redirects to the current workspace.",
    r"\bgo to the war room\b": "The retired page redirects to the current workspace.",
    r"\bmain demo surface\b": "Describe the current workspace.",
}
EXPECTED_SCREENSHOTS = {
    "approval.png",
    "custom-question.png",
    "result.png",
    "workspace.png",
}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"Not a valid PNG: {path.relative_to(ROOT)}")
    return struct.unpack(">II", header[16:24])


def main() -> int:
    failures: list[str] = []
    for relative in AUTHORITATIVE:
        path = ROOT / relative
        if not path.exists():
            failures.append(f"Missing authoritative document: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern, guidance in FORBIDDEN.items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                failures.append(f"Stale term in {relative}: {pattern!r}. {guidance}")

        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            target = target.split(maxsplit=1)[0]
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                failures.append(f"Broken local link in {relative}: {raw_target}")

    screenshot_dir = ROOT / "submission" / "screenshots"
    actual = {path.name for path in screenshot_dir.glob("*.png")}
    if actual != EXPECTED_SCREENSHOTS:
        failures.append(
            "Screenshot set is stale: "
            f"expected {sorted(EXPECTED_SCREENSHOTS)}, found {sorted(actual)}"
        )
    for name in sorted(actual & EXPECTED_SCREENSHOTS):
        width, height = png_dimensions(screenshot_dir / name)
        if width != 1440 or height < 900:
            failures.append(f"Unexpected screenshot dimensions for {name}: {width}x{height}")

    if failures:
        print("Public surface verification failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Public surface verification passed: current terms, local links, and screenshots are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
