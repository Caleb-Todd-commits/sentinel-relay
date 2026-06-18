#!/usr/bin/env python3
"""Print a safe Band environment checklist without revealing secrets."""

from __future__ import annotations

import os

REQUIRED = [
    "BAND_PROVIDER_ENABLED",
    "NEXT_PUBLIC_ENABLE_BAND_MODE",
    "NEXT_PUBLIC_COLLABORATION_MODE",
    "BAND_LEADER_AGENT_API_KEY",
]

OPTIONAL = [
    "BAND_API_BASE_URL",
    "BAND_WS_URL",
    "BAND_HUMAN_API_KEY",
    "BAND_LEADER_AGENT_ID",
    "BAND_LEADER_HANDLE",
    "BAND_FORENSICS_PARTICIPANT_ID",
    "BAND_THREAT_INTEL_PARTICIPANT_ID",
    "BAND_CODE_REVIEW_PARTICIPANT_ID",
    "BAND_RISK_COMPLIANCE_PARTICIPANT_ID",
    "BAND_REMEDIATION_PARTICIPANT_ID",
    "SENTINEL_RELAY_AGENT_RUNTIME",
    "SENTINEL_RELAY_APP_URL",
    "SENTINEL_RELAY_AGENT_ROOM_ID",
    "SENTINEL_RELAY_AGENT_POLL_SECONDS",
]

ALIASES = {
    "BAND_LEADER_AGENT_API_KEY": ["BAND_COMMANDER_AGENT_API_KEY", "COMMANDER_AGENT_API_KEY"],
    "BAND_LEADER_AGENT_ID": ["BAND_LEADER_PARTICIPANT_ID", "BAND_COMMANDER_PARTICIPANT_ID", "COMMANDER_AGENT_ID"],
    "BAND_LEADER_HANDLE": ["BAND_COMMANDER_HANDLE"],
    "BAND_FORENSICS_PARTICIPANT_ID": ["BAND_FORENSICS_AGENT_ID", "FORENSICS_AGENT_ID"],
    "BAND_THREAT_INTEL_PARTICIPANT_ID": ["BAND_THREAT_INTEL_AGENT_ID", "THREAT_INTEL_AGENT_ID"],
    "BAND_CODE_REVIEW_PARTICIPANT_ID": ["BAND_CODE_REVIEW_AGENT_ID", "CODE_REVIEW_AGENT_ID"],
    "BAND_RISK_COMPLIANCE_PARTICIPANT_ID": ["BAND_RISK_COMPLIANCE_AGENT_ID", "RISK_COMPLIANCE_AGENT_ID"],
    "BAND_REMEDIATION_PARTICIPANT_ID": ["BAND_REMEDIATION_AGENT_ID", "REMEDIATION_AGENT_ID"],
}


def present(name: str) -> bool:
    return bool(os.environ.get(name, "").strip())


def present_or_alias(name: str) -> bool:
    return present(name) or any(present(alias) for alias in ALIASES.get(name, []))


def main() -> int:
    print("Sentinel Relay Band env check")
    print("================================")
    for name in REQUIRED:
        print(f"{'OK ' if present_or_alias(name) else 'MISS'} required {name}")
    for name in OPTIONAL:
        print(f"{'OK ' if present_or_alias(name) else 'MISS'} optional {name}")

    if os.environ.get("NEXT_PUBLIC_COLLABORATION_MODE") == "band" and os.environ.get("NEXT_PUBLIC_ENABLE_BAND_MODE") != "true":
        print("WARN NEXT_PUBLIC_COLLABORATION_MODE=band but NEXT_PUBLIC_ENABLE_BAND_MODE is not true.")
    if os.environ.get("BAND_PROVIDER_ENABLED") == "true" and not present_or_alias("BAND_LEADER_AGENT_API_KEY"):
        print("FAIL Band provider is enabled but BAND_LEADER_AGENT_API_KEY is missing.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
