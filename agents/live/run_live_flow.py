"""Run the full inc-1042 agent flow with real LLM calls (agents lane, live mode).

Same 14-step Commander-led @mention flow as the offline mock, driven through the
same ``handle_turn`` seam and the same schema validator — only the six AI agents'
turns are produced by the AI/ML API instead of canned data. The human approval
gate (step 11) is a human actor, not an LLM, so it stays the canned deterministic
decision in both modes.

Mode is selected by the existing ``SENTINEL_RELAY_AGENT_OFFLINE_MODE`` toggle:
  * unset / not "true"  -> LIVE  (real AI/ML API calls for the six agents)
  * "true"              -> MOCK  (canned turns; identical to run_mock_flow)

This runner does NOT hide errors. If a live turn fails (API error, timeout, or
off-schema output after the seam's retries), the real exception is printed and
that turn is marked ERROR; the flow continues so every failure is visible, and
the process exits non-zero. A failed live turn is never replaced by canned data.
Provenance (LIVE / CANNED / ERROR) is reported per message in the console and is
kept entirely off the AgentMessage schema.

Usage:
    python3 agents/live/run_live_flow.py            # tagged transcript + raw JSON
    python3 agents/live/run_live_flow.py --json     # raw AgentMessage[] only
    SENTINEL_RELAY_AGENT_OFFLINE_MODE=true python3 agents/live/run_live_flow.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_DIR))

from typing import Any, Callable  # noqa: E402

from common.aimlapi_client import AimlapiClient, AimlapiError  # noqa: E402
from common.fixtures import AGENT_PROFILES, load_incident  # noqa: E402
from common.live_agent import make_live_handle_turn  # noqa: E402
from common.schema import AgentTurnContext  # noqa: E402
from mock.mock_transport import MockBandRoom  # noqa: E402
from mock.run_mock_flow import (  # noqa: E402
    CANNED_TURNS,
    EXPECTED_STEPS,
    HANDLES,
    _context,
    build_steps,
)

# The human approval gate is a human actor, never an LLM — canned in both modes.
HUMAN_GATE_ID = "agent-human-approver"

# agent_id -> directory holding that agent's prompt.md.
_PROMPT_DIR = {
    "agent-commander": "commander",
    "agent-forensics": "forensics",
    "agent-threat-intel": "threat_intel",
    "agent-code-review": "code_review",
    "agent-risk-compliance": "risk_compliance",
    "agent-remediation": "remediation",
}


def _is_offline() -> bool:
    return os.getenv("SENTINEL_RELAY_AGENT_OFFLINE_MODE") == "true"


def _build_live_turns(client: AimlapiClient) -> dict[str, Callable[[AgentTurnContext], dict[str, Any]]]:
    """One live handle_turn per AI agent, sharing a single client."""
    live: dict[str, Callable[[AgentTurnContext], dict[str, Any]]] = {}
    for agent_id, dir_name in _PROMPT_DIR.items():
        live[agent_id] = make_live_handle_turn(
            agent_id=agent_id,
            agent_name=AGENT_PROFILES[agent_id]["name"],
            prompt_path=_AGENTS_DIR / dir_name / "prompt.md",
            canned_handle_turn=CANNED_TURNS[agent_id],
            client=client,
        )
    return live


def run_live_flow(offline: bool) -> tuple[MockBandRoom, list[dict[str, Any]]]:
    """Drive the 14-step flow. Returns the room and a per-step outcome log."""
    client = None if offline else AimlapiClient()
    live_turns = {} if offline else _build_live_turns(client)

    packet = load_incident()
    room = MockBandRoom(room_id=packet.case["roomId"])
    for agent_id, handle in HANDLES.items():
        room.register(agent_id, handle)

    outcomes: list[dict[str, Any]] = []
    for sequence, (actor_id, task) in enumerate(build_steps(), start=1):
        # Choose the turn AND its provenance: live for AI agents in live mode,
        # canned for the human gate (always) and for everything in offline mode.
        if not offline and actor_id != HUMAN_GATE_ID:
            handle_turn = live_turns[actor_id]
            provenance = "LIVE"
        else:
            handle_turn = CANNED_TURNS[actor_id]
            provenance = "CANNED"

        ctx = _context(packet, room, actor_id, task, sequence)
        outcome: dict[str, Any] = {"sequence": sequence, "actorId": actor_id, "provenance": provenance}
        try:
            room.post(handle_turn, ctx)
            if provenance == "LIVE" and client is not None and client.last_call:
                outcome["apiCall"] = client.last_call
        except Exception as exc:  # noqa: BLE001 - surface every real failure
            outcome["provenance"] = "ERROR"
            outcome["error"] = f"{type(exc).__name__}: {exc}"
            if not offline and client is not None and client.last_call:
                outcome["apiCall"] = client.last_call
            print(
                f"\n[ERROR] step {sequence} ({actor_id}) failed live turn — NOT substituting canned:\n"
                f"        {outcome['error']}",
                file=sys.stderr,
            )
        outcomes.append(outcome)

    return room, outcomes


def _print_report(room: MockBandRoom, outcomes: list[dict[str, Any]], offline: bool) -> None:
    mode = "MOCK (canned, offline)" if offline else "LIVE (real AI/ML API calls)"
    print(f"\nSentinel Relay — inc-1042 flow — mode: {mode}\n{'=' * 74}")
    by_seq = {m["sequence"]: m for m in room.transcript}
    for outcome in outcomes:
        seq = outcome["sequence"]
        message = by_seq.get(seq)
        api = outcome.get("apiCall") or {}
        usage = api.get("usage") or {}
        stat = ""
        if outcome["provenance"] == "LIVE":
            stat = f"  [model={api.get('model')} tokens={usage.get('total_tokens', '?')}]"
        if message is not None:
            sender = room.handles.get(message["agentId"], message["agentId"])
            print(
                f"[{seq:>2}] {outcome['provenance']:<6} @{sender:<14} {message['type']:<16}{stat}\n"
                f"      {message['title']}"
            )
        else:
            print(f"[{seq:>2}] {outcome['provenance']:<6} {outcome['actorId']:<22} {outcome.get('error', '')}")
    print("=" * 74)

    live = sum(1 for o in outcomes if o["provenance"] == "LIVE")
    canned = sum(1 for o in outcomes if o["provenance"] == "CANNED")
    errored = sum(1 for o in outcomes if o["provenance"] == "ERROR")
    total_tokens = sum((o.get("apiCall") or {}).get("usage", {}).get("total_tokens", 0) or 0 for o in outcomes)
    print(
        f"\nSteps: {len(outcomes)} | live: {live} | canned: {canned} | errored: {errored} | "
        f"messages on transcript: {len(room.transcript)}/{EXPECTED_STEPS}"
    )
    if not offline:
        print(f"Live API tokens used this run: {total_tokens}")
    if errored:
        print(f"\nFAIL: {errored} turn(s) errored — see [ERROR] lines above. No canned substitution was made.")
    else:
        print("\nOK: every step produced a schema-valid AgentMessage; provenance shown per message above.")


def main(argv: list[str]) -> int:
    offline = _is_offline()
    try:
        room, outcomes = run_live_flow(offline)
    except AimlapiError as exc:
        # Setup-level failure (e.g. missing/placeholder key) before any turn ran.
        print(f"\n[FATAL] live mode could not start: {exc}", file=sys.stderr)
        return 2

    if "--json" in argv:
        print(json.dumps(room.transcript, indent=2))
    else:
        _print_report(room, outcomes, offline)
        print("\n--- RAW AgentMessage[] ---")
        print(json.dumps(room.transcript, indent=2))

    return 1 if any(o["provenance"] == "ERROR" for o in outcomes) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
