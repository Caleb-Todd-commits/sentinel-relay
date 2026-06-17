"""Thin OpenAI-compatible client for the AI/ML API (live mode only).

One module, standard library only (``urllib``) so the agents lane keeps its
zero-install property: live mode needs the API key and nothing pip-installed.

Config comes from the environment (the existing ``.env`` keys), nothing new:
  * ``AIMLAPI_API_KEY``  — required; the call fails loudly if it is missing or
    still the ``REPLACE_WITH_...`` placeholder.
  * ``AIMLAPI_BASE_URL`` — defaults to ``https://api.aimlapi.com/v1``.
  * ``AIMLAPI_MODEL``    — defaults to ``gpt-4o-mini``.

This client does NOT hide failures: any transport error, non-200 status, or
unparseable body is raised as :class:`AimlapiError` carrying the real detail.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "https://api.aimlapi.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT_SECONDS = 90
# Cloudflare fronts api.aimlapi.com and 403s the default "Python-urllib" agent
# (Cloudflare error 1010). A named User-Agent is required to reach the API.
_USER_AGENT = "sentinel-relay-agents/0.1"
_PLACEHOLDER_PREFIX = "REPLACE_WITH"


class AimlapiError(RuntimeError):
    """Raised when a live AI/ML API call fails. Never swallowed."""


def load_env_file(env_path: Path | str | None = None) -> None:
    """Populate ``os.environ`` from a ``.env`` file (stdlib, no python-dotenv).

    Existing environment variables win; only missing keys are filled. Safe to
    call when the file is absent. Kept tiny on purpose — this is config, not a
    dependency.
    """
    if env_path is None:
        repo_root = Path(__file__).resolve().parents[2]
        env_path = repo_root / ".env"
    env_path = Path(env_path)
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


class AimlapiClient:
    """Minimal chat-completions client. One public method: :meth:`chat`."""

    def __init__(self) -> None:
        load_env_file()
        api_key = (os.getenv("AIMLAPI_API_KEY") or "").strip()
        if not api_key:
            raise AimlapiError(
                "AIMLAPI_API_KEY is not set. Live mode needs a real AI/ML API key "
                "in the environment or .env."
            )
        if api_key.startswith(_PLACEHOLDER_PREFIX):
            raise AimlapiError(
                f"AIMLAPI_API_KEY is still the placeholder ({api_key!r}); refusing "
                "to make live calls with a placeholder key."
            )
        self.api_key = api_key
        self.base_url = (os.getenv("AIMLAPI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = os.getenv("AIMLAPI_MODEL") or DEFAULT_MODEL
        # Provenance of the most recent call, for the runner to report (kept off
        # the AgentMessage schema deliberately).
        self.last_call: dict[str, Any] | None = None

    def chat(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_tokens: int = 3000,
    ) -> str:
        """POST one chat completion and return the assistant message content.

        Raises :class:`AimlapiError` on timeout, transport failure, non-200
        status, or a response body that does not contain a message — the real
        cause is always preserved in the message.
        """
        url = f"{self.base_url}/chat/completions"
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": _USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
                status = response.status
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:1000]
            raise AimlapiError(
                f"AI/ML API HTTP {exc.code} from {url}: {detail}"
            ) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise AimlapiError(f"AI/ML API request to {url} failed: {exc}") from exc

        try:
            data = json.loads(body)
            content = data["choices"][0]["message"]["content"]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            raise AimlapiError(
                f"AI/ML API returned an unparseable body (HTTP {status}): "
                f"{body[:1000]!r}"
            ) from exc

        self.last_call = {
            "model": data.get("model", self.model),
            "status": status,
            "usage": data.get("usage"),
            "content_chars": len(content),
        }
        return content
