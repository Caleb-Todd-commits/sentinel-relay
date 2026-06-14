#!/usr/bin/env python3
"""Static checks for the evidence-driven prize workflow."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "data" / "incidents" / "inc-1042"
EXPECTED_FILES = [
    "evidence_manifest.json",
    "api_gateway_logs.jsonl",
    "auth_events.jsonl",
    "cloudtrail_events.jsonl",
    "git_diff.patch",
    "secret_scan.json",
    "suspicious_ips.json",
    "incident_policy.json",
    "ground_truth_for_judges.md",
]
EXPECTED_EVIDENCE_IDS = {
    "ev-api-gateway-logs",
    "ev-auth-events",
    "ev-cloudtrail-events",
    "ev-code-diff",
    "ev-secret-scan",
    "ev-ip-intel",
    "ev-incident-policy",
}


def read_json(path: Path):
    return json.loads(path.read_text())


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_no, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: {exc}") from exc
    return rows


def main() -> int:
    missing = [name for name in EXPECTED_FILES if not (EVIDENCE_DIR / name).exists()]
    if missing:
        print("Missing evidence files:")
        for name in missing:
            print(f"- {name}")
        return 1

    manifest = read_json(EVIDENCE_DIR / "evidence_manifest.json")
    ids = {item["id"] for item in manifest["evidence"]}
    if ids != EXPECTED_EVIDENCE_IDS:
        print(f"Evidence ID mismatch: {sorted(ids)}")
        return 1

    api_logs = read_jsonl(EVIDENCE_DIR / "api_gateway_logs.jsonl")
    auth_events = read_jsonl(EVIDENCE_DIR / "auth_events.jsonl")
    cloudtrail = read_jsonl(EVIDENCE_DIR / "cloudtrail_events.jsonl")
    if len(api_logs) < 8 or len(auth_events) < 6 or len(cloudtrail) < 4:
        print("Evidence packet is too small to demonstrate multi-agent reasoning.")
        return 1

    returned = sum(
        row.get("records_returned", 0)
        for row in api_logs
        if row.get("status") == 200 and "fallback_token" in row.get("risk_flags", [])
    )
    if returned != 10227:
        print(f"Unexpected suspicious record count: {returned}")
        return 1

    diff = (EVIDENCE_DIR / "git_diff.patch").read_text()
    for required in ["ALLOW_FALLBACK_TOKEN", "PAYMENTS_API_FALLBACK_TOKEN", "customer_records_using_fallback_token"]:
        if required not in diff:
            print(f"Missing expected diff marker: {required}")
            return 1

    runner = (ROOT / "scripts" / "demo" / "run-evidence-band-workflow.py").read_text()
    for required in ["AIMLAPI_API_KEY", "risk_policy_gate", "band_leader_synthesis", "/api/collaboration"]:
        if required not in runner:
            print(f"Evidence workflow runner missing marker: {required}")
            return 1

    print("Evidence-driven AI/ML API workflow static verification passed.")
    print(f"Checked {len(EXPECTED_FILES)} files, {len(api_logs)} API rows, {len(auth_events)} auth events, {len(cloudtrail)} CloudTrail rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
