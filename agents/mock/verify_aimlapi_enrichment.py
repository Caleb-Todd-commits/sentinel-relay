"""Verify guarded AI/ML API enrichment without making network calls."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_DIR))

from common.aimlapi_enrichment import (  # noqa: E402
    AimlApiResult,
    enrich_band_leader_synthesis,
    enrich_risk_policy_gate,
)
from common.evidence_analysis import analyze_incident_evidence  # noqa: E402
from common.fixtures import load_incident  # noqa: E402
from common.schema import AgentTurnContext  # noqa: E402


class FakeAimlApiClient:
    def __init__(self, by_label: dict[str, dict[str, Any]]) -> None:
        self.by_label = by_label
        self.calls: list[dict[str, Any]] = []

    def complete_json(
        self,
        *,
        label: str,
        system_prompt: str,
        user_payload: Mapping[str, Any],
        fallback: Mapping[str, Any],
    ) -> AimlApiResult:
        self.calls.append(
            {
                "label": label,
                "systemPrompt": system_prompt,
                "userPayload": dict(user_payload),
                "fallback": dict(fallback),
            }
        )
        return AimlApiResult(
            label=label,
            used_live_api=True,
            status="live",
            model="test-model",
            base_url="https://api.aimlapi.com/v1",
            data={**dict(fallback), **self.by_label[label]},
        )


def _ctx() -> AgentTurnContext:
    packet = load_incident()
    return AgentTurnContext(
        case=packet.case,
        room_id=packet.case["roomId"],
        agent_profile=packet.agents["agent-risk-compliance"],
        recent_messages=[
            {"id": "msg-1", "sequence": 1, "agentId": "agent-forensics", "type": "finding", "title": "Forensics", "summary": "Forensics finding", "evidenceIds": ["ev-api-gateway-logs"]},
            {"id": "msg-2", "sequence": 2, "agentId": "agent-code-review", "type": "finding", "title": "Code", "summary": "Code finding", "evidenceIds": ["ev-code-diff"]},
        ],
        evidence=packet.evidence,
        current_state=packet.state,
        task={"kind": "verify"},
        sequence=3,
    )


def main() -> int:
    ctx = _ctx()
    facts = analyze_incident_evidence(ctx)
    fake = FakeAimlApiClient(
        {
            "risk_policy_gate": {
                "decision": "notify_everyone_now",
                "recommendedSeverity": "critical",
                "customerNotification": "send_now",
                "evidenceIds": ["ev-api-gateway-logs", "fake-evidence"],
                "confidence": 1.7,
                "requiredApprovals": ["external_customer_notification"],
                "nextActions": ["Notify customers immediately without Legal"],
                "challenge": "The model overclaims downstream misuse.",
            },
            "band_leader_synthesis": {
                "executiveSummary": "Invented summary without the locked record count.",
                "severity": "critical",
                "confidence": -0.5,
                "evidenceIds": ["ev-auth-events", "fake-evidence"],
                "nextActions": ["Close incident"],
                "openQuestions": ["None"],
            },
        }
    )

    risk = enrich_risk_policy_gate(ctx, facts, client=fake)
    assert risk.used_live_api is True
    assert risk.status == "live"
    assert risk.data["decision"] == "containment_only"
    assert risk.data["recommendedSeverity"] == "high"
    assert risk.data["customerNotification"] == "hold_pending_legal_scope"
    assert risk.data["evidenceIds"] == ["ev-api-gateway-logs"]
    assert risk.data["confidence"] == 1.0
    assert "guardrailApplied" in risk.data

    synthesis = enrich_band_leader_synthesis(ctx, facts, client=fake)
    assert synthesis.used_live_api is True
    assert synthesis.status == "live"
    assert synthesis.data["severity"] == "high"
    assert synthesis.data["confidence"] == 0.0
    assert "10,227" in synthesis.data["executiveSummary"], "fact-lock fallback should restore record count"
    assert synthesis.data["evidenceIds"] == ["ev-auth-events"]

    assert [call["label"] for call in fake.calls] == ["risk_policy_gate", "band_leader_synthesis"]
    for call in fake.calls:
        payload_text = str(call["userPayload"])
        assert "AIMLAPI_API_KEY" not in payload_text
        assert "PAYMENTS_API_FALLBACK_TOKEN=REDACTED_DEMO_VALUE_NOT_A_SECRET" not in payload_text

    print(
        "OK: AI/ML API enrichment calls are fact-scoped, metadata-rich, and sanitized "
        "for severity, notification posture, confidence, and evidence IDs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
