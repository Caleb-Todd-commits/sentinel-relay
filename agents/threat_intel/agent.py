"""Threat Intel agent business logic (agents lane).

Assesses the source IPs and behavior, deliberately refusing real-world
attribution overreach (the IPs are documentation-range demo indicators).
Deterministic in mock mode.

Analytic doctrine (see threat_intel/prompt.md): assess exposure velocity
(commodity scanners find and abuse leaked secrets fast), read the abuse and
monetisation path for THIS credential type, and give a likelihood-of-exploitation
view rather than restating that a secret leaked.
"""

from __future__ import annotations

from typing import Any

from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-threat-intel"
AGENT_NAME = "Threat Intel Agent"

_EVIDENCE = ["ev-ip-intel", "ev-api-gateway-logs"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    findings = [
        {
            "claim": (
                "Discovery-to-abuse velocity is consistent with automated secret hunting: "
                "~18 minutes from the 20:47:11Z deploy to first external use at 21:04:59Z."
            ),
            "evidenceRef": "ev-api-gateway-logs",
            "source": "api_gateway_logs.jsonl",
            "observation": (
                "Leaked tokens committed to env/config files are routinely found and exercised "
                "within minutes by commodity scanners and secret-hunting crawlers; the timing here "
                "fits opportunistic automation, not a slow targeted operation."
            ),
        },
        {
            "claim": (
                "Two off-baseline external IPs used the token; 198.51.100.24 is expected CI/prod egress "
                "and must not be miscounted as hostile."
            ),
            "evidenceRef": "ev-ip-intel",
            "source": "suspicious_ips.json",
            "observation": (
                "203.0.113.77 (curl/8.1.2) ran bulk export; 198.51.100.188 (python-requests/2.31) "
                "probed an internal canary then hit the VIP export. Both used automation user agents "
                "during the spike; 198.51.100.24 is the known payments worker egress."
            ),
        },
        {
            "claim": (
                "Behavior shows intent to retain access: 203.0.113.77 attempted another request AFTER "
                "rotation, raising likelihood this is active abuse rather than incidental exposure."
            ),
            "evidenceRef": "ev-ip-intel",
            "source": "suspicious_ips.json",
            "observation": "Post-rotation retry at 21:12:02Z indicates the source was actively working the token, not a passive scan that moved on.",
        },
    ]
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="finding",
        title="High likelihood of exploitation: fast automated discovery, bulk PII abuse path, attacker persistence",
        summary=(
            "Assessing this as active abuse of an exposed customer-records bearer token. The ~18-minute "
            "gap from deploy to first external use fits commodity secret-scanning velocity, the access "
            "pattern (canary probe then bulk and VIP export) is a classic enumerate-then-exfiltrate PII "
            "monetisation path, and a post-rotation retry shows the source wanted to keep access. "
            "Likelihood of exploitation is HIGH. Indicators are documentation-range demo IPs, so no "
            "real-world actor attribution is claimed."
        ),
        confidence=0.74,
        severity="medium",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact=(
            "Raises this from 'a secret leaked' to 'an exposed credential is being actively abused', which "
            "should drive urgency on containment and on the breach-notification assessment."
        ),
        next_action="Risk & Compliance should treat this as active unauthorized use feeding the GDPR/CCPA assessment, not yet as attributed breach.",
        payload={
            "kind": "finding",
            "data": {
                "findings": findings,
                "exposureVelocity": {
                    "deployAt": "2026-06-12T20:47:11Z",
                    "firstAbuseAt": "2026-06-12T21:04:59Z",
                    "minutesToAbuse": 18,
                    "assessment": "Within the minutes-to-hours window typical of automated secret discovery; supports opportunistic-then-hands-on abuse.",
                },
                "credentialAbusePath": {
                    "credentialType": "customer-records service bearer token (read access to customer PII + payment-methods)",
                    "likelyObjective": "bulk exfiltration of customer PII / payment-method data",
                    "monetisation": [
                        "Resale of customer + payment-method records on data markets",
                        "Account-takeover / payment fraud against affected customers",
                        "Extortion of the platform over the export",
                    ],
                    "observedTradecraft": ["canary/seed-path probing", "bulk paginated export", "targeting the VIP segment", "post-rotation retry"],
                },
                "likelihoodOfExploitation": "high",
                "strongestSignals": [
                    "confirmed use by unexpected external IPs (not just exposure)",
                    "automation user agents (curl, python-requests) off the worker baseline",
                    "enumerate-then-export sequence",
                    "post-rotation persistence attempt",
                    "discovery-to-abuse timing consistent with automated scanning",
                ],
                "weakSignals": ["raw IP reputation alone", "geo of documentation-range IPs"],
                "limitations": [
                    "Documentation-range IPs; do NOT claim real-world threat-actor attribution or geolocation.",
                    "Cannot confirm resale or downstream use; monetisation paths are assessed, not observed.",
                ],
            },
        },
    )
