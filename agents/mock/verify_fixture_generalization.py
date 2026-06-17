"""Verify agents generalize beyond the primary inc-1042 fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_DIR))

from common.evidence_analysis import analyze_incident_evidence  # noqa: E402
from common.fixtures import load_incident  # noqa: E402
from common.schema import AgentTurnContext  # noqa: E402
from mock.run_mock_flow import EXPECTED_STEPS, run_flow  # noqa: E402

_INC_1043_DIR = Path("data/incidents/inc-1043")
_FORBIDDEN_1043_TEXT = (
    "1042",
    "inc-1042",
    "payments_api_fallback_token",
    "allow_fallback_token",
    ".env.release",
    "svc-payments-api",
    "secrets manager primary",
)


def main() -> int:
    _assert_inc_1042_still_parses()
    packet = load_incident(_INC_1043_DIR)
    facts = _facts(packet)

    assert packet.case["id"] == "INC-1043"
    assert packet.case["roomId"] == "band-room-inc-1043"
    assert facts.api.unauthorized_records_returned == 3636
    assert facts.api.unauthorized_ips == ["198.51.100.221", "203.0.113.142"]
    assert facts.api.first_unauthorized_success_at == "2026-06-14T16:24:39Z"
    assert facts.auth.subject == "svc-analytics-exporter"
    assert facts.auth.compromised_token_id == "svc-analytics-exporter-oidc-redacted"
    assert facts.auth.credential_mechanism == "overbroad GitHub OIDC trust"
    assert facts.auth.credential_first_observed_at == "2026-06-14T16:20:11Z"
    assert facts.auth.issuer_verified_inactive_at == "2026-06-14T16:31:08Z"
    assert facts.cloudtrail.configuration_change_event_name == "UpdateAssumeRolePolicy"
    assert facts.code.root_cause_kind == "oidc_trust_wildcard"
    assert facts.code.customer_export_enabled_added is True
    assert facts.secret_scan.unresolved_high_count == 0
    assert facts.policy.policy_id == "SEC-IR-OIDC-002"

    room = run_flow(incident_id="INC-1043")
    messages = room.transcript
    assert len(messages) == EXPECTED_STEPS
    assert [message["sequence"] for message in messages] == list(range(1, EXPECTED_STEPS + 1))
    assert messages[0]["caseId"] == "INC-1043"
    assert messages[0]["roomId"] == "band-room-inc-1043"
    assert messages[-1]["type"] == "report_section"
    _assert_no_primary_fixture_bleed(messages)
    _assert_inc_1043_agent_outputs(messages, facts)

    print(
        "OK: inc-1043 fixture proves agents generalize to OIDC trust misuse "
        "without fallback-token copy."
    )
    return 0


def _assert_inc_1042_still_parses() -> None:
    packet = load_incident()
    facts = _facts(packet)
    assert packet.case["id"] == "INC-1042"
    assert facts.api.unauthorized_records_returned == 10227
    assert facts.code.root_cause_kind == "fallback_token_path"
    assert facts.auth.compromised_token_id == "svc-payments-fallback-redacted"
    assert facts.secret_scan.unresolved_high_count == 1


def _assert_inc_1043_agent_outputs(messages: list[dict[str, Any]], facts: Any) -> None:
    forensics = _find(messages, "agent-forensics", "finding")
    forensics_data = _payload_data(forensics)
    assert "federated token" in forensics["title"].lower()
    assert "3,636" in forensics["summary"]
    assert forensics_data["recordsExportedEstimate"] == facts.api.unauthorized_records_returned
    assert forensics_data["compromisedIdentity"]["credentialLabel"] == facts.auth.compromised_token_id
    assert forensics_data["exposureWindow"]["credentialFirstObservedAt"] == facts.auth.credential_first_observed_at

    code_review = _find(messages, "agent-code-review", "finding")
    code_data = _payload_data(code_review)
    assert "oidc trust wildcard" in code_review["title"].lower()
    assert "no committed secret" in code_review["summary"].lower()
    assert code_data["derivedFacts"]["rootCauseKind"] == "oidc_trust_wildcard"
    assert code_data["derivedFacts"]["unresolvedHighSecretFindings"] == 0
    assert any(
        item.get("issuer") == "GitHub OIDC / AWS STS"
        for item in code_data["siblingCredentialHunt"]["credentialsAuthenticatingPrincipal"]
    )

    threat = _find(messages, "agent-threat-intel", "finding")
    threat_data = _payload_data(threat)
    assert "oidc" in threat["title"].lower()
    assert threat_data["derivedFacts"]["unexpectedIps"] == facts.threat.unexpected_ips
    assert "do not claim real-world threat-actor attribution" in _lower_json(threat_data)

    cross_review = _find(messages, "agent-commander", "handoff")
    cross_review_data = _payload_data(cross_review)
    assert cross_review_data["requiredReviewerAgentIds"] == [
        "agent-forensics",
        "agent-code-review",
        "agent-threat-intel",
    ]
    assert len(cross_review_data["sourceFindingMessageIds"]) == 3

    forensics_review = _find(messages, "agent-forensics", "verification")
    forensics_review_data = _payload_data(forensics_review)
    assert forensics_review_data["derivedFacts"]["recordsReturnedToUnexpectedIps"] == 3636
    assert forensics_review_data["derivedFacts"]["rootCauseKind"] == "oidc_trust_wildcard"

    code_review_check = _find(messages, "agent-code-review", "verification")
    code_review_check_data = _payload_data(code_review_check)
    assert any("OIDC trust" in item for item in code_review_check_data["requiredContainmentControls"])

    threat_review = _find(messages, "agent-threat-intel", "verification")
    threat_review_data = _payload_data(threat_review)
    assert threat_review_data["derivedFacts"]["rootCauseKind"] == "oidc_trust_wildcard"
    assert "downstream resale" in _lower_json(threat_review_data)

    risk = _find(messages, "agent-risk-compliance", "challenge")
    risk_data = _payload_data(risk)
    assert risk_data["derivedFacts"]["policyId"] == "SEC-IR-OIDC-002"
    assert risk_data["derivedFacts"]["recordsReturnedToUnexpectedIps"] == 3636
    assert risk_data["policyGate"]["customerNotification"] == "hold_pending_legal_scope"
    assert risk_data["crossReviewGate"]["gateSatisfied"] is True
    assert len(risk_data["crossReviewGate"]["receivedVerificationMessageIds"]) == 3

    approval = _find(messages, "agent-commander", "approval_request")
    approval_data = _payload_data(approval)
    assert approval_data["requestedActions"] == [
        "Revoke federated sessions",
        "Tighten OIDC trust policy",
        "Patch export scope",
    ]
    assert approval_data["notRequestedActions"] == ["External customer notification", "Incident closure"]

    remediation = _find(messages, "agent-remediation", "remediation_task")
    remediation_data = _payload_data(remediation)
    assert "oidc trust rollback" in remediation["title"].lower()
    assert "External customer notification" in remediation_data["excludedPendingApproval"]
    assert any(task["id"] == "rem-002" and "OIDC trust" in task["title"] for task in remediation_data["tasks"])
    assert remediation_data["derivedFacts"]["rootCauseKind"] == "oidc_trust_wildcard"

    report = _find(messages, "agent-commander", "report_section")
    report_data = _payload_data(report)
    assert "3,636" in report["summary"]
    assert "OIDC trust-policy regression" in report_data["executiveSummary"]
    assert report_data["reportId"] == "report-inc-1043"
    assert report_data["derivedFacts"]["recordsReturnedToUnexpectedIps"] == 3636
    assert report_data["crossAgentReview"]["status"] == "complete"


def _assert_no_primary_fixture_bleed(messages: list[dict[str, Any]]) -> None:
    text = _lower_json(messages)
    for forbidden in _FORBIDDEN_1043_TEXT:
        assert forbidden not in text, f"inc-1043 output leaked primary fixture wording: {forbidden}"


def _facts(packet: Any) -> Any:
    return analyze_incident_evidence(
        AgentTurnContext(
            case=packet.case,
            room_id=packet.case["roomId"],
            agent_profile=packet.agents["agent-forensics"],
            recent_messages=[],
            evidence=packet.evidence,
            current_state=packet.state,
            task={"kind": "verify", "incidentDir": str(_INC_1043_DIR) if packet.case["id"] == "INC-1043" else ""},
            sequence=1,
        )
    )


def _find(messages: list[dict[str, Any]], agent_id: str, message_type: str) -> dict[str, Any]:
    matches = [
        message
        for message in messages
        if message.get("agentId") == agent_id and message.get("type") == message_type
    ]
    assert matches, f"missing {message_type} from {agent_id}"
    return matches[-1]


def _payload_data(message: dict[str, Any]) -> dict[str, Any]:
    data = (message.get("payload") or {}).get("data") or {}
    assert isinstance(data, dict)
    return data


def _lower_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True).lower()


if __name__ == "__main__":
    raise SystemExit(main())
