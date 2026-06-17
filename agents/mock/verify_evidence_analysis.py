"""Verify evidence-derived facts used by the Sentinel Relay agents."""

from __future__ import annotations

import sys
from pathlib import Path

_AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_DIR))

from common.evidence_analysis import analyze_incident_evidence  # noqa: E402
from common.fixtures import load_incident  # noqa: E402
from common.schema import AgentTurnContext  # noqa: E402


def main() -> int:
    packet = load_incident()
    ctx = AgentTurnContext(
        case=packet.case,
        room_id=packet.case["roomId"],
        agent_profile=packet.agents["agent-forensics"],
        recent_messages=[],
        evidence=packet.evidence,
        current_state=packet.state,
        task={"kind": "verify"},
        sequence=1,
    )
    facts = analyze_incident_evidence(ctx)

    assert facts.api.unauthorized_records_returned == 10227
    assert facts.api.unauthorized_ips == ["198.51.100.188", "203.0.113.77"]
    assert facts.api.first_unauthorized_success_at == "2026-06-12T21:04:59Z"
    assert facts.auth.fallback_loaded_at == "2026-06-12T20:55:38Z"
    assert facts.auth.issuer_verified_inactive_at == "2026-06-12T21:12:02Z"
    assert facts.cloudtrail.deploy_enabled_fallback_at == "2026-06-12T20:47:11Z"
    assert facts.cloudtrail.fallback_env_enabled is True
    assert facts.auth.compromised_token_id == "svc-payments-fallback-redacted"
    assert facts.auth.credential_mechanism == "static fallback bearer token"
    assert facts.code.root_cause_kind == "fallback_token_path"
    assert facts.code.fail_open_fallback_added is True
    assert facts.code.env_release_added is True
    assert facts.secret_scan.unresolved_high_count == 1
    assert facts.threat.minutes_from_deploy_to_abuse == 18
    assert "external_customer_notification" in facts.policy.human_approval_actions

    print(
        "OK: evidence analysis derives record counts, exposure window, code/config risk, "
        "threat timing, and policy gates from inc-1042 fixtures."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
