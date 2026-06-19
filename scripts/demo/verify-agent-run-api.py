#!/usr/bin/env python3
"""Verify the two-phase Vercel agent runtime without network calls."""

from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["BAND_PROVIDER_ENABLED"] = "false"
os.environ["SENTINEL_RELAY_AIMLAPI_ENABLED"] = "false"
os.environ["SENTINEL_RELAY_RUN_SIGNING_SECRET"] = "verification-secret"

from apps.web.api.agent_run import (  # noqa: E402
    APPROVAL_SEQUENCE,
    create_continuation,
    run_phase,
    verify_continuation,
)


def main() -> int:
    for scenario_id in ("INC-1042", "INC-1043"):
        investigation = run_phase(scenario_id, "investigate")
        resolution = run_phase(scenario_id, "approve")
        assert len(investigation) == APPROVAL_SEQUENCE
        assert investigation[-1]["type"] == "approval_request"
        assert len(resolution) == 4
        assert resolution[0]["type"] == "approval_decision"
        assert resolution[-1]["type"] == "report_section"

    token = create_continuation(
        {"scenarioId": "INC-1042", "runId": "verify", "roomId": None, "mode": "live_local", "issuedAt": 1000}
    )
    assert verify_continuation(token, now=1001)["runId"] == "verify"

    try:
        verify_continuation(token + "tampered", now=1001)
    except ValueError:
        pass
    else:
        raise AssertionError("tampered continuation was accepted")

    try:
        verify_continuation(token, now=2000)
    except ValueError:
        pass
    else:
        raise AssertionError("expired continuation was accepted")

    print("Agent run API verification passed: 14 investigation messages + 4 approved-resolution messages for both scenarios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
