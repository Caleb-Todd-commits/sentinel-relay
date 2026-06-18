#!/usr/bin/env python3
"""Static checks for the evidence-driven prize workflow."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INCIDENTS_DIR = ROOT / "data" / "incidents"
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
EXPECTED_INCIDENTS = {
    "inc-1042": {
        "caseId": "INC-1042",
        "recordsReturned": 10227,
        "requiredDiffMarkers": [
            "ALLOW_FALLBACK_TOKEN",
            "PAYMENTS_API_FALLBACK_TOKEN",
            "customer_records_using_fallback_token",
        ],
    },
    "inc-1043": {
        "caseId": "INC-1043",
        "recordsReturned": 3636,
        "requiredDiffMarkers": [
            "token.actions.githubusercontent.com:sub",
            "repo:acme/payments:*",
            "customer:records:export",
        ],
    },
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
    checked_rows = {}
    for incident_slug, expectation in EXPECTED_INCIDENTS.items():
        evidence_dir = INCIDENTS_DIR / incident_slug
        missing = [name for name in EXPECTED_FILES if not (evidence_dir / name).exists()]
        if missing:
            print(f"Missing evidence files for {incident_slug}:")
            for name in missing:
                print(f"- {name}")
            return 1

        manifest = read_json(evidence_dir / "evidence_manifest.json")
        if manifest.get("caseId") != expectation["caseId"]:
            print(f"{incident_slug} caseId mismatch: {manifest.get('caseId')}")
            return 1

        ids = {item["id"] for item in manifest["evidence"]}
        if ids != EXPECTED_EVIDENCE_IDS:
            print(f"{incident_slug} evidence ID mismatch: {sorted(ids)}")
            return 1

        api_logs = read_jsonl(evidence_dir / "api_gateway_logs.jsonl")
        auth_events = read_jsonl(evidence_dir / "auth_events.jsonl")
        cloudtrail = read_jsonl(evidence_dir / "cloudtrail_events.jsonl")
        if len(api_logs) < 8 or len(auth_events) < 6 or len(cloudtrail) < 3:
            print(f"{incident_slug} packet is too small to demonstrate multi-agent reasoning.")
            return 1

        returned = sum(
            row.get("records_returned", 0)
            for row in api_logs
            if row.get("status") == 200
            and "unexpected_source_ip" in row.get("risk_flags", [])
            and (
                "fallback_token" in row.get("risk_flags", [])
                or "federated_token" in row.get("risk_flags", [])
                or "oidc_trust_misuse" in row.get("risk_flags", [])
            )
        )
        if returned != expectation["recordsReturned"]:
            print(f"{incident_slug} unexpected suspicious record count: {returned}")
            return 1

        diff = (evidence_dir / "git_diff.patch").read_text()
        for required in expectation["requiredDiffMarkers"]:
            if required not in diff:
                print(f"{incident_slug} missing expected diff marker: {required}")
                return 1

        checked_rows[incident_slug] = (len(api_logs), len(auth_events), len(cloudtrail))

    runner = (ROOT / "scripts" / "demo" / "run-evidence-band-workflow.py").read_text()
    for required in ["--incident-id", "run_mock_agent_flow", "resolve_incident_dir", "/api/collaboration"]:
        if required not in runner:
            print(f"Evidence workflow runner missing marker: {required}")
            return 1

    review_markers = {
        "agents/commander/agent.py": ["request_cross_review", "cross_review", "blocksRiskGateUntil"],
        "agents/common/turn_adapter.py": ["_should_request_cross_review", "_all_review_verifications_present"],
        "agents/common/collaboration_api_worker.py": ["_is_cross_review_handoff", "_all_review_verifications_present"],
    }
    for relative_path, markers in review_markers.items():
        text = (ROOT / relative_path).read_text()
        for marker in markers:
            if marker not in text:
                print(f"Cross-agent review gate missing marker {marker!r} in {relative_path}.")
                return 1

    enrichment = (ROOT / "agents" / "common" / "aimlapi_enrichment.py").read_text()
    for required in ["risk_policy_gate", "band_leader_synthesis", "sanitize_risk_gate", "sanitize_band_leader_synthesis"]:
        if required not in enrichment:
            print(f"Agent AI/ML enrichment missing marker: {required}")
            return 1

    print("Evidence-driven AI/ML API workflow static verification passed.")
    print(
        "Checked "
        + ", ".join(
            f"{slug}: {rows[0]} API rows, {rows[1]} auth events, {rows[2]} CloudTrail rows"
            for slug, rows in checked_rows.items()
        )
        + "."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
