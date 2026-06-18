"""Guarded AI/ML API enrichment for Sentinel Relay agents.

The partner-prize path should be meaningful without making the demo fragile:
Risk & Compliance asks AI/ML API to reason over evidence-derived facts as a
policy gate, and Band Leader asks it to synthesize the room trail. The output is
JSON-only, sanitized, and always backed by deterministic fallback data.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from common.evidence_analysis import IncidentEvidenceFacts
from common.schema import AgentTurnContext, SEVERITIES

ALLOWED_EVIDENCE_IDS = {
    "ev-api-gateway-logs",
    "ev-auth-events",
    "ev-cloudtrail-events",
    "ev-code-diff",
    "ev-secret-scan",
    "ev-ip-intel",
    "ev-incident-policy",
}

DEFAULT_BASE_URL = "https://api.aimlapi.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


@dataclass(frozen=True)
class AimlApiResult:
    label: str
    used_live_api: bool
    status: str
    model: str
    base_url: str
    data: dict[str, Any]
    error: str | None = None

    def metadata(self) -> dict[str, Any]:
        return {
            "provider": "AI/ML API",
            "label": self.label,
            "usedLiveApi": self.used_live_api,
            "status": self.status,
            "model": self.model,
            "baseUrl": self.base_url,
            "error": self.error,
        }


class AimlApiClient:
    """Minimal OpenAI-compatible chat-completions client using stdlib only."""

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        require_live: bool | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.enabled = _read_bool("SENTINEL_RELAY_AIMLAPI_ENABLED", default=False) if enabled is None else enabled
        self.require_live = _read_bool("SENTINEL_RELAY_AIMLAPI_REQUIRE_LIVE", default=False) if require_live is None else require_live
        self.timeout_seconds = timeout_seconds or _read_float("AIMLAPI_TIMEOUT_SECONDS", default=20.0)
        self.api_key = _read_env("AIMLAPI_API_KEY")
        self.base_url = (_read_env("AIMLAPI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = _read_env("AIMLAPI_MODEL") or DEFAULT_MODEL
        self.max_tokens = int(_read_float("AIMLAPI_MAX_TOKENS", default=900))

    def complete_json(
        self,
        *,
        label: str,
        system_prompt: str,
        user_payload: Mapping[str, Any],
        fallback: Mapping[str, Any],
    ) -> AimlApiResult:
        fallback_data = dict(fallback)
        if not self.enabled:
            return AimlApiResult(label, False, "disabled_fallback", self.model, self.base_url, fallback_data)

        if not self.api_key:
            if self.require_live:
                raise RuntimeError("AIMLAPI_API_KEY is required because SENTINEL_RELAY_AIMLAPI_REQUIRE_LIVE=true.")
            return AimlApiResult(label, False, "missing_api_key_fallback", self.model, self.base_url, fallback_data)

        request_payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(dict(user_payload), sort_keys=True)},
            ],
            "temperature": 0.1,
            "max_tokens": self.max_tokens,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(request_payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "SentinelRelayHackathon/0.1",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error = _read_http_error(exc)
            if self.require_live:
                raise RuntimeError(f"AI/ML API {label} failed with HTTP {exc.code}: {error}") from exc
            return AimlApiResult(label, False, f"http_{exc.code}_fallback", self.model, self.base_url, fallback_data, error)
        except urllib.error.URLError as exc:
            if self.require_live:
                raise RuntimeError(f"AI/ML API {label} failed: {exc}") from exc
            return AimlApiResult(label, False, "network_fallback", self.model, self.base_url, fallback_data, str(exc))
        except json.JSONDecodeError as exc:
            if self.require_live:
                raise RuntimeError(f"AI/ML API {label} returned invalid JSON response.") from exc
            return AimlApiResult(label, False, "invalid_response_fallback", self.model, self.base_url, fallback_data, str(exc))

        content = _extract_content(raw)
        parsed = _parse_json_object(content)
        if parsed is None:
            if self.require_live:
                raise RuntimeError(f"AI/ML API {label} did not return parseable JSON.")
            return AimlApiResult(label, False, "unparseable_json_fallback", self.model, self.base_url, fallback_data)

        return AimlApiResult(label, True, "live", self.model, self.base_url, {**fallback_data, **parsed})


def enrich_risk_policy_gate(
    ctx: AgentTurnContext,
    facts: IncidentEvidenceFacts,
    *,
    client: AimlApiClient | None = None,
) -> AimlApiResult:
    fallback = _risk_fallback(facts)
    result = (client or AimlApiClient()).complete_json(
        label="risk_policy_gate",
        system_prompt=(
            "You are Sentinel Relay's Risk & Compliance agent. Return only a JSON object. "
            "Use only supplied facts and evidence IDs. Do not invent customers, laws, actors, "
            "secret values, or downstream misuse. Challenge unsupported breach/exfiltration claims. "
            "Keep customer notification held until scope and Legal review are complete."
        ),
        user_payload={
            "case": ctx.case,
            "agentRole": ctx.agent_profile,
            "evidenceFacts": evidence_fact_bundle(facts),
            "recentMessages": message_summary(ctx.recent_messages),
            "requiredFields": list(fallback),
            "allowedEvidenceIds": sorted(ALLOWED_EVIDENCE_IDS),
            "hardConstraints": {
                "customerNotification": "hold_pending_legal_scope",
                "classification": "suspected_exposure",
                "recommendedSeverity": "high",
            },
        },
        fallback=fallback,
    )
    return AimlApiResult(
        result.label,
        result.used_live_api,
        result.status,
        result.model,
        result.base_url,
        sanitize_risk_gate(result.data, facts),
        result.error,
    )


def enrich_band_leader_synthesis(
    ctx: AgentTurnContext,
    facts: IncidentEvidenceFacts,
    *,
    client: AimlApiClient | None = None,
) -> AimlApiResult:
    fallback = _synthesis_fallback(facts)
    result = (client or AimlApiClient()).complete_json(
        label="band_leader_synthesis",
        system_prompt=(
            "You are Sentinel Relay's Band Leader. Return only a JSON object. Synthesize the Band room "
            "for an enterprise incident review. Use only supplied facts and message summaries. Preserve "
            "agent disagreement, cite evidence IDs, and do not overclaim confirmed exfiltration."
        ),
        user_payload={
            "case": ctx.case,
            "evidenceFacts": evidence_fact_bundle(facts),
            "bandRoomTrail": message_summary(ctx.recent_messages),
            "requiredFields": list(fallback),
            "allowedEvidenceIds": sorted(ALLOWED_EVIDENCE_IDS),
            "hardConstraints": {
                "severity": "high",
                "classification": "suspected_exposure",
                "notificationPosture": "held_for_legal_scope",
            },
        },
        fallback=fallback,
    )
    return AimlApiResult(
        result.label,
        result.used_live_api,
        result.status,
        result.model,
        result.base_url,
        sanitize_band_leader_synthesis(result.data, facts),
        result.error,
    )


def evidence_fact_bundle(facts: IncidentEvidenceFacts) -> dict[str, Any]:
    """Small JSON-safe fact bundle for model prompts and payload traceability."""

    return {
        "api": asdict(facts.api),
        "auth": asdict(facts.auth),
        "cloudtrail": asdict(facts.cloudtrail),
        "code": asdict(facts.code),
        "secretScan": asdict(facts.secret_scan),
        "threat": asdict(facts.threat),
        "policy": asdict(facts.policy),
    }


def message_summary(messages: list[Mapping[str, Any]], *, limit: int = 12) -> list[dict[str, Any]]:
    return [
        {
            "id": message.get("id"),
            "sequence": message.get("sequence"),
            "agentId": message.get("agentId"),
            "type": message.get("type"),
            "title": message.get("title"),
            "summary": message.get("summary"),
            "evidenceIds": message.get("evidenceIds", []),
            "targetAgentIds": message.get("targetAgentIds", []),
        }
        for message in messages[-limit:]
    ]


def sanitize_risk_gate(data: Mapping[str, Any], facts: IncidentEvidenceFacts) -> dict[str, Any]:
    fallback = _risk_fallback(facts)
    sanitized = {
        "decision": _choice(data.get("decision"), {"containment_only", "continue_investigation", "escalate_to_human"}, fallback["decision"]),
        "classification": "suspected_exposure",
        "recommendedSeverity": _severity(data.get("recommendedSeverity"), fallback["recommendedSeverity"]),
        "customerNotification": "hold_pending_legal_scope",
        "challenge": _text(data.get("challenge"), fallback["challenge"], max_len=700),
        "requiredApprovals": _string_list(data.get("requiredApprovals")) or fallback["requiredApprovals"],
        "nextActions": _string_list(data.get("nextActions"), limit=6) or fallback["nextActions"],
        "unsupportedClaims": _string_list(data.get("unsupportedClaims"), limit=5) or fallback["unsupportedClaims"],
        "openQuestions": _string_list(data.get("openQuestions"), limit=5) or fallback["openQuestions"],
        "evidenceIds": _evidence_ids(data.get("evidenceIds")) or fallback["evidenceIds"],
        "confidence": _confidence(data.get("confidence"), fallback["confidence"]),
        "reasoningSummary": _text(data.get("reasoningSummary"), fallback["reasoningSummary"], max_len=700),
    }
    if sanitized["recommendedSeverity"] == "critical":
        sanitized["recommendedSeverity"] = "high"
        sanitized["guardrailApplied"] = "Downgraded critical severity because the supplied facts do not prove downstream misuse or inability to contain."
    return sanitized


def sanitize_band_leader_synthesis(data: Mapping[str, Any], facts: IncidentEvidenceFacts) -> dict[str, Any]:
    fallback = _synthesis_fallback(facts)
    executive_summary = _text(data.get("executiveSummary"), fallback["executiveSummary"], max_len=900)
    records_text = f"{facts.api.unauthorized_records_returned:,}"
    if records_text not in executive_summary:
        executive_summary = fallback["executiveSummary"]
    severity = _severity(data.get("severity"), fallback["severity"])
    if severity == "critical":
        severity = "high"
    return {
        "executiveSummary": executive_summary,
        "recommendedDecision": _text(data.get("recommendedDecision"), fallback["recommendedDecision"], max_len=300),
        "severity": severity,
        "confidence": _confidence(data.get("confidence"), fallback["confidence"]),
        "evidenceIds": _evidence_ids(data.get("evidenceIds")) or fallback["evidenceIds"],
        "nextActions": _string_list(data.get("nextActions"), limit=6) or fallback["nextActions"],
        "openQuestions": _string_list(data.get("openQuestions"), limit=6) or fallback["openQuestions"],
        "bandCoordinationValue": _text(data.get("bandCoordinationValue"), fallback["bandCoordinationValue"], max_len=500),
        "dissentToPreserve": _string_list(data.get("dissentToPreserve"), limit=5) or fallback["dissentToPreserve"],
        "judgeDemoMoment": _text(data.get("judgeDemoMoment"), fallback["judgeDemoMoment"], max_len=400),
    }


def _risk_fallback(facts: IncidentEvidenceFacts) -> dict[str, Any]:
    records_text = f"{facts.api.unauthorized_records_returned:,}"
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    return {
        "decision": "containment_only",
        "classification": "suspected_exposure",
        "recommendedSeverity": "high",
        "customerNotification": "hold_pending_legal_scope",
        "challenge": (
            f"Gateway logs show {records_text} records returned to unexpected IPs, so containment is urgent, "
            "but downstream misuse, actor identity, residency scope, and Legal wording are not proven."
        ),
        "requiredApprovals": facts.policy.human_approval_actions,
        "nextActions": (
            [
                "Approve issuer-first federated-session containment.",
                "Hold customer notification pending Legal and customer-scope mapping.",
                "Restore OIDC trust to protected refs and remove export scope from untrusted workflows.",
                "Map exported records to jurisdiction and controller/processor duties.",
            ]
            if is_oidc
            else [
                "Approve issuer-first token containment.",
                "Hold customer notification pending Legal and customer-scope mapping.",
                "Verify sibling Secrets Manager credential rotation.",
                "Map exported records to jurisdiction and controller/processor duties.",
            ]
        ),
        "unsupportedClaims": [
            "Confirmed named threat actor.",
            "Confirmed downstream resale or misuse.",
            "Customer notification ready without Legal scope review.",
        ],
        "openQuestions": [
            "Which exact customers and jurisdictions are in the returned records?",
            "Did downstream systems cache, forward, or expose the returned rows?",
            "Is the OIDC trust boundary fixed and active sessions revoked?"
            if is_oidc
            else "Is the sibling managed credential fully rotated and verified dead?",
        ],
        "evidenceIds": ["ev-incident-policy", "ev-api-gateway-logs", "ev-code-diff", "ev-auth-events"],
        "confidence": 0.88,
        "reasoningSummary": "The evidence supports active unauthorized access and high-severity containment, while policy blocks notification and closure until scope is verified.",
    }


def _synthesis_fallback(facts: IncidentEvidenceFacts) -> dict[str, Any]:
    records_text = f"{facts.api.unauthorized_records_returned:,}"
    opened_at = facts.cloudtrail.deploy_enabled_fallback_at or "unknown"
    closed_at = facts.auth.issuer_verified_inactive_at or facts.api.post_rotation_attempt_at or "unknown"
    ips = ", ".join(facts.api.unauthorized_ips)
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    return {
        "executiveSummary": (
            (
                "Band-coordinated agents traced an OIDC trust-policy regression to a repo-wide wildcard, measured "
                f"{records_text} customer records returned to unexpected IPs ({ips}), and bounded the exposure "
                f"window from {opened_at} to issuer-verified denial at {closed_at}. Risk kept the case at "
                "suspected exposure, approved containment only, and held notification for Legal scope review."
            )
            if is_oidc
            else (
                f"Band-coordinated agents traced an exposed fallback service token to a Friday deploy, measured "
                f"{records_text} customer records returned to unexpected IPs ({ips}), and bounded the exposure "
                f"window from {opened_at} to issuer-verified denial at {closed_at}. Risk kept the case at "
                "suspected exposure, approved containment only, and held notification for Legal scope review."
            )
        ),
        "recommendedDecision": "Proceed with approved containment and evidence preservation; keep notification and closure behind Legal and human approval.",
        "severity": "high",
        "confidence": 0.92,
        "evidenceIds": [
            "ev-api-gateway-logs",
            "ev-auth-events",
            "ev-cloudtrail-events",
            "ev-code-diff",
            "ev-secret-scan",
            "ev-incident-policy",
        ],
        "nextActions": (
            [
                "Complete OIDC trust-policy rollback.",
                "Revoke active federated sessions and remove export scope from untrusted refs.",
                "Map returned records to customer and jurisdiction scope.",
                "Prepare Legal-reviewed notification recommendation.",
            ]
            if is_oidc
            else [
                "Complete sibling credential rotation.",
                "Disable fail-open fallback path and purge release env secret sprawl.",
                "Map returned records to customer and jurisdiction scope.",
                "Prepare Legal-reviewed notification recommendation.",
            ]
        ),
        "openQuestions": [
            "Which exact customer rows and jurisdictions were returned?",
            "Did downstream systems cache or forward the data?",
            "Are all OIDC trust policies limited to protected refs?"
            if is_oidc
            else "Are all CI, deploy, clone, and image copies purged?",
        ],
        "bandCoordinationValue": "Band preserved assignments, specialist findings, Risk challenge, human approval, remediation, and final synthesis as one auditable room trail.",
        "dissentToPreserve": [
            "Forensics proves records returned; Risk refuses to call downstream misuse proven.",
            "Threat Intel says exploitation likely; no real-world actor attribution is supported.",
            "Remediation says the observed token is dead; Code Review still requires OIDC trust rollback."
            if is_oidc
            else "Remediation says fallback is dead; Code Review still requires sibling credential rotation.",
        ],
        "judgeDemoMoment": "The strongest moment is the Risk gate: enough evidence for urgent containment, not enough for autonomous customer notification.",
    }


def _read_env(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


def _read_bool(name: str, *, default: bool) -> bool:
    value = _read_env(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _read_float(name: str, *, default: float) -> float:
    value = _read_env(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _read_http_error(exc: urllib.error.HTTPError) -> str:
    body = exc.read().decode("utf-8", errors="replace")
    if not body:
        return "empty error response"
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return body[:500]
    if isinstance(parsed, dict):
        error = parsed.get("error") or parsed.get("message") or parsed
        return json.dumps(error) if not isinstance(error, str) else error
    return str(parsed)


def _extract_content(raw: Mapping[str, Any]) -> str:
    choices = raw.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, Mapping):
        return ""
    message = first.get("message")
    if not isinstance(message, Mapping):
        return ""
    content = message.get("content", "")
    if isinstance(content, list):
        return "\n".join(
            str(item.get("text", item)) if isinstance(item, Mapping) else str(item)
            for item in content
        )
    return str(content)


def _parse_json_object(content: str) -> dict[str, Any] | None:
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        stripped = "\n".join(lines[1:-1]).strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        parsed = json.loads(stripped[start : end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _text(value: Any, fallback: str, *, max_len: int) -> str:
    text = str(value).strip() if value is not None else ""
    if not text:
        return fallback
    return text[:max_len]


def _string_list(value: Any, *, limit: int = 8) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip()[:240] for item in value if str(item).strip()][:limit]


def _evidence_ids(value: Any) -> list[str]:
    return [item for item in _string_list(value, limit=12) if item in ALLOWED_EVIDENCE_IDS]


def _confidence(value: Any, fallback: float) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return fallback
    return max(0.0, min(1.0, confidence))


def _severity(value: Any, fallback: str) -> str:
    severity = str(value).strip().lower() if value is not None else ""
    return severity if severity in SEVERITIES else fallback


def _choice(value: Any, allowed: set[str], fallback: str) -> str:
    choice = str(value).strip() if value is not None else ""
    return choice if choice in allowed else fallback
