#!/usr/bin/env python3
"""Smoke-test the public Band REST API connection with safe identity checks.

This script does not create a chat. It only verifies whether the configured
Commander Agent key can call GET /api/v1/agent/me, and whether the optional
Human key can call GET /api/v1/me/profile.
"""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def clean_url(value: str | None) -> str:
    base = (value or "https://app.band.ai/api/v1").rstrip("/")
    if base.endswith("/agent"):
        base = base[: -len("/agent")]
    if base.endswith("/me"):
        base = base[: -len("/me")]
    return base


def request_json(url: str, api_key: str) -> tuple[bool, int, object]:
    req = Request(url, headers={"X-API-Key": api_key, "Accept": "application/json"}, method="GET")
    try:
        with urlopen(req, timeout=15) as response:
            body = response.read().decode("utf-8")
            return True, response.status, json.loads(body) if body else {}
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            payload: object = json.loads(body) if body else {}
        except json.JSONDecodeError:
            payload = body
        return False, exc.code, payload
    except URLError as exc:
        return False, 0, str(exc)


def safe_payload(payload: object) -> object:
    text = json.dumps(payload, default=str)
    for key_name in ["api_key", "key", "token", "secret"]:
        text = text.replace(key_name, f"{key_name}")
    return json.loads(text) if text.startswith("{") or text.startswith("[") else text


def main() -> int:
    base = clean_url(os.environ.get("BAND_API_BASE_URL"))
    commander_key = os.environ.get("BAND_COMMANDER_AGENT_API_KEY", "").strip()
    human_key = os.environ.get("BAND_HUMAN_API_KEY", "").strip()

    if not commander_key:
        print("FAIL BAND_COMMANDER_AGENT_API_KEY is required for the smoke test.")
        return 1

    ok, status, payload = request_json(f"{base}/agent/me", commander_key)
    print(json.dumps({"check": "agent/me", "ok": ok, "status": status, "payload": safe_payload(payload)}, indent=2))
    if not ok:
        return 1

    if human_key:
        ok, status, payload = request_json(f"{base}/me/profile", human_key)
        print(json.dumps({"check": "me/profile", "ok": ok, "status": status, "payload": safe_payload(payload)}, indent=2))
        return 0 if ok else 1

    print("SKIP BAND_HUMAN_API_KEY not set; dashboard can still use the local server mirror.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
