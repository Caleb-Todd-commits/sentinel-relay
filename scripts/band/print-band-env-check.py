#!/usr/bin/env python3
"""Print a safe Band environment checklist without revealing secrets."""

from __future__ import annotations

import os

REQUIRED = [
    "BAND_PROVIDER_ENABLED",
    "NEXT_PUBLIC_ENABLE_BAND_MODE",
    "NEXT_PUBLIC_COLLABORATION_MODE",
    "BAND_COMMANDER_AGENT_API_KEY",
]

OPTIONAL = [
    "BAND_API_BASE_URL",
    "BAND_WS_URL",
    "BAND_HUMAN_API_KEY",
    "BAND_COMMANDER_PARTICIPANT_ID",
    "BAND_FORENSICS_PARTICIPANT_ID",
    "BAND_THREAT_INTEL_PARTICIPANT_ID",
    "BAND_CODE_REVIEW_PARTICIPANT_ID",
    "BAND_RISK_COMPLIANCE_PARTICIPANT_ID",
    "BAND_REMEDIATION_PARTICIPANT_ID",
]


def present(name: str) -> bool:
    return bool(os.environ.get(name, "").strip())


def main() -> int:
    print("Sentinel Relay Band env check")
    print("================================")
    for name in REQUIRED:
        print(f"{'OK ' if present(name) else 'MISS'} required {name}")
    for name in OPTIONAL:
        print(f"{'OK ' if present(name) else 'MISS'} optional {name}")

    if os.environ.get("NEXT_PUBLIC_COLLABORATION_MODE") == "band" and os.environ.get("NEXT_PUBLIC_ENABLE_BAND_MODE") != "true":
        print("WARN NEXT_PUBLIC_COLLABORATION_MODE=band but NEXT_PUBLIC_ENABLE_BAND_MODE is not true.")
    if os.environ.get("BAND_PROVIDER_ENABLED") == "true" and not present("BAND_COMMANDER_AGENT_API_KEY"):
        print("FAIL Band provider is enabled but BAND_COMMANDER_AGENT_API_KEY is missing.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
