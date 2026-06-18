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

from common.evidence_analysis import analyze_incident_evidence
from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-code-review"
AGENT_NAME = "Code Review Agent"

_EVIDENCE = ["ev-code-diff", "ev-secret-scan"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    if ctx.task.get("kind") == "cross_review":
        return _cross_review(ctx)

    facts = analyze_incident_evidence(ctx)
    changed_files = facts.code.changed_files or [
        "services/customer-records/src/auth/service-token.ts",
        "services/customer-records/.env.release",
    ]
    changed_files_text = ", ".join(changed_files)
    high_findings = facts.secret_scan.unresolved_high_count
    finding_refs = ", ".join(facts.secret_scan.finding_ids) or "secret-scan finding"
    finding_files = ", ".join(facts.secret_scan.finding_files) or "release env file"
    credential_label = facts.code.credential_label or facts.auth.compromised_token_id or facts.code.fallback_token_label or "svc-payments-fallback-redacted"
    diff_blob = facts.code.diff_blob_range or "61bf8b2->e248d7a"
    subject = facts.auth.subject or "svc-payments-api"
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"

    if is_oidc:
        findings = [
            {
                "claim": "Introducing change: the IAM trust policy widened GitHub OIDC from protected main to a repo-wide wildcard.",
                "evidenceRef": "ev-code-diff",
                "source": "git_diff.patch",
                "observation": (
                    f"infra/iam/github-oidc-trust.json (blob {diff_blob}): "
                    "token.actions.githubusercontent.com:sub changed from the protected main ref to repo:acme/payments:*."
                ),
            },
            {
                "claim": "No static secret was committed; the credential was minted dynamically through the widened trust policy.",
                "evidenceRef": "ev-secret-scan",
                "source": "secret_scan.json",
                "observation": (
                    f"The scanner reported {high_findings} unresolved high finding(s). This incident class "
                    "would bypass traditional secret scanning because the risky value is the trust boundary, not a literal token."
                ),
            },
            {
                "claim": (
                    f"FEDERATED-CREDENTIAL RISK: subject {subject} can now be assumed by untrusted preview refs, "
                    "so revoking one issued token is incomplete unless the trust policy is tightened."
                ),
                "evidenceRef": "ev-code-diff",
                "source": "git_diff.patch + cloudtrail_events.jsonl",
                "observation": (
                    "The role can mint fresh sessions while the wildcard remains. Containment must revoke active "
                    "sessions and restore protected-ref conditions before considering the window closed."
                ),
            },
            {
                "claim": "Export scope was expanded to customer records and payment-method reads for the federated role.",
                "evidenceRef": "ev-code-diff",
                "source": "git_diff.patch",
                "observation": "services/customer-records/config/export-policy.json adds customer:records:export and customer:payment-methods:read.",
            },
        ]
        title = "Root cause: OIDC trust wildcard let an untrusted workflow mint an exporter token"
        summary = (
            f"The deploy diff touched {changed_files_text} and widened GitHub OIDC trust from the protected "
            f"main branch to a repo-wide wildcard. That allowed an untrusted preview workflow to mint "
            f"{credential_label} for subject {subject}; no committed secret was required and the scanner correctly "
            f"shows {high_findings} unresolved high finding(s). Containment must revoke active federated sessions, "
            "restore protected-ref trust conditions, and remove export/payment-method scope from untrusted refs."
        )
        root_cause = facts.code.root_cause_summary or "OIDC trust wildcard + overbroad export scope"
        credential_hunt = {
            "principal": subject,
            "credentialsAuthenticatingPrincipal": [
                {
                    "name": credential_label,
                    "issuer": "GitHub OIDC / AWS STS",
                    "ref": facts.cloudtrail.managed_secret_id or "customer-records-github-oidc-exporter",
                    "revokingOneSessionFixesTrust": False,
                },
                {
                    "name": facts.auth.primary_token_ids[0] if facts.auth.primary_token_ids else "svc-analytics-exporter-prod",
                    "issuer": "production workload identity",
                    "ref": "protected main deployment",
                    "requiresIndependentReview": True,
                },
            ],
            "legacyOrFallbackPaths": facts.code.risky_controls,
            "mustAlsoCheck": [
                "Other roles using repo-wide token.actions.githubusercontent.com:sub wildcards",
                "Preview workflows that can request customer export scopes",
                "Active STS sessions minted before trust policy rollback",
            ],
            "warning": "Revoking the observed token is not enough while the OIDC wildcard can mint another session.",
        }
    else:
        findings = [
            {
                "claim": "Introducing change: the Friday deploy added a fallback-token code path in getServiceToken() guarded by ALLOW_FALLBACK_TOKEN.",
                "evidenceRef": "ev-code-diff",
                "source": "git_diff.patch",
                "observation": (
                    f"services/customer-records/src/auth/service-token.ts (blob {diff_blob}): on Secrets "
                    "Manager failure it now returns process.env.PAYMENTS_API_FALLBACK_TOKEN when "
                    "ALLOW_FALLBACK_TOKEN === 'true' instead of failing closed."
                ),
            },
            {
                "claim": "Secret sprawl: a NEW committed .env.release ships the fallback token variable and turns the path on in production.",
                "evidenceRef": "ev-secret-scan",
                "source": "secret_scan.json",
                "observation": (
                    f"{finding_refs} reported {high_findings} unresolved high finding(s) at {finding_files}; "
                    "the build proceeded despite the unresolved high finding, so push/secret protection was "
                    "effectively bypassed or absent."
                ),
            },
            {
                "claim": (
                    "SIBLING-CREDENTIAL RISK: subject svc-payments-api is now authenticated by TWO credentials "
                    f"— the Secrets Manager primary ({facts.cloudtrail.managed_secret_id or 'prod/payments/customer-records/token'}, "
                    "svc-payments-prod-v2) and the static env fallback (PAYMENTS_API_FALLBACK_TOKEN). "
                    "Rotating one does NOT invalidate the other."
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
        title = "Root cause: Friday deploy added a fallback token path + committed .env.release; a sibling credential survives rotation"
        summary = (
            f"The deploy diff touched {changed_files_text} and changed getServiceToken() to fail OPEN to a static "
            "env fallback (PAYMENTS_API_FALLBACK_TOKEN) behind ALLOW_FALLBACK_TOKEN. A new committed "
            f".env.release shipped that token plus CUSTOMER_EXPORT_ENABLED=true. The scanner flagged "
            f"{high_findings} high-severity unresolved finding(s) and the release still went out. Critically, "
            "subject svc-payments-api now has two credentials — the Secrets Manager primary and this static "
            "fallback — so rotating one leaves the other alive: containment must hit BOTH issuers and disable "
            "the fallback path, not just rotate the token."
        )
        root_cause = "ALLOW_FALLBACK_TOKEN fail-open path + committed .env.release (token + CUSTOMER_EXPORT_ENABLED)"
        credential_hunt = {
            "principal": "svc-payments-api",
            "credentialsAuthenticatingPrincipal": [
                {"name": "svc-payments-prod-v2", "issuer": "AWS Secrets Manager", "ref": facts.cloudtrail.managed_secret_id or "prod/payments/customer-records/token", "rotatingInvalidatesFallback": False},
                {"name": credential_label, "issuer": "static env (PAYMENTS_API_FALLBACK_TOKEN)", "ref": ".env.release", "rotatingInvalidatesPrimary": False},
            ],
            "legacyOrFallbackPaths": ["ALLOW_FALLBACK_TOKEN fail-open branch in getServiceToken()"],
            "mustAlsoCheck": [
                "Other services / repos / .env files referencing PAYMENTS_API_FALLBACK_TOKEN or ALLOW_FALLBACK_TOKEN",
                "CI/CD secret stores and built container images that may still carry the fallback value",
                "Whether the fallback value is reused as a credential anywhere else",
            ],
            "warning": "Rotating only the Secrets Manager primary would leave the exposed fallback usable; disabling only the fallback would not rotate the primary. Treat them as independent.",
        }
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="finding",
        title=title,
        summary=summary,
        confidence=0.91,
        severity="high",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact=(
            "Establishes the root-cause trust-policy change and warns that token revocation alone is incomplete while the wildcard can mint new sessions."
            if is_oidc
            else "Establishes the root-cause change AND warns that single-credential rotation would leave a sibling "
            "path usable — the classic incomplete-containment failure."
        ),
        next_action=(
            "Remediation must revoke active federated sessions, restore protected-ref OIDC trust, remove export scope from untrusted refs, and add policy-as-code guardrails."
            if is_oidc
            else "Remediation must disable the ALLOW_FALLBACK_TOKEN path, remove .env.release, invalidate the fallback "
            "at its issuer, AND confirm no other clone/CI/image still carries it; add a deploy-time secret-scan gate."
        ),
        payload={
            "kind": "finding",
            "data": {
                "findings": findings,
                "rootCauseChange": root_cause,
                "introducedBy": {
                    "release": "release-9814" if not is_oidc else "release-1007",
                    "changedFile": changed_files[0] if changed_files else "unknown",
                    "blob": diff_blob,
                    "newFile": "services/customer-records/.env.release" if not is_oidc else "services/customer-records/config/export-policy.json",
                    "commitSha": "not present in evidence packet — confirm with repo owner",
                },
                "pushProtection": (
                    "Not applicable: no static secret was committed; policy-as-code guardrails should catch the trust regression."
                    if is_oidc
                    else f"Bypassed or absent: {finding_refs} was high-severity and unresolved, yet the release shipped."
                ),
                "siblingCredentialHunt": credential_hunt,
                "limitations": [
                    "Token value in the patch is a redacted demo placeholder, not a usable secret."
                    if not is_oidc
                    else "The token label is redacted synthetic evidence; no usable federated credential is present.",
                    "No introducing commit SHA, repo name/branch, or image digest in the packet to fully pin propagation.",
                ],
                "derivedFacts": {
                    "source": "common.evidence_analysis.analyze_incident_evidence",
                    "changedFiles": changed_files,
                    "rootCauseKind": facts.code.root_cause_kind,
                    "rootCauseSummary": facts.code.root_cause_summary,
                    "riskyControls": facts.code.risky_controls,
                    "failOpenFallbackAdded": facts.code.fail_open_fallback_added,
                    "envReleaseAdded": facts.code.env_release_added,
                    "fallbackTokenVariableAdded": facts.code.fallback_token_variable_added,
                    "customerExportEnabledAdded": facts.code.customer_export_enabled_added,
                    "unresolvedHighSecretFindings": high_findings,
                },
            },
        },
    )


def _cross_review(ctx: AgentTurnContext) -> dict[str, Any]:
    facts = analyze_incident_evidence(ctx)
    records = facts.api.unauthorized_records_returned
    records_text = f"{records:,}"
    subject = facts.auth.subject or "svc-payments-api"
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    review_round_id = str(ctx.task.get("reviewRoundId") or f"review-{ctx.case['id'].lower()}-1")
    reviewed_message_ids = _latest_message_ids(
        ctx,
        {
            "agent-forensics": "finding",
            "agent-threat-intel": "finding",
        },
    )

    if is_oidc:
        containment_gap = (
            "Forensics can show the observed token/session is issuer-verified inactive, but containment is "
            "not complete until the GitHub OIDC trust condition is restored to protected refs and export scope "
            "is removed from untrusted workflow paths."
        )
        root_cause = facts.code.root_cause_summary or "OIDC trust wildcard + overbroad export scope"
        required_controls = [
            "Revoke active federated sessions",
            "Restore protected-ref OIDC trust conditions",
            "Remove customer export/payment-method scope from untrusted refs",
            "Add policy-as-code checks for repo-wide OIDC subject wildcards",
        ]
    else:
        containment_gap = (
            "Forensics can show the fallback token is issuer-verified inactive, but containment is not complete "
            "until the fallback path is disabled and the sibling Secrets Manager primary is independently rotated."
        )
        root_cause = "ALLOW_FALLBACK_TOKEN fail-open path + committed .env.release"
        required_controls = [
            "Rotate the exposed fallback credential at its issuer",
            "Disable the ALLOW_FALLBACK_TOKEN branch",
            "Independently rotate the Secrets Manager primary",
            "Block production deploys with unresolved high secret-scan findings",
        ]

    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="verification",
        title="Peer review: containment is incomplete without fixing the trust/control path",
        summary=(
            f"Reviewed Forensics and Threat Intel before the policy gate. Their evidence supports urgent containment: "
            f"{records_text} records were returned through the affected {subject} path and the abuse pattern is active, "
            f"not theoretical. My challenge is containment scope: {containment_gap} Risk should not let approval wording "
            "collapse to token rotation alone."
        ),
        confidence=0.89,
        severity="high",
        evidence_ids=sorted(set(_EVIDENCE + ["ev-api-gateway-logs", "ev-auth-events", "ev-ip-intel"])),
        target_agent_ids=["agent-commander"],
        decision_impact=(
            "Prevents a narrow containment plan that closes the observed credential but leaves the code, trust, "
            "or sibling-credential path capable of reintroducing access."
        ),
        next_action="Risk should require the approval request to include the full containment scope, not only the observed token/session.",
        payload={
            "kind": "cross_review_verification",
            "data": {
                "reviewRoundId": review_round_id,
                "reviewerAgentId": AGENT_ID,
                "reviewedAgentIds": ["agent-forensics", "agent-threat-intel"],
                "reviewedMessageIds": reviewed_message_ids,
                "verifiedClaims": [
                    f"Forensics' {records_text}-record exposure estimate is consistent with the root-cause change: {root_cause}.",
                    "Threat Intel's urgency is justified because the observed path is useful for bulk export and had a post-rotation retry.",
                ],
                "challengesPreserved": [
                    containment_gap,
                    "Do not mark the incident contained solely because the observed credential is dead.",
                    "Do not skip prevention controls; the same class can recur on the next deploy or workflow run.",
                ],
                "requiredContainmentControls": required_controls,
                "derivedFacts": {
                    "source": "common.evidence_analysis.analyze_incident_evidence",
                    "recordsReturnedToUnexpectedIps": records,
                    "rootCauseKind": facts.code.root_cause_kind,
                    "rootCauseSummary": facts.code.root_cause_summary,
                    "riskyControls": facts.code.risky_controls,
                    "unresolvedHighSecretFindings": facts.secret_scan.unresolved_high_count,
                },
            },
        },
    )


def _latest_message_ids(ctx: AgentTurnContext, wanted: dict[str, str]) -> list[str]:
    ids: list[str] = []
    for agent_id, message_type in wanted.items():
        for message in reversed(ctx.recent_messages):
            if message.get("agentId") == agent_id and message.get("type") == message_type and message.get("id"):
                ids.append(str(message["id"]))
                break
    return ids
