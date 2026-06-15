"""Code Review agent business logic (agents lane).

Inspects the Friday deploy diff and secret-scan output to identify the exposure
mechanism. Deterministic in mock mode.
"""

from __future__ import annotations

from typing import Any

from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-code-review"
AGENT_NAME = "Code Review Agent"

_EVIDENCE = ["ev-code-diff", "ev-secret-scan"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    findings = [
        {
            "claim": "Friday deploy added a fallback-token code path guarded by ALLOW_FALLBACK_TOKEN.",
            "evidenceRef": "ev-code-diff",
            "source": "git_diff.patch",
            "observation": "Returns process.env.PAYMENTS_API_FALLBACK_TOKEN when ALLOW_FALLBACK_TOKEN === 'true'.",
        },
        {
            "claim": "A new .env.release file enables the fallback and ships the token variable.",
            "evidenceRef": "ev-secret-scan",
            "source": "secret_scan.json",
            "observation": "secret-1042-001: high-severity finding (0.92) on .env.release line 3.",
        },
    ]
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="finding",
        title="Friday deploy introduced the fallback-token exposure path",
        summary=(
            "The deploy diff adds an ALLOW_FALLBACK_TOKEN code path and a new "
            ".env.release that enables it and ships PAYMENTS_API_FALLBACK_TOKEN, "
            "which the secret scanner flagged as a high-severity finding."
        ),
        confidence=0.91,
        severity="high",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact="Establishes the root-cause change; the fix is to disable the fallback path and remove .env.release.",
        next_action="Remediation should disable the fallback path and add a deploy-time secret-scan guardrail after approval.",
        payload={
            "kind": "finding",
            "data": {
                "findings": findings,
                "rootCauseChange": "ALLOW_FALLBACK_TOKEN fallback path + .env.release",
                "limitations": ["Token value in the patch is a redacted demo placeholder, not a usable secret."],
            },
        },
    )
