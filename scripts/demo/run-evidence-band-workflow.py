#!/usr/bin/env python3
"""Run the evidence-driven Sentinel Relay workflow through the Band app routes.

This is the prize-path rehearsal:

1. Load a realistic incident evidence packet.
2. Derive specialist findings from the packet.
3. Use AI/ML API for the Risk policy gate and Band Leader synthesis.
4. Post the resulting collaboration trail through /api/collaboration routes.

The script never prints secret values. It expects the Next.js app to be running
with Band Mode configured from the root .env file.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = ROOT / "data" / "incidents" / "inc-1042"
SCHEMA_VERSION = "0.4.0"
CASE_ID = "INC-1042"
CASE_TITLE = "Possible API Key Exposure After Friday Deploy"


AGENTS: list[dict[str, Any]] = [
    {
        "id": "agent-commander",
        "name": "Band Leader",
        "shortName": "Band Leader",
        "kind": "ai_agent",
        "role": "Case coordination and task routing",
        "responsibility": "Maintains shared Band state, routes handoffs, requests approvals, and synthesizes final status.",
        "capability": "case_command",
        "status": "working",
        "currentTask": "Coordinate evidence-driven findings and maintain the incident state.",
        "allowedDecisions": ["assign tasks", "summarize state", "request human approval", "generate report when ready"],
        "requiresHumanApprovalFor": ["production containment", "external customer notification", "closing incident"],
    },
    {
        "id": "agent-forensics",
        "name": "Forensics Agent",
        "shortName": "Forensics",
        "kind": "ai_agent",
        "role": "Log analysis and evidence timeline",
        "responsibility": "Reviews auth and API gateway logs, extracts suspicious activity, and submits evidence-backed timeline events.",
        "capability": "log_forensics",
        "status": "working",
        "currentTask": "Parse API/auth/cloud logs for suspicious token use.",
        "allowedDecisions": ["submit evidence-backed findings", "build timeline events", "request indicator verification"],
        "requiresHumanApprovalFor": ["declaring customer impact", "revoking production credentials"],
    },
    {
        "id": "agent-threat-intel",
        "name": "Threat Intel Agent",
        "shortName": "Threat Intel",
        "kind": "ai_agent",
        "role": "Indicator and behavior assessment",
        "responsibility": "Evaluates suspicious IPs, user agents, token behavior, and confidence signals without overstating weak indicators.",
        "capability": "threat_assessment",
        "status": "working",
        "currentTask": "Assess source IP and behavior confidence.",
        "allowedDecisions": ["assess indicator confidence", "lower or raise confidence", "flag weak evidence"],
        "requiresHumanApprovalFor": ["declaring breach scope", "notifying customers"],
    },
    {
        "id": "agent-code-review",
        "name": "Code Review Agent",
        "shortName": "Code Review",
        "kind": "ai_agent",
        "role": "Deployment and config review",
        "responsibility": "Inspects recent diffs and configuration changes to determine whether code exposed a credential path.",
        "capability": "code_review",
        "status": "working",
        "currentTask": "Inspect Friday deploy diff and scanner output.",
        "allowedDecisions": ["identify risky diff", "propose fix", "create remediation checklist"],
        "requiresHumanApprovalFor": ["merging production code", "rotating live secrets"],
    },
    {
        "id": "agent-risk-compliance",
        "name": "Risk & Compliance Agent",
        "shortName": "Risk",
        "kind": "ai_agent",
        "role": "Policy review, challenge, and escalation",
        "responsibility": "Checks policy, challenges unsupported conclusions, and determines what requires human approval.",
        "capability": "risk_compliance",
        "status": "challenging",
        "currentTask": "Use policy and AI/ML API review to challenge or approve next steps.",
        "allowedDecisions": ["challenge unsupported claims", "classify policy requirement", "recommend escalation"],
        "requiresHumanApprovalFor": ["external notification", "legal/comms disclosure", "closing incident as resolved"],
    },
    {
        "id": "agent-remediation",
        "name": "Remediation Agent",
        "shortName": "Remediation",
        "kind": "ai_agent",
        "role": "Containment and fix planning",
        "responsibility": "Generates containment steps, fix checklist, test criteria, and a PR-ready remediation summary.",
        "capability": "remediation",
        "status": "waiting",
        "currentTask": "Wait for approval before marking containment work approved.",
        "allowedDecisions": ["draft remediation plan", "create acceptance criteria", "prepare PR summary"],
        "requiresHumanApprovalFor": ["executing production containment", "invalidating live credentials without approval"],
    },
]


@dataclass
class PartnerResult:
    label: str
    used: bool
    status: str
    model: str
    base_url: str
    data: dict[str, Any]
    error: str | None = None

    def metadata(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "provider": "AI/ML API",
            "used": self.used,
            "status": self.status,
            "model": self.model,
            "baseUrl": self.base_url,
            "label": self.label,
        }
        if self.error:
            result["error"] = self.error
        return result


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].strip()
        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        value = raw_value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no} is not valid JSONL: {exc}") from exc
    return rows


def json_dumps(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def compact_list(values: list[Any], limit: int = 5) -> list[Any]:
    return values[:limit] + ([f"... {len(values) - limit} more"] if len(values) > limit else [])


class AppClient:
    def __init__(self, app_url: str, timeout: int) -> None:
        self.base = app_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str) -> dict[str, Any]:
        return self._request("GET", path)

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", path, payload)

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base}/api/collaboration{path}",
            data=data,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            try:
                parsed = json.loads(body) if body else {}
            except json.JSONDecodeError:
                parsed = {"error": body}
            raise RuntimeError(f"{method} {path} failed with HTTP {exc.code}: {json_dumps(parsed)}") from exc
        except URLError as exc:
            raise RuntimeError(
                f"Cannot reach Sentinel Relay app at {self.base}. Start it with: corepack pnpm dev"
            ) from exc


class AimlApiClient:
    def __init__(self, *, disabled: bool, require_live: bool, timeout: int) -> None:
        self.disabled = disabled
        self.require_live = require_live
        self.timeout = timeout
        self.api_key = os.environ.get("AIMLAPI_API_KEY", "").strip()
        self.base_url = os.environ.get("AIMLAPI_BASE_URL", "https://api.aimlapi.com/v1").strip().rstrip("/")
        self.model = os.environ.get("AIMLAPI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"

    def complete_json(
        self,
        *,
        label: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        fallback: dict[str, Any],
    ) -> PartnerResult:
        if self.disabled:
            return PartnerResult(label, False, "skipped_by_flag", self.model, self.base_url, fallback)

        if not self.api_key:
            if self.require_live:
                raise RuntimeError("AIMLAPI_API_KEY is required for this run, but it is not set.")
            return PartnerResult(label, False, "missing_api_key_fallback", self.model, self.base_url, fallback)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json_dumps(user_payload)},
            ],
            "temperature": 0.2,
            "max_tokens": 900,
        }
        request = Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "SentinelRelayHackathon/0.1 (+https://github.com/Caleb-Todd-commits/sentinel-relay)",
            },
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            error = self._read_error(exc)
            if self.require_live:
                raise RuntimeError(f"AI/ML API {label} call failed with HTTP {exc.code}: {error}") from exc
            return PartnerResult(label, False, f"http_{exc.code}_fallback", self.model, self.base_url, fallback, error)
        except URLError as exc:
            if self.require_live:
                raise RuntimeError(f"AI/ML API {label} call failed: {exc}") from exc
            return PartnerResult(label, False, "network_fallback", self.model, self.base_url, fallback, str(exc))

        content = self._extract_content(raw)
        parsed = self._parse_model_json(content)
        if parsed is None:
            if self.require_live:
                raise RuntimeError(f"AI/ML API {label} did not return parseable JSON.")
            return PartnerResult(label, True, "unparseable_json_fallback", self.model, self.base_url, fallback)

        merged = {**fallback, **parsed}
        return PartnerResult(label, True, "live", self.model, self.base_url, merged)

    @staticmethod
    def _read_error(exc: HTTPError) -> str:
        body = exc.read().decode("utf-8")
        if not body:
            return "empty error response"
        try:
            parsed = json.loads(body)
            return parsed.get("error", parsed.get("message", json.dumps(parsed))) if isinstance(parsed, dict) else str(parsed)
        except json.JSONDecodeError:
            return body[:500]

    @staticmethod
    def _extract_content(raw: dict[str, Any]) -> str:
        choices = raw.get("choices")
        if not choices:
            return ""
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, list):
            return "\n".join(str(part.get("text", part)) if isinstance(part, dict) else str(part) for part in content)
        return str(content)

    @staticmethod
    def _parse_model_json(content: str) -> dict[str, Any] | None:
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


def load_evidence(evidence_dir: Path) -> dict[str, Any]:
    manifest = read_json(evidence_dir / "evidence_manifest.json")
    return {
        "manifest": manifest,
        "api_logs": read_jsonl(evidence_dir / "api_gateway_logs.jsonl"),
        "auth_events": read_jsonl(evidence_dir / "auth_events.jsonl"),
        "cloudtrail_events": read_jsonl(evidence_dir / "cloudtrail_events.jsonl"),
        "git_diff": (evidence_dir / "git_diff.patch").read_text(),
        "secret_scan": read_json(evidence_dir / "secret_scan.json"),
        "ip_intel": read_json(evidence_dir / "suspicious_ips.json"),
        "policy": read_json(evidence_dir / "incident_policy.json"),
    }


def build_forensics_finding(evidence: dict[str, Any]) -> dict[str, Any]:
    api_logs = evidence["api_logs"]
    auth_events = evidence["auth_events"]
    unexpected_ips = {
        item["ip"]
        for item in evidence["ip_intel"]["indicators"]
        if item["classification"].startswith("unexpected")
    }
    suspicious_requests = [
        row
        for row in api_logs
        if row["source_ip"] in unexpected_ips or "fallback_token" in row.get("risk_flags", [])
    ]
    successful_suspicious = [row for row in suspicious_requests if row["status"] == 200]
    records_returned = sum(int(row.get("records_returned", 0)) for row in successful_suspicious)
    endpoints = sorted({row["endpoint"].split("?")[0] for row in successful_suspicious})
    source_ips = sorted({row["source_ip"] for row in suspicious_requests})
    denied_after_rotation = [
        row for row in suspicious_requests if row["status"] in (401, 403) or "post_rotation_attempt" in row.get("risk_flags", [])
    ]
    fallback_auth_events = [
        event for event in auth_events if event.get("token_id") == "svc-payments-fallback-redacted"
    ]

    return {
        "claim": (
            f"The fallback service token was used from {len(source_ips)} unexpected source IPs. "
            f"Successful suspicious requests returned {records_returned} customer records before rotation."
        ),
        "summary": (
            f"Parsed {len(api_logs)} API gateway rows and {len(auth_events)} auth events. "
            f"The spike starts at {suspicious_requests[0]['timestamp']} and includes "
            f"{len(successful_suspicious)} successful suspicious reads across {', '.join(endpoints)}. "
            f"Rotation is reflected by {len(denied_after_rotation)} denied or post-rotation attempts."
        ),
        "confidence": 0.88,
        "severity": "high",
        "evidenceIds": ["ev-api-gateway-logs", "ev-auth-events", "ev-ip-intel"],
        "supportingEvidenceIds": ["ev-api-gateway-logs", "ev-auth-events"],
        "contradictingEvidenceIds": [],
        "limitations": [
            "Logs show records returned to a suspicious token session, but do not prove the actor's legal identity.",
            "IP intelligence is synthetic medium-confidence demo data and should not be treated as attribution.",
        ],
        "requestedVerifications": [
            "Have Code Review confirm whether the fallback token path was introduced by the Friday deploy.",
            "Have Risk & Compliance decide whether suspected exposure is enough for external notification.",
        ],
        "metrics": {
            "apiLogRows": len(api_logs),
            "authEvents": len(auth_events),
            "unexpectedSourceIps": source_ips,
            "successfulSuspiciousReads": len(successful_suspicious),
            "recordsReturned": records_returned,
            "fallbackAuthEvents": len(fallback_auth_events),
            "deniedAfterRotation": len(denied_after_rotation),
        },
    }


def build_code_review_finding(evidence: dict[str, Any]) -> dict[str, Any]:
    diff = evidence["git_diff"]
    secret_findings = evidence["secret_scan"].get("findings", [])
    risky_tokens = [
        "ALLOW_FALLBACK_TOKEN",
        "PAYMENTS_API_FALLBACK_TOKEN",
        "customer_records_using_fallback_token",
    ]
    present_tokens = [token for token in risky_tokens if token in diff]
    unresolved_secret_findings = [finding for finding in secret_findings if finding.get("status") != "resolved"]

    return {
        "claim": (
            "The Friday deploy created a fallback-token execution path and shipped a release env file that can carry "
            "the fallback token into production."
        ),
        "summary": (
            f"Reviewed the deploy diff and scanner output. Found {len(present_tokens)} risky fallback-token indicators "
            f"and {len(unresolved_secret_findings)} unresolved high-severity scanner finding."
        ),
        "confidence": 0.9,
        "severity": "high",
        "evidenceIds": ["ev-code-diff", "ev-secret-scan", "ev-cloudtrail-events"],
        "supportingEvidenceIds": ["ev-code-diff", "ev-secret-scan"],
        "contradictingEvidenceIds": [],
        "limitations": [
            "The sample value is redacted, so the diff proves the exposure path rather than a usable credential.",
            "A production deploy audit confirms the setting was enabled, but not who obtained the token."
        ],
        "requestedVerifications": [
            "Remove the fallback path and deploy a fail-closed token lookup.",
            "Require human approval before rotating production credentials."
        ],
        "metrics": {
            "riskyDiffIndicators": present_tokens,
            "secretScannerFindings": len(secret_findings),
            "unresolvedSecretScannerFindings": len(unresolved_secret_findings),
        },
    }


def build_threat_intel_finding(evidence: dict[str, Any], forensics: dict[str, Any]) -> dict[str, Any]:
    indicators = evidence["ip_intel"]["indicators"]
    unexpected = [item for item in indicators if item["classification"].startswith("unexpected")]
    api_logs = evidence["api_logs"]
    user_agents = sorted({row["user_agent"] for row in api_logs if row["source_ip"] in {item["ip"] for item in unexpected}})

    return {
        "claim": (
            "The suspicious activity is behaviorally credible but should remain medium-confidence attribution: two "
            "unexpected sources used command-line clients and one probed a canary path."
        ),
        "summary": (
            f"Assessed {len(indicators)} indicators. {len(unexpected)} unexpected sources align with the "
            f"Forensics spike and used {', '.join(user_agents)} instead of the expected payments worker."
        ),
        "confidence": 0.74,
        "severity": "high",
        "evidenceIds": ["ev-ip-intel", "ev-api-gateway-logs", "ev-auth-events"],
        "supportingEvidenceIds": ["ev-ip-intel", "ev-api-gateway-logs"],
        "contradictingEvidenceIds": [],
        "limitations": [
            "Documentation-range IPs make this safe demo evidence; do not claim real-world threat actor attribution.",
            "The behavior supports suspicious use, not confirmed identity or intent."
        ],
        "requestedVerifications": [
            "Correlate egress, WAF, and CDN logs for the same request IDs.",
            "Keep severity high until token rotation and export throttling are verified."
        ],
        "metrics": {
            "indicatorCount": len(indicators),
            "unexpectedIndicatorCount": len(unexpected),
            "observedUnexpectedUserAgents": user_agents,
            "recordsReturnedFromForensics": forensics["metrics"]["recordsReturned"],
        },
    }


def policy_gate_fallback(forensics: dict[str, Any], code_review: dict[str, Any], threat_intel: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision": "approve_containment_only",
        "challenge": "Do not make an external customer notification yet. The evidence supports suspected exposure and urgent containment, but customer-impact scope still needs legal review.",
        "recommendedSeverity": "high",
        "customerNotification": "defer",
        "requiredApprovals": ["Security Lead approval for token rotation", "Legal approval before external notification"],
        "nextActions": [
            "Approve credential rotation and temporary customer export throttling.",
            "Preserve request IDs and downstream access logs for customer-impact scoping.",
            "Ask Remediation to remove the fallback token path and prepare a fail-closed patch."
        ],
        "evidenceIds": sorted(set(forensics["evidenceIds"] + code_review["evidenceIds"] + threat_intel["evidenceIds"] + ["ev-incident-policy"])),
        "confidence": 0.82,
    }


def synthesis_fallback(
    forensics: dict[str, Any],
    code_review: dict[str, Any],
    threat_intel: dict[str, Any],
    policy_gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "executiveSummary": (
            "Sentinel Relay found a likely fallback-token exposure path tied to the Friday deploy. "
            f"Forensics counted {forensics['metrics']['recordsReturned']} records returned through suspicious reads. "
            "Risk & Compliance recommends containment now and customer notification only after scope verification."
        ),
        "recommendedDecision": policy_gate.get("decision", "approve_containment_only"),
        "severity": policy_gate.get("recommendedSeverity", "high"),
        "confidence": policy_gate.get("confidence", 0.82),
        "evidenceIds": policy_gate.get("evidenceIds", []),
        "nextActions": policy_gate.get("nextActions", []),
        "openQuestions": [
            "Which customer records map to the returned export rows?",
            "Did downstream systems cache or forward the exported records?",
            "Does Legal require customer notification after scope is verified?"
        ],
        "bandCoordinationValue": (
            "Band kept specialist findings, risk challenge, approval, remediation status, and final synthesis in one shared room."
        ),
    }


def call_policy_gate(
    aiml: AimlApiClient,
    evidence: dict[str, Any],
    forensics: dict[str, Any],
    code_review: dict[str, Any],
    threat_intel: dict[str, Any],
) -> PartnerResult:
    fallback = policy_gate_fallback(forensics, code_review, threat_intel)
    return aiml.complete_json(
        label="risk_policy_gate",
        system_prompt=(
            "You are the Sentinel Relay Risk & Compliance agent. Return only JSON. "
            "Challenge unsupported breach claims, cite evidence IDs, and decide whether containment, "
            "credential rotation, and external customer notification can proceed under policy. "
            "Never invent evidence and never include secret values."
        ),
        user_payload={
            "caseId": CASE_ID,
            "policy": evidence["policy"],
            "forensicsFinding": forensics,
            "codeReviewFinding": code_review,
            "threatIntelFinding": threat_intel,
            "requiredJsonFields": [
                "decision",
                "challenge",
                "recommendedSeverity",
                "customerNotification",
                "requiredApprovals",
                "nextActions",
                "evidenceIds",
                "confidence",
            ],
        },
        fallback=fallback,
    )


def call_band_leader_synthesis(
    aiml: AimlApiClient,
    *,
    snapshot_summary: dict[str, Any],
    forensics: dict[str, Any],
    code_review: dict[str, Any],
    threat_intel: dict[str, Any],
    policy_gate: PartnerResult,
) -> PartnerResult:
    fallback = synthesis_fallback(forensics, code_review, threat_intel, policy_gate.data)
    return aiml.complete_json(
        label="band_leader_synthesis",
        system_prompt=(
            "You are Sentinel Relay's Band Leader. Return only JSON. "
            "Synthesize the multi-agent investigation for a judge-facing enterprise incident room. "
            "Be concrete, cite evidence IDs, include what Band coordinated, and do not overclaim."
        ),
        user_payload={
            "caseId": CASE_ID,
            "bandRoomSnapshot": snapshot_summary,
            "forensicsFinding": forensics,
            "codeReviewFinding": code_review,
            "threatIntelFinding": threat_intel,
            "policyGate": policy_gate.data,
            "requiredJsonFields": [
                "executiveSummary",
                "recommendedDecision",
                "severity",
                "confidence",
                "evidenceIds",
                "nextActions",
                "openQuestions",
                "bandCoordinationValue",
            ],
        },
        fallback=fallback,
    )


def make_message(
    *,
    room_id: str,
    sequence: int,
    agent_id: str,
    agent_name: str,
    message_type: str,
    title: str,
    summary: str,
    confidence: float,
    severity: str,
    evidence_ids: list[str],
    target_agent_ids: list[str],
    decision_impact: str,
    next_action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": f"msg-evidence-{sequence:03d}",
        "schemaVersion": SCHEMA_VERSION,
        "caseId": CASE_ID,
        "roomId": room_id,
        "sequence": sequence,
        "agentId": agent_id,
        "agentName": agent_name,
        "type": message_type,
        "title": title,
        "summary": summary,
        "confidence": confidence,
        "severity": severity,
        "evidenceIds": evidence_ids,
        "targetAgentIds": target_agent_ids,
        "createdAt": now_iso(),
        "visibility": "judge_demo",
        "decisionImpact": decision_impact,
        "nextAction": next_action,
        "correlationId": f"trace-inc-1042-evidence-{sequence:03d}",
        "payload": payload,
    }


def finding_payload(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "finding",
        "data": {
            "claim": finding["claim"],
            "supportingEvidenceIds": finding["supportingEvidenceIds"],
            "contradictingEvidenceIds": finding["contradictingEvidenceIds"],
            "limitations": finding["limitations"],
            "requestedVerifications": finding["requestedVerifications"],
        },
    }


def snapshot_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "registeredAgents": len(snapshot.get("registeredAgents", [])),
        "messages": len(snapshot.get("messages", [])),
        "approvalRequests": len(snapshot.get("approvalRequests", [])),
        "approvalDecisions": len(snapshot.get("approvalDecisions", [])),
        "taskStatuses": len(snapshot.get("taskStatuses", [])),
        "auditEvents": len(snapshot.get("auditEvents", [])),
        "remoteWarnings": len(snapshot.get("remoteWarnings", [])),
        "latestMessageIds": [message.get("id") for message in snapshot.get("messages", [])[-5:]],
    }


def post_message(client: AppClient, room_id: str, message: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/messages", {"action": "sendMessage", "roomId": room_id, "message": message})
    snapshot = response.get("snapshot")
    if not snapshot:
        raise RuntimeError(f"Message {message['id']} did not return a room snapshot.")
    return snapshot


def register_agents(client: AppClient, room_id: str) -> None:
    timestamp = now_iso()
    for profile in AGENTS:
        client.post(
            "/rooms",
            {
                "action": "registerAgent",
                "roomId": room_id,
                "agent": {**profile, "createdAt": timestamp},
            },
        )


def run_workflow(args: argparse.Namespace) -> dict[str, Any]:
    load_dotenv(ROOT / ".env")
    evidence_dir = Path(args.evidence_dir).resolve()
    evidence = load_evidence(evidence_dir)
    aiml = AimlApiClient(disabled=args.skip_aimlapi, require_live=args.require_aimlapi, timeout=args.timeout)
    app = AppClient(args.app_url, args.timeout)

    health = app.get("/health?live=false")
    if health.get("status") not in ("configured", "ready"):
        raise RuntimeError(f"Band app routes are not configured: {json_dumps(health)}")

    room = app.post(
        "/rooms",
        {
            "action": "createIncidentRoom",
            "input": {
                "caseId": CASE_ID,
                "title": f"{CASE_TITLE} - evidence run",
                "requestedBy": "evidence-workflow-runner",
            },
        },
    )
    room_id = room["id"]
    register_agents(app, room_id)

    forensics = build_forensics_finding(evidence)
    code_review = build_code_review_finding(evidence)
    threat_intel = build_threat_intel_finding(evidence, forensics)

    snapshot = post_message(
        app,
        room_id,
        make_message(
            room_id=room_id,
            sequence=1,
            agent_id="agent-commander",
            agent_name="Band Leader",
            message_type="task_assignment",
            title="Evidence packet assigned to specialist agents",
            summary=(
                "Band Leader opened an evidence-driven investigation and assigned logs, code diff, "
                "indicator review, policy review, and remediation planning to specialist agents."
            ),
            confidence=1.0,
            severity="high",
            evidence_ids=[item["id"] for item in evidence["manifest"]["evidence"]],
            target_agent_ids=["agent-forensics", "agent-code-review", "agent-threat-intel", "agent-risk-compliance"],
            decision_impact="Starts the shared Band room trail from a concrete evidence packet.",
            next_action="Specialist agents derive findings from their assigned evidence.",
            payload={
                "kind": "generic",
                "data": {
                    "evidenceManifest": "data/incidents/inc-1042/evidence_manifest.json",
                    "assignedEvidenceIds": [item["id"] for item in evidence["manifest"]["evidence"]],
                },
            },
        ),
    )

    snapshot = post_message(
        app,
        room_id,
        make_message(
            room_id=room_id,
            sequence=2,
            agent_id="agent-forensics",
            agent_name="Forensics Agent",
            message_type="finding",
            title="Suspicious fallback-token reads found in API logs",
            summary=forensics["summary"],
            confidence=forensics["confidence"],
            severity=forensics["severity"],
            evidence_ids=forensics["evidenceIds"],
            target_agent_ids=["agent-commander", "agent-threat-intel", "agent-risk-compliance"],
            decision_impact="Shows the suspicious access pattern and record volume that drive containment urgency.",
            next_action="Threat Intel should assess the indicators; Risk should evaluate notification and approval posture.",
            payload=finding_payload(forensics),
        ),
    )

    snapshot = post_message(
        app,
        room_id,
        make_message(
            room_id=room_id,
            sequence=3,
            agent_id="agent-code-review",
            agent_name="Code Review Agent",
            message_type="finding",
            title="Friday deploy introduced a fallback-token exposure path",
            summary=code_review["summary"],
            confidence=code_review["confidence"],
            severity=code_review["severity"],
            evidence_ids=code_review["evidenceIds"],
            target_agent_ids=["agent-commander", "agent-risk-compliance", "agent-remediation"],
            decision_impact="Links the suspicious runtime behavior to a concrete deployment and fix path.",
            next_action="Risk should require approval for credential rotation; Remediation should remove the fallback path.",
            payload=finding_payload(code_review),
        ),
    )

    snapshot = post_message(
        app,
        room_id,
        make_message(
            room_id=room_id,
            sequence=4,
            agent_id="agent-threat-intel",
            agent_name="Threat Intel Agent",
            message_type="finding",
            title="Indicator confidence supports urgency but not attribution",
            summary=threat_intel["summary"],
            confidence=threat_intel["confidence"],
            severity=threat_intel["severity"],
            evidence_ids=threat_intel["evidenceIds"],
            target_agent_ids=["agent-commander", "agent-risk-compliance", "agent-forensics"],
            decision_impact="Keeps the response evidence-based by separating behavior confidence from actor attribution.",
            next_action="Risk should challenge overbroad breach claims and approve containment-focused action.",
            payload=finding_payload(threat_intel),
        ),
    )

    policy_gate = call_policy_gate(aiml, evidence, forensics, code_review, threat_intel)
    gate_data = policy_gate.data
    source_message_ids = [message.get("id") for message in snapshot.get("messages", [])]
    snapshot = post_message(
        app,
        room_id,
        make_message(
            room_id=room_id,
            sequence=5,
            agent_id="agent-risk-compliance",
            agent_name="Risk & Compliance Agent",
            message_type="challenge",
            title="Policy gate blocks customer notification but approves containment request",
            summary=str(gate_data.get("challenge", policy_gate_fallback(forensics, code_review, threat_intel)["challenge"])),
            confidence=float(gate_data.get("confidence", 0.82)),
            severity=str(gate_data.get("recommendedSeverity", "high")),
            evidence_ids=list(gate_data.get("evidenceIds", ["ev-incident-policy"])),
            target_agent_ids=["agent-commander", "agent-remediation", "agent-code-review"],
            decision_impact="Prevents an unsupported external notification while preserving urgent containment momentum.",
            next_action="Request human approval for token rotation and temporary export throttling.",
            payload={
                "kind": "generic",
                "data": {
                    "challenge": {
                        "requiredNextStep": "Approve containment, defer external notification, and preserve evidence for scope review.",
                        "blocking": True,
                        "suggestedOwnerAgentId": "agent-remediation",
                    },
                    "policyGate": gate_data,
                    "sourceMessageIds": source_message_ids,
                    "partnerTool": policy_gate.metadata(),
                },
            },
        ),
    )

    approval_request = {
        "id": "approval-inc-1042-containment",
        "caseId": CASE_ID,
        "requestedByAgentId": "agent-risk-compliance",
        "action": "Rotate the fallback token, disable the fallback path, and temporarily throttle customer export endpoints.",
        "reason": "Evidence supports likely credential exposure and suspicious customer-data reads, but policy requires human approval for production containment.",
        "severity": "high",
        "evidenceIds": list(gate_data.get("evidenceIds", ["ev-api-gateway-logs", "ev-code-diff", "ev-incident-policy"])),
        "riskIfApproved": "Temporary export disruption and credential-rotation coordination overhead.",
        "riskIfRejected": "The suspected exposed credential path may remain usable and customer-data exports may continue.",
        "requiredApprover": "Security Lead",
        "status": "pending",
        "createdAt": now_iso(),
    }
    snapshot = app.post(
        "/approvals",
        {
            "action": "requestHumanApproval",
            "roomId": room_id,
            "request": approval_request,
        },
    )["snapshot"]

    approval_decision = {
        "id": "decision-inc-1042-containment",
        "requestId": approval_request["id"],
        "decision": "approved",
        "decidedBy": "Human Security Lead",
        "rationale": "Approve containment and credential rotation now; explicitly defer customer notification until scope and Legal review are complete.",
        "decidedAt": now_iso(),
        "approvedActionScope": [
            "Rotate fallback token and production service credential.",
            "Disable fallback token path in production.",
            "Temporarily throttle customer export endpoint while scope is reviewed.",
        ],
        "explicitlyNotApproved": [
            "External customer notification.",
            "Closing the incident.",
            "Public breach attribution."
        ],
    }
    snapshot = app.post(
        "/approvals",
        {
            "action": "submitHumanDecision",
            "roomId": room_id,
            "decision": approval_decision,
        },
    )["snapshot"]

    remediation_tasks = [
        {
            "taskId": "rem-rotate-fallback-token",
            "status": "done",
            "evidenceIds": ["ev-auth-events", "ev-cloudtrail-events", "ev-incident-policy"],
            "acceptanceCriteria": ["Old fallback token returns 401.", "New token is stored only in the managed secret store."],
        },
        {
            "taskId": "rem-remove-fallback-path",
            "status": "review",
            "evidenceIds": ["ev-code-diff", "ev-secret-scan"],
            "acceptanceCriteria": ["Token lookup fails closed.", "Release env file no longer contains fallback token variables."],
        },
        {
            "taskId": "rem-scope-customer-impact",
            "status": "in_progress",
            "evidenceIds": ["ev-api-gateway-logs", "ev-auth-events"],
            "acceptanceCriteria": ["Returned record IDs mapped to accounts.", "Legal-ready customer-impact summary created."],
        },
    ]
    for task in remediation_tasks:
        snapshot = app.post(
            "/messages",
            {
                "action": "updateTaskStatus",
                "roomId": room_id,
                "taskId": task["taskId"],
                "status": task["status"],
            },
        )["snapshot"]

    snapshot = post_message(
        app,
        room_id,
        make_message(
            room_id=room_id,
            sequence=6,
            agent_id="agent-remediation",
            agent_name="Remediation Agent",
            message_type="remediation_task",
            title="Containment plan started after human approval",
            summary=(
                "Credential rotation is marked done, fail-closed code changes are in review, and customer-impact scoping remains in progress."
            ),
            confidence=0.86,
            severity="high",
            evidence_ids=["ev-auth-events", "ev-cloudtrail-events", "ev-code-diff", "ev-incident-policy"],
            target_agent_ids=["agent-commander", "agent-risk-compliance", "agent-code-review"],
            decision_impact="Turns the approval decision into trackable remediation state in the Band room.",
            next_action="Band Leader should synthesize final judge-facing status and open questions.",
            payload={
                "kind": "generic",
                "data": {
                    "tasks": remediation_tasks,
                    "approvalDecisionId": approval_decision["id"],
                },
            },
        ),
    )

    synthesis = call_band_leader_synthesis(
        aiml,
        snapshot_summary=snapshot_summary(snapshot),
        forensics=forensics,
        code_review=code_review,
        threat_intel=threat_intel,
        policy_gate=policy_gate,
    )
    synthesis_data = synthesis.data
    executive_summary = str(synthesis_data.get("executiveSummary", synthesis_fallback(forensics, code_review, threat_intel, gate_data)["executiveSummary"]))
    snapshot = post_message(
        app,
        room_id,
        make_message(
            room_id=room_id,
            sequence=7,
            agent_id="agent-commander",
            agent_name="Band Leader",
            message_type="report_section",
            title="AI/ML API synthesized the Band room into a judge-ready incident status",
            summary=executive_summary,
            confidence=float(synthesis_data.get("confidence", 0.82)),
            severity=str(synthesis_data.get("severity", "high")),
            evidence_ids=list(synthesis_data.get("evidenceIds", gate_data.get("evidenceIds", []))),
            target_agent_ids=["agent-forensics", "agent-threat-intel", "agent-code-review", "agent-risk-compliance", "agent-remediation"],
            decision_impact="Shows partner-powered cross-agent reasoning over Band-shared context.",
            next_action="Use the final status, approvals, and open questions in the video and submission narrative.",
            payload={
                "kind": "generic",
                "data": {
                    "synthesis": synthesis_data,
                    "partnerTool": synthesis.metadata(),
                    "policyGatePartnerTool": policy_gate.metadata(),
                    "bandSnapshotSummary": snapshot_summary(snapshot),
                },
            },
        ),
    )

    summary = snapshot_summary(snapshot)
    return {
        "caseId": CASE_ID,
        "roomId": room_id,
        "evidenceDir": str(evidence_dir.relative_to(ROOT)),
        "messagesPosted": summary["messages"],
        "registeredAgents": summary["registeredAgents"],
        "approvalRequests": summary["approvalRequests"],
        "approvalDecisions": summary["approvalDecisions"],
        "taskStatuses": summary["taskStatuses"],
        "auditEvents": summary["auditEvents"],
        "remoteWarnings": summary["remoteWarnings"],
        "recordsReturnedBySuspiciousReads": forensics["metrics"]["recordsReturned"],
        "aimlapi": {
            "model": aiml.model,
            "baseUrl": aiml.base_url,
            "policyGate": policy_gate.metadata(),
            "bandLeaderSynthesis": synthesis.metadata(),
        },
        "latestMessageIds": summary["latestMessageIds"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the evidence-driven Band workflow.")
    parser.add_argument("--app-url", default=os.environ.get("SENTINEL_RELAY_APP_URL", "http://127.0.0.1:3000"))
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--skip-aimlapi", action="store_true", help="Use deterministic fallbacks instead of AI/ML API calls.")
    parser.add_argument("--require-aimlapi", action="store_true", help="Fail if AI/ML API cannot be called live.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = run_workflow(args)
    except Exception as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    print(json_dumps(result))
    if result["remoteWarnings"]:
        print("WARN Band route remote warnings were recorded; inspect the room snapshot in the running app.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
