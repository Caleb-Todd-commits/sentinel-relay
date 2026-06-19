"""Two-phase Sentinel Relay agent execution for Vercel's Python runtime."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any


FUNCTION_PATH = Path(__file__).resolve()
ROOT = next(
    (
        candidate
        for candidate in (
            FUNCTION_PATH.parents[3],
            FUNCTION_PATH.parents[1] / ".python-runtime",
            FUNCTION_PATH.parents[1],
            Path.cwd(),
        )
        if (candidate / "agents" / "mock" / "run_mock_flow.py").exists()
    ),
    FUNCTION_PATH.parents[1],
)
AGENTS_DIR = ROOT / "agents"
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from mock.run_mock_flow import EXPECTED_STEPS, run_flow  # noqa: E402


VALID_SCENARIOS = {"INC-1042", "INC-1043"}
APPROVAL_SEQUENCE = 14
TOKEN_TTL_SECONDS = 600
MAX_BODY_BYTES = 256_000
RATE_LIMIT_REQUESTS = 6
RATE_LIMIT_WINDOW_SECONDS = 60
LOCAL_SIGNING_SECRET = "sentinel-relay-local-development-only"

_requests_by_ip: dict[str, deque[float]] = defaultdict(deque)

AGENT_ENV_PREFIX = {
    "agent-commander": "BAND_LEADER",
    "agent-forensics": "FORENSICS_AGENT",
    "agent-threat-intel": "THREAT_INTEL_AGENT",
    "agent-code-review": "CODE_REVIEW_AGENT",
    "agent-risk-compliance": "RISK_COMPLIANCE_AGENT",
    "agent-remediation": "REMEDIATION_AGENT",
}


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _signing_secret() -> bytes:
    value = os.environ.get("SENTINEL_RELAY_RUN_SIGNING_SECRET", "").strip()
    if value:
        return value.encode("utf-8")
    return LOCAL_SIGNING_SECRET.encode("utf-8")


def create_continuation(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    encoded = _b64encode(body)
    signature = hmac.new(_signing_secret(), encoded.encode("ascii"), hashlib.sha256).digest()
    return f"{encoded}.{_b64encode(signature)}"


def verify_continuation(token: str, *, now: float | None = None) -> dict[str, Any]:
    try:
        encoded, supplied_signature = token.split(".", 1)
        expected_signature = hmac.new(_signing_secret(), encoded.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(expected_signature, _b64decode(supplied_signature)):
            raise ValueError("Continuation signature is invalid.")
        payload = json.loads(_b64decode(encoded))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Continuation token is invalid.") from exc

    issued_at = payload.get("issuedAt")
    if not isinstance(issued_at, (int, float)):
        raise ValueError("Continuation token is missing its issue time.")
    current_time = time.time() if now is None else now
    if current_time - float(issued_at) > TOKEN_TTL_SECONDS:
        raise ValueError("Continuation token has expired.")
    if payload.get("scenarioId") not in VALID_SCENARIOS:
        raise ValueError("Continuation scenario is invalid.")
    return payload


def run_phase(scenario_id: str, action: str) -> list[dict[str, Any]]:
    if scenario_id not in VALID_SCENARIOS:
        raise ValueError("Unknown scenario.")
    room = run_flow(
        incident_id=scenario_id,
        stop_after=APPROVAL_SEQUENCE if action == "investigate" else EXPECTED_STEPS,
    )
    return room.transcript if action == "investigate" else room.transcript[APPROVAL_SEQUENCE:]


def _fallback_messages(scenario_id: str, action: str) -> list[dict[str, Any]]:
    filename = scenario_id.lower() + "-transcript.json"
    project_root = FUNCTION_PATH.parents[1]
    scenario_root = ROOT / "apps" / "web" if (ROOT / "apps" / "web").exists() else project_root
    path = scenario_root / "src" / "lib" / "scenarios" / filename
    messages = json.loads(path.read_text(encoding="utf-8"))
    return messages[:APPROVAL_SEQUENCE] if action == "investigate" else messages[APPROVAL_SEQUENCE:]


def _partner_used_live(value: Any) -> bool:
    if isinstance(value, dict):
        if value.get("usedLiveApi") is True:
            return True
        return any(_partner_used_live(item) for item in value.values())
    if isinstance(value, list):
        return any(_partner_used_live(item) for item in value)
    return False


def _unwrap_data(raw: Any) -> Any:
    if isinstance(raw, dict) and "data" in raw:
        return raw["data"]
    return raw


class BandSync:
    def __init__(self) -> None:
        self.base_url = os.environ.get("BAND_API_BASE_URL", "https://app.band.ai/api/v1").rstrip("/")
        self.leader_key = os.environ.get("BAND_LEADER_AGENT_API_KEY", "").strip()
        self.enabled = os.environ.get("BAND_PROVIDER_ENABLED", "false").lower() == "true" and bool(self.leader_key)
        self.warning: str | None = None

    def create_room(self, scenario_id: str) -> str | None:
        if not self.enabled:
            return None
        try:
            raw = self._request(self.leader_key, "/agent/chats", {"chat": {}})
            data = _unwrap_data(raw)
            room_id = data.get("id") if isinstance(data, dict) else None
            if not room_id:
                raise RuntimeError("Band did not return a room id.")
            self._add_participants(str(room_id))
            self.post_event(
                str(room_id),
                "agent-commander",
                {
                    "event": {
                        "content": f"Sentinel Relay opened {scenario_id}",
                        "message_type": "task",
                        "metadata": {"source_system": "sentinel_relay", "case_id": scenario_id},
                    }
                },
            )
            return str(room_id)
        except Exception as exc:  # noqa: BLE001 - degrade without exposing credentials
            self.warning = str(exc)
            return None

    def post_message(self, room_id: str | None, message: dict[str, Any]) -> bool:
        if not room_id or not self.enabled:
            return False
        event = {
            "event": {
                "content": message.get("summary", message.get("title", "Agent update")),
                "message_type": "task",
                "metadata": {
                    "source_system": "sentinel_relay",
                    "schema_version": message.get("schemaVersion"),
                    "case_id": message.get("caseId"),
                    "room_id": room_id,
                    "agent_id": message.get("agentId"),
                    "agent_name": message.get("agentName"),
                    "message_id": message.get("id"),
                    "message_type": message.get("type"),
                    "sequence": message.get("sequence"),
                    "evidence_ids": message.get("evidenceIds", []),
                    "target_agent_ids": message.get("targetAgentIds", []),
                    "decision_impact": message.get("decisionImpact"),
                },
            }
        }
        try:
            self.post_event(room_id, str(message.get("agentId")), event)
            return True
        except Exception as exc:  # noqa: BLE001
            self.warning = str(exc)
            return False

    def post_event(self, room_id: str, agent_id: str, event: dict[str, Any]) -> None:
        key = self._agent_key(agent_id) or self.leader_key
        self._request(key, f"/agent/chats/{room_id}/events", event)

    def _agent_key(self, agent_id: str) -> str | None:
        prefix = AGENT_ENV_PREFIX.get(agent_id)
        if not prefix:
            return None
        return os.environ.get(f"{prefix}_API_KEY", "").strip() or os.environ.get(
            f"{prefix}_AGENT_API_KEY", ""
        ).strip() or None

    def _add_participants(self, room_id: str) -> None:
        for agent_id, prefix in AGENT_ENV_PREFIX.items():
            if agent_id == "agent-commander":
                continue
            participant_id = os.environ.get(f"{prefix}_ID", "").strip() or os.environ.get(
                f"{prefix}_AGENT_ID", ""
            ).strip()
            if not participant_id:
                continue
            try:
                self._request(
                    self.leader_key,
                    f"/agent/chats/{room_id}/participants",
                    {"participant": {"participant_id": participant_id}},
                )
            except Exception as exc:  # noqa: BLE001
                self.warning = str(exc)

    def _request(self, api_key: str, path: str, payload: dict[str, Any]) -> Any:
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "SentinelRelay/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Band request failed with HTTP {exc.code}.") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError("Band request was unavailable.") from exc


def _client_ip(headers: Any) -> str:
    forwarded = headers.get("x-forwarded-for", "")
    return forwarded.split(",", 1)[0].strip() or "local"


def _rate_limited(ip: str, *, now: float | None = None) -> bool:
    current = time.time() if now is None else now
    bucket = _requests_by_ip[ip]
    while bucket and current - bucket[0] > RATE_LIMIT_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_REQUESTS:
        return True
    bucket.append(current)
    return False


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        self._json_response(
            200,
            {
                "ok": True,
                "runtime": "python",
                "scenarios": sorted(VALID_SCENARIOS),
                "bandConfigured": BandSync().enabled,
                "modelConfigured": bool(os.environ.get("AIMLAPI_API_KEY", "").strip()),
                "signingConfigured": bool(os.environ.get("SENTINEL_RELAY_RUN_SIGNING_SECRET", "").strip()),
            },
        )

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        if _rate_limited(_client_ip(self.headers)):
            self._json_response(429, {"error": "Please wait before starting another investigation."})
            return

        content_length = int(self.headers.get("content-length", "0") or "0")
        if content_length <= 0 or content_length > MAX_BODY_BYTES:
            self._json_response(400, {"error": "Request body is missing or too large."})
            return
        try:
            payload = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json_response(400, {"error": "Request body must be valid JSON."})
            return

        action = payload.get("action")
        if action not in {"investigate", "approve"}:
            self._json_response(400, {"error": "Action must be investigate or approve."})
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        try:
            if action == "investigate":
                self._investigate(str(payload.get("scenarioId", "")).upper())
            else:
                self._approve(payload)
        except ValueError:
            self._emit({"type": "error", "code": "invalid_request", "message": "The investigation could not be resumed."})
        except Exception:  # noqa: BLE001 - client receives safe fallback only
            if action == "approve":
                self._emit({"type": "error", "code": "resolution_unavailable", "message": "The live resolution was unavailable."})
                return
            scenario_id = str(payload.get("scenarioId", "INC-1042")).upper()
            if scenario_id not in VALID_SCENARIOS:
                scenario_id = "INC-1042"
            self._emit({"type": "fallback", "mode": "verified_replay", "reasonCode": "agent_runtime_unavailable"})
            for message in _fallback_messages(scenario_id, action):
                self._emit({"type": "agent_message", "message": message, "mode": "verified_replay"})

    def _investigate(self, scenario_id: str) -> None:
        if scenario_id not in VALID_SCENARIOS:
            self._emit({"type": "fallback", "mode": "verified_replay", "reasonCode": "unknown_scenario"})
            return

        run_id = str(uuid.uuid4())
        self._emit({"type": "run_started", "runId": run_id, "scenarioId": scenario_id})
        band = BandSync()
        room_id = band.create_room(scenario_id)
        mode = "live_local"
        messages = run_phase(scenario_id, "investigate")
        posted = 0
        for original in messages:
            message = {**original, "roomId": room_id or original.get("roomId")}
            if band.post_message(room_id, message):
                posted += 1
            self._emit({"type": "agent_message", "message": message})

        model_live = any(_partner_used_live(message) for message in messages)
        if room_id and posted == len(messages) and model_live:
            mode = "live_band"
        self._emit(
            {
                "type": "integration_status",
                "mode": mode,
                "band": "connected" if room_id and posted == len(messages) else "degraded",
                "model": "live" if model_live else "fallback",
            }
        )
        continuation = create_continuation(
            {
                "scenarioId": scenario_id,
                "runId": run_id,
                "roomId": room_id,
                "mode": mode,
                "issuedAt": int(time.time()),
            }
        )
        self._emit(
            {
                "type": "approval_required",
                "continuation": continuation,
                "request": messages[-1],
                "mode": mode,
            }
        )

    def _approve(self, payload: dict[str, Any]) -> None:
        if payload.get("decision") != "approved":
            raise ValueError("Only an explicit approved decision can resume remediation.")
        state = verify_continuation(str(payload.get("continuation", "")))
        scenario_id = str(state["scenarioId"])
        room_id = state.get("roomId")
        band = BandSync()
        messages = run_phase(scenario_id, "approve")
        posted = 0
        for original in messages:
            message = {**original, "roomId": room_id or original.get("roomId")}
            if band.post_message(room_id, message):
                posted += 1
            self._emit({"type": "agent_message", "message": message})
        model_live = any(_partner_used_live(message) for message in messages)
        mode = str(state.get("mode") or "live_local")
        if room_id and posted == len(messages) and model_live:
            mode = "live_band"
        self._emit(
            {
                "type": "result",
                "mode": mode,
                "roomId": room_id,
                "messages": len(messages),
                "report": messages[-1],
            }
        )

    def _emit(self, event: dict[str, Any]) -> None:
        self.wfile.write((json.dumps(event, separators=(",", ":")) + "\n").encode("utf-8"))
        self.wfile.flush()

    def _json_response(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


__all__ = [
    "APPROVAL_SEQUENCE",
    "create_continuation",
    "run_phase",
    "verify_continuation",
]
