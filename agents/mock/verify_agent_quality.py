"""Quality gates for the inc-1042 agent workflow.

This test is intentionally more opinionated than schema validation. It asserts
that the agents stay evidence-grounded, preserve dissent, route human approval,
and keep AI/ML API enrichment behind guardrails.
"""

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

_FORBIDDEN_OVERCLAIMS = (
    "confirmed downstream misuse",
    "confirmed resale",
    "customer notification approved",
    "known attacker",
    "attributed to",
    "nation-state",
    "apt ",
    " apt",
)
_PARTNER_FALLBACK_STATUSES = {
    "live_api",
    "disabled_fallback",
    "missing_api_key_fallback",
    "api_error_fallback",
    "invalid_response_fallback",
}


def main() -> int:
    packet = load_incident()
    facts = analyze_incident_evidence(
        AgentTurnContext(
            case=packet.case,
            room_id=packet.case["roomId"],
            agent_profile=packet.agents["agent-forensics"],
            recent_messages=[],
            evidence=packet.evidence,
            current_state=packet.state,
            task={"kind": "quality"},
            sequence=1,
        )
    )
    room = run_flow()
    messages = room.transcript

    assert len(messages) == EXPECTED_STEPS, f"expected {EXPECTED_STEPS} messages, got {len(messages)}"
    _assert_no_forbidden_overclaims(messages)
    _assert_forensics(messages, facts)
    _assert_code_review(messages, facts)
    _assert_threat_intel(messages, facts)
    _assert_cross_review(messages, facts)
    _assert_risk_gate(messages, facts)
    _assert_human_gate(messages)
    _assert_remediation(messages, facts)
    _assert_final_report(messages, facts)

    print(
        "OK: agent quality gates passed "
        "(evidence grounding, dissent, human approval, AI/ML guardrails, no overclaim)."
    )
    return 0


def _assert_forensics(messages: list[dict[str, Any]], facts: Any) -> None:
    message = _find_message(messages, "agent-forensics", "finding")
    data = _payload_data(message)
    exposure_window = data["exposureWindow"]
    derived = data["derivedFacts"]

    assert data["recordsExportedEstimate"] == facts.api.unauthorized_records_returned
    assert sum(item["records"] for item in data["exportBreakdown"]) == facts.api.unauthorized_records_returned
    assert exposure_window["openedAt"] == facts.cloudtrail.deploy_enabled_fallback_at
    assert exposure_window["fallbackFirstLoadedAt"] == facts.auth.fallback_loaded_at
    assert exposure_window["firstUnauthorizedUseAt"] == facts.api.first_unauthorized_success_at
    assert exposure_window["issuerVerifiedInactiveAt"] == facts.auth.issuer_verified_inactive_at
    assert exposure_window["status"] == "verified_closed"
    assert derived["unauthorizedSourceIps"] == facts.api.unauthorized_ips
    assert derived["bulkExportRecords"] == facts.api.bulk_export_records
    assert derived["vipExportRecords"] == facts.api.vip_export_records
    assert "downstream reuse" in _lower_json(data)


def _assert_code_review(messages: list[dict[str, Any]], facts: Any) -> None:
    message = _find_message(messages, "agent-code-review", "finding")
    data = _payload_data(message)
    derived = data["derivedFacts"]
    credential_hunt = data["siblingCredentialHunt"]

    assert derived["changedFiles"] == facts.code.changed_files
    assert derived["failOpenFallbackAdded"] is facts.code.fail_open_fallback_added
    assert derived["envReleaseAdded"] is facts.code.env_release_added
    assert derived["fallbackTokenVariableAdded"] is facts.code.fallback_token_variable_added
    assert derived["customerExportEnabledAdded"] is facts.code.customer_export_enabled_added
    assert derived["unresolvedHighSecretFindings"] == facts.secret_scan.unresolved_high_count
    assert credential_hunt["principal"] == facts.auth.subject
    assert len(credential_hunt["credentialsAuthenticatingPrincipal"]) >= 2
    assert any(
        item.get("issuer") == "AWS Secrets Manager"
        for item in credential_hunt["credentialsAuthenticatingPrincipal"]
    )
    assert any(
        item.get("issuer") == "static env (PAYMENTS_API_FALLBACK_TOKEN)"
        for item in credential_hunt["credentialsAuthenticatingPrincipal"]
    )


def _assert_threat_intel(messages: list[dict[str, Any]], facts: Any) -> None:
    message = _find_message(messages, "agent-threat-intel", "finding")
    data = _payload_data(message)
    derived = data["derivedFacts"]

    assert derived["unexpectedIps"] == facts.threat.unexpected_ips
    assert derived["expectedIps"] == facts.threat.expected_ips
    assert derived["postRotationRetryIps"] == facts.threat.post_rotation_retry_ips
    assert derived["canaryProbeIps"] == facts.threat.canary_probe_ips
    assert derived["automationUserAgents"] == facts.threat.automation_user_agents
    assert data["likelihoodOfExploitation"] == "high"
    assert "do not claim real-world threat-actor attribution" in _lower_json(data)
    assert "cannot confirm resale" in _lower_json(data)


def _assert_cross_review(messages: list[dict[str, Any]], facts: Any) -> None:
    handoff = _find_message(messages, "agent-commander", "handoff")
    handoff_data = _payload_data(handoff)
    reviews = [
        _find_message(messages, "agent-forensics", "verification"),
        _find_message(messages, "agent-code-review", "verification"),
        _find_message(messages, "agent-threat-intel", "verification"),
    ]
    risk = _find_message(messages, "agent-risk-compliance", "challenge")

    assert handoff["targetAgentIds"] == [
        "agent-forensics",
        "agent-code-review",
        "agent-threat-intel",
    ]
    assert handoff_data["blocksRiskGateUntil"] == "all_required_verifications_posted"
    assert len(handoff_data["sourceFindingMessageIds"]) == 3
    assert all(review["sequence"] < risk["sequence"] for review in reviews)

    forensics_review = _payload_data(reviews[0])
    code_review = _payload_data(reviews[1])
    threat_review = _payload_data(reviews[2])

    assert forensics_review["derivedFacts"]["recordsReturnedToUnexpectedIps"] == facts.api.unauthorized_records_returned
    assert "downstream resale" in _lower_json(forensics_review["challengesPreserved"])
    assert code_review["derivedFacts"]["rootCauseKind"] == facts.code.root_cause_kind
    assert any("Secrets Manager primary" in item for item in code_review["requiredContainmentControls"])
    assert threat_review["derivedFacts"]["unexpectedIps"] == facts.threat.unexpected_ips
    assert "do not claim real-world threat-actor attribution" in _lower_json(threat_review)


def _assert_risk_gate(messages: list[dict[str, Any]], facts: Any) -> None:
    message = _find_message(messages, "agent-risk-compliance", "challenge")
    data = _payload_data(message)
    policy_gate = data["policyGate"]
    partner_tool = data["partnerTool"]
    derived = data["derivedFacts"]

    assert partner_tool["provider"] == "AI/ML API"
    assert partner_tool["label"] == "risk_policy_gate"
    assert partner_tool["status"] in _PARTNER_FALLBACK_STATUSES
    assert policy_gate["classification"] == "suspected_exposure"
    assert policy_gate["recommendedSeverity"] == "high"
    assert policy_gate["customerNotification"] == "hold_pending_legal_scope"
    assert policy_gate["confidence"] <= 0.9
    assert "external_customer_notification" in data["humanApprovalRequired"]
    assert "external_customer_notification" in data["deferredPendingHuman"]
    assert derived["recordsReturnedToUnexpectedIps"] == facts.api.unauthorized_records_returned
    assert derived["unexpectedIps"] == facts.api.unauthorized_ips
    assert derived["policyId"] == facts.policy.policy_id
    assert "confirmed downstream resale or misuse" in _lower_json(policy_gate["unsupportedClaims"])
    assert data["crossReviewGate"]["gateSatisfied"] is True
    assert len(data["crossReviewGate"]["receivedVerificationMessageIds"]) == 3


def _assert_human_gate(messages: list[dict[str, Any]]) -> None:
    request = _find_message(messages, "agent-commander", "approval_request")
    decision = _find_message(messages, "agent-human-approver", "approval_decision")
    request_data = _payload_data(request)
    decision_data = _payload_data(decision)

    assert request["targetAgentIds"] == ["agent-human-approver"]
    assert request_data["requestedActions"] == [
        "Rotate fallback token",
        "Disable fallback token path",
        "Patch config",
    ]
    assert request_data["notRequestedActions"] == ["External customer notification", "Incident closure"]
    assert decision_data["decision"] == "approved"
    assert decision_data["approvedScope"] == [
        "Rotate fallback token",
        "Disable fallback token path",
        "Patch config",
    ]
    assert decision_data["explicitlyNotApproved"] == ["External customer notification", "Incident closure"]


def _assert_remediation(messages: list[dict[str, Any]], facts: Any) -> None:
    message = _find_message(messages, "agent-remediation", "remediation_task")
    data = _payload_data(message)
    derived = data["derivedFacts"]

    assert "External customer notification" in data["excludedPendingApproval"]
    assert "Incident closure" in data["excludedPendingApproval"]
    assert "External customer notification" not in data["approvedScope"]
    assert facts.auth.issuer_verified_inactive_at in data["windowClosedCriterion"]
    assert derived["issuerVerifiedInactiveAt"] == facts.auth.issuer_verified_inactive_at
    assert derived["managedSecretId"] == facts.cloudtrail.managed_secret_id
    assert derived["fallbackTokenId"] == facts.auth.fallback_token_id
    assert derived["primaryTokenIds"] == facts.auth.primary_token_ids
    assert any(
        credential.get("ref") == facts.cloudtrail.managed_secret_id
        for credential in data["siblingCredentialsToAddress"]
    )
    assert any(task["id"] == "rem-005" and "federated credentials" in task["title"] for task in data["tasks"])
    assert any(task["id"] == "rem-006" and "secret-scan" in task["title"] for task in data["tasks"])


def _assert_final_report(messages: list[dict[str, Any]], facts: Any) -> None:
    message = _find_message(messages, "agent-commander", "report_section")
    data = _payload_data(message)
    synthesis = data["synthesis"]
    partner_tool = data["partnerTool"]
    derived = data["derivedFacts"]

    assert partner_tool["provider"] == "AI/ML API"
    assert partner_tool["label"] == "band_leader_synthesis"
    assert partner_tool["status"] in _PARTNER_FALLBACK_STATUSES
    assert synthesis["severity"] == "high"
    assert synthesis["confidence"] <= 0.95
    assert "10,227" in synthesis["executiveSummary"]
    assert "10,227" in message["summary"]
    assert "Risk kept the case at suspected exposure" in message["summary"]
    assert data["heldActions"] == ["External customer notification", "Incident closure"]
    assert data["crossAgentReview"]["status"] == "complete"
    assert len(data["crossAgentReview"]["verificationMessageIds"]) == 3
    assert len(data["auditTrailMessageIds"]) == EXPECTED_STEPS - 1
    assert derived["recordsReturnedToUnexpectedIps"] == facts.api.unauthorized_records_returned
    assert derived["unexpectedIps"] == facts.api.unauthorized_ips
    assert derived["unresolvedHighSecretFindings"] == facts.secret_scan.unresolved_high_count
    assert any(
        "Forensics proves records returned; Risk refuses" in disagreement
        for disagreement in data["surfacedDisagreements"]
    )


def _assert_no_forbidden_overclaims(messages: list[dict[str, Any]]) -> None:
    for message in messages:
        searchable = _lower_json(
            {
                "title": message.get("title"),
                "summary": message.get("summary"),
                "nextAction": message.get("nextAction"),
                "payload": message.get("payload"),
            }
        )
        for phrase in _FORBIDDEN_OVERCLAIMS:
            assert phrase not in searchable, (
                f"message {message.get('id')} contains forbidden overclaim phrase: {phrase!r}"
            )


def _find_message(messages: list[dict[str, Any]], agent_id: str, message_type: str) -> dict[str, Any]:
    matches = [
        message
        for message in messages
        if message.get("agentId") == agent_id and message.get("type") == message_type
    ]
    assert matches, f"missing {message_type} message from {agent_id}"
    return matches[-1]


def _payload_data(message: dict[str, Any]) -> dict[str, Any]:
    payload = message.get("payload") or {}
    data = payload.get("data") or {}
    assert isinstance(data, dict), f"{message.get('id')} payload.data must be an object"
    return data


def _lower_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True).lower()


if __name__ == "__main__":
    raise SystemExit(main())
