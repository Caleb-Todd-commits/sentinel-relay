"""Code Review agent business logic (agents lane).

Inspects the Friday deploy diff and secret-scan output to identify the exposure
mechanism. Deterministic in mock mode.

Analytic doctrine (see code_review/prompt.md): trace how the secret entered and
propagated, check whether push protection was bypassed, and — critically — hunt
for sibling/fallback credentials and legacy auth paths that keep the old secret
alive after rotation. Rotating one credential and leaving a sibling is the classic
failure mode.
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
            "claim": "Introducing change: the Friday deploy added a fallback-token code path in getServiceToken() guarded by ALLOW_FALLBACK_TOKEN.",
            "evidenceRef": "ev-code-diff",
            "source": "git_diff.patch",
            "observation": (
                "services/customer-records/src/auth/service-token.ts (blob 61bf8b2->e248d7a): on Secrets "
                "Manager failure it now returns process.env.PAYMENTS_API_FALLBACK_TOKEN when "
                "ALLOW_FALLBACK_TOKEN === 'true' instead of failing closed."
            ),
        },
        {
            "claim": "Secret sprawl: a NEW committed .env.release ships the fallback token variable and turns the path on in production.",
            "evidenceRef": "ev-secret-scan",
            "source": "secret_scan.json",
            "observation": (
                "secret-1042-001 (ruleId env-file-sensitive-token, severity high, confidence 0.92, "
                "status UNRESOLVED) on .env.release line 3; the build proceeded despite the unresolved "
                "high finding, so push/secret protection was effectively bypassed or absent."
            ),
        },
        {
            "claim": (
                "SIBLING-CREDENTIAL RISK: subject svc-payments-api is now authenticated by TWO credentials "
                "— the Secrets Manager primary (prod/payments/customer-records/token, svc-payments-prod-v2) "
                "and the static env fallback (PAYMENTS_API_FALLBACK_TOKEN). Rotating one does NOT invalidate the other."
            ),
            "evidenceRef": "ev-code-diff",
            "source": "git_diff.patch + cloudtrail_events.jsonl",
            "observation": (
                "The fallback is a separate static secret, not a version of the managed secret, so a Secrets "
                "Manager rotation leaves the fallback usable, and disabling the fallback leaves the managed "
                "secret untouched. Both must be addressed independently at their issuers."
            ),
        },
        {
            "claim": "Second risky flag: .env.release also sets CUSTOMER_EXPORT_ENABLED=true, widening the blast radius to the bulk export endpoints the attacker hit.",
            "evidenceRef": "ev-code-diff",
            "source": "git_diff.patch",
            "observation": "The same release file that introduced the fallback token also enabled the customer export capability used for the 5000-row pulls.",
        },
    ]
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="finding",
        title="Root cause: Friday deploy added a fallback token path + committed .env.release; a sibling credential survives rotation",
        summary=(
            "The deploy diff changed getServiceToken() to fail OPEN to a static env fallback "
            "(PAYMENTS_API_FALLBACK_TOKEN) behind ALLOW_FALLBACK_TOKEN, and a new committed .env.release "
            "shipped that token plus CUSTOMER_EXPORT_ENABLED=true. The scanner flagged it high-severity but "
            "UNRESOLVED and the release still went out. Critically, subject svc-payments-api now has two "
            "credentials — the Secrets Manager primary and this static fallback — so rotating one leaves the "
            "other alive: containment must hit BOTH issuers and disable the fallback path, not just rotate the token."
        ),
        confidence=0.91,
        severity="high",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact=(
            "Establishes the root-cause change AND warns that single-credential rotation would leave a sibling "
            "path usable — the classic incomplete-containment failure."
        ),
        next_action=(
            "Remediation must disable the ALLOW_FALLBACK_TOKEN path, remove .env.release, invalidate the fallback "
            "at its issuer, AND confirm no other clone/CI/image still carries it; add a deploy-time secret-scan gate."
        ),
        payload={
            "kind": "finding",
            "data": {
                "findings": findings,
                "rootCauseChange": "ALLOW_FALLBACK_TOKEN fail-open path + committed .env.release (token + CUSTOMER_EXPORT_ENABLED)",
                "introducedBy": {
                    "release": "release-9814",
                    "changedFile": "services/customer-records/src/auth/service-token.ts",
                    "blob": "61bf8b2->e248d7a",
                    "newFile": "services/customer-records/.env.release",
                    "commitSha": "not present in evidence packet — confirm with repo owner",
                },
                "pushProtection": "Bypassed or absent: secret-scan finding secret-1042-001 was high-severity and UNRESOLVED, yet the release shipped.",
                "siblingCredentialHunt": {
                    "principal": "svc-payments-api",
                    "credentialsAuthenticatingPrincipal": [
                        {"name": "svc-payments-prod-v2", "issuer": "AWS Secrets Manager", "ref": "prod/payments/customer-records/token", "rotatingInvalidatesFallback": False},
                        {"name": "svc-payments-fallback-redacted", "issuer": "static env (PAYMENTS_API_FALLBACK_TOKEN)", "ref": ".env.release", "rotatingInvalidatesPrimary": False},
                    ],
                    "legacyOrFallbackPaths": ["ALLOW_FALLBACK_TOKEN fail-open branch in getServiceToken()"],
                    "mustAlsoCheck": [
                        "Other services / repos / .env files referencing PAYMENTS_API_FALLBACK_TOKEN or ALLOW_FALLBACK_TOKEN",
                        "CI/CD secret stores and built container images that may still carry the fallback value",
                        "Whether the fallback value is reused as a credential anywhere else",
                    ],
                    "warning": "Rotating only the Secrets Manager primary would leave the exposed fallback usable; disabling only the fallback would not rotate the primary. Treat them as independent.",
                },
                "limitations": [
                    "Token value in the patch is a redacted demo placeholder, not a usable secret.",
                    "No introducing commit SHA, repo name/branch, or image digest in the packet to fully pin propagation.",
                ],
            },
        },
    )
