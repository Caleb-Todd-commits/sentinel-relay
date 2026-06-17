"""Remediation agent business logic (agents lane).

Produces an approval-scoped containment and fix plan. Only executes the actions
the human approver authorized; deferred actions are left out. Deterministic in
mock mode.

Analytic doctrine (see remediation/prompt.md): issuer-first two-key rotation
(create new, cut over, verify health and logs, then disable old), kill fallback
and legacy auth paths and stale CI secrets, insist the old credential is
issuer-verified dead before calling the window closed, and recommend collapsing
the incident class via short-lived federated credentials.
"""

from __future__ import annotations

from typing import Any

from common.evidence_analysis import analyze_incident_evidence
from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-remediation"
AGENT_NAME = "Remediation Agent"

_EVIDENCE = ["ev-code-diff", "ev-auth-events"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    facts = analyze_incident_evidence(ctx)
    is_oidc = facts.code.root_cause_kind == "oidc_trust_wildcard"
    approved_scope = ctx.task.get("approvedScope") or (
        ["Revoke federated sessions", "Tighten OIDC trust policy"]
        if is_oidc
        else ["Rotate fallback token", "Disable fallback token path"]
    )
    fallback_token = facts.auth.compromised_token_id or facts.auth.fallback_token_id or "svc-payments-fallback-redacted"
    primary_token = facts.auth.primary_token_ids[0] if facts.auth.primary_token_ids else "svc-payments-prod-v2"
    managed_secret = facts.cloudtrail.managed_secret_id or "prod/payments/customer-records/token"
    issuer_closed_at = facts.auth.issuer_verified_inactive_at or facts.api.post_rotation_attempt_at or "21:12:02Z"
    if is_oidc:
        primary_token = facts.auth.primary_token_ids[0] if facts.auth.primary_token_ids else "svc-analytics-exporter-prod"
        managed_secret = facts.cloudtrail.managed_secret_id or "customer-records-github-oidc-exporter"
        tasks = [
            {
                "id": "rem-001",
                "title": "Revoke active federated sessions for the exporter role",
                "status": "done",
                "severity": "high",
                "rationale": (
                    f"The OIDC-issued token {fallback_token} for {facts.auth.subject or 'svc-analytics-exporter'} was used by external IPs. "
                    "Issuer-side session invalidation is what stops active access."
                ),
                "evidenceIds": ["ev-auth-events"],
                "acceptanceCriteria": [
                    f"Old federated token returns 401/deny at the issuer (CONFIRMED: auth deny + gateway 401 at {issuer_closed_at})",
                    f"No further 200s on the federated token after {issuer_closed_at}",
                ],
                "rollbackPlan": "Do not restore the wildcard trust; if deploys break, issue a protected-ref-only emergency role.",
            },
            {
                "id": "rem-002",
                "title": "Restore GitHub OIDC trust to protected refs only",
                "status": "in_progress",
                "severity": "high",
                "rationale": "The repo-wide subject wildcard can mint new production-scoped sessions until the trust policy is tightened.",
                "evidenceIds": ["ev-code-diff"],
                "acceptanceCriteria": [
                    "token.actions.githubusercontent.com:sub is limited to protected main/release refs",
                    "Pull request and preview refs cannot assume the exporter role",
                    "CloudTrail shows denied AssumeRoleWithWebIdentity for the prior untrusted ref",
                ],
                "rollbackPlan": "Use a separate least-privilege preview role instead of widening the production exporter role.",
            },
            {
                "id": "rem-003",
                "title": "Remove export/payment-method scope from untrusted workflow paths",
                "status": "in_progress",
                "severity": "high",
                "rationale": "The federated role gained customer:records:export and customer:payment-methods:read outside protected branches.",
                "evidenceIds": ["ev-code-diff"],
                "acceptanceCriteria": [
                    "Untrusted refs have no customer:records:export permission",
                    "Payment-method reads require protected deployment identity",
                    "Policy test proves preview workflows receive least-privilege scope",
                ],
                "rollbackPlan": "Temporarily disable preview exports rather than granting production data scope.",
            },
            {
                "id": "rem-004",
                "title": "Scan IAM trust policies for repo-wide OIDC wildcards",
                "status": "todo",
                "severity": "medium",
                "rationale": "This was a policy boundary failure; traditional secret scanning found no high secret finding.",
                "evidenceIds": ["ev-code-diff"],
                "acceptanceCriteria": [
                    "CI fails on repo:* OIDC subjects for production roles",
                    "Exceptions require Security Lead approval and expiry",
                ],
                "rollbackPlan": "Manual security override only with an audit-log entry.",
            },
            {
                "id": "rem-005",
                "title": "Split preview and production workload identities",
                "status": "todo",
                "severity": "medium",
                "rationale": "Federation is still the right direction; the fix is least-privilege trust boundaries, not static fallback tokens.",
                "evidenceIds": ["ev-code-diff"],
                "acceptanceCriteria": [
                    "Preview workflows use a separate no-customer-data role",
                    "Production exporter role only trusts protected refs",
                ],
                "rollbackPlan": "Disable preview export jobs until the split is complete.",
            },
            {
                "id": "rem-006",
                "title": "Add deploy-time OIDC trust-policy regression tests",
                "status": "todo",
                "severity": "medium",
                "rationale": "The release changed trust from StringEquals protected ref to StringLike wildcard; policy tests should block that.",
                "evidenceIds": ["ev-code-diff"],
                "acceptanceCriteria": ["CI fails on protected-ref downgrade", "Safe protected-ref trust policy passes"],
                "rollbackPlan": "Manual security override only with Security Lead and IAM owner sign-off.",
            },
        ]
    else:
        tasks = [
            {
                "id": "rem-001",
                "title": "Invalidate the exposed fallback token at its issuer (issuer-first containment)",
                "status": "done",
                "severity": "high",
                "rationale": (
                    f"The fallback bearer token {fallback_token} for svc-payments-api was used by external IPs. Issuer-side "
                    "revocation — not code cleanup — is what stops access. Issuer logs confirm it is now dead."
                ),
                "evidenceIds": ["ev-auth-events"],
                "acceptanceCriteria": [
                    f"Old fallback token returns 401/deny at the issuer (CONFIRMED: auth deny + gateway 401 at {issuer_closed_at})",
                    f"No further 200s on the fallback token after {issuer_closed_at}",
                ],
                "rollbackPlan": "Do not re-enable the fallback token; if a service breaks, restore from the Secrets Manager primary, never the static fallback.",
            },
            {
                "id": "rem-002",
                "title": f"Two-key rotate the Secrets Manager primary ({primary_token}) — sibling credential",
                "status": "in_progress",
                "severity": "high",
                "rationale": (
                    "Same identity (svc-payments-api) is authenticated by the managed primary too. Per Code Review, "
                    "rotating one credential leaves the sibling alive, so the primary must be rotated independently: "
                    "create new version, cut services over, verify health and logs, THEN disable the old version."
                ),
                "evidenceIds": ["ev-code-diff"],
                "acceptanceCriteria": [
                    "New primary version live and serving svc-payments-api with no errors",
                    "Old primary version disabled and failing auth",
                    "Dependent services healthy on the new version before old is cut",
                ],
                "rollbackPlan": "Keep the previous primary version staged-disabled (not deleted) until the new version is verified, then destroy.",
            },
            {
                "id": "rem-003",
                "title": "Disable ALLOW_FALLBACK_TOKEN fail-open path and remove .env.release",
                "status": "in_progress",
                "severity": "high",
                "rationale": "The fail-open fallback branch plus committed .env.release is the root-cause exposure mechanism; the auth path must fail closed.",
                "evidenceIds": ["ev-code-diff"],
                "acceptanceCriteria": ["getServiceToken() fails closed on Secrets Manager error", ".env.release removed from repo and build", "Secret-pattern unit test added"],
                "rollbackPlan": "Never restore the token-like fallback; revert only surrounding config if the deploy breaks.",
            },
            {
                "id": "rem-004",
                "title": "Purge the fallback value from CI/CD secrets, deploy env, and built images",
                "status": "todo",
                "severity": "high",
                "rationale": "Old clones, CI secret stores, and container image layers can recontaminate after rotation; code/history cleanup is secondary to issuer revocation but still required to prevent reuse.",
                "evidenceIds": ["ev-code-diff"],
                "acceptanceCriteria": [
                    "No PAYMENTS_API_FALLBACK_TOKEN / ALLOW_FALLBACK_TOKEN in CI variables, deploy config, or image layers",
                    "Deploy system no longer sources the fallback value",
                ],
                "rollbackPlan": "Manual security override only with an audit-log entry.",
            },
            {
                "id": "rem-005",
                "title": "Collapse the incident class: move to short-lived federated credentials",
                "status": "todo",
                "severity": "medium",
                "rationale": "Static long-lived service tokens are the root incident class. Federated short-lived credentials remove the standing secret entirely.",
                "evidenceIds": ["ev-code-diff"],
                "acceptanceCriteria": [
                    "CI uses AWS OIDC for GitHub Actions (no long-lived secret in CI)",
                    "Runtime uses Workload Identity Federation / short-lived tokens; no static fallback token exists to leak",
                ],
                "rollbackPlan": "Phase in behind a flag; fall back to the rotated Secrets Manager primary (never the static token) if federation has issues.",
            },
            {
                "id": "rem-006",
                "title": "Add deploy-time secret-scan guardrail in CI",
                "status": "todo",
                "severity": "medium",
                "rationale": "secret-1042-001 was high-severity but UNRESOLVED and the release shipped anyway; block token-like values before deploy.",
                "evidenceIds": ["ev-code-diff"],
                "acceptanceCriteria": ["CI fails on unresolved high secret findings", "Safe placeholder passes"],
                "rollbackPlan": "Manual security override only with an audit-log entry.",
            },
        ]
    return build_message(
        sequence=ctx.sequence,
        agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        case_id=ctx.case["id"],
        room_id=ctx.room_id,
        message_type="remediation_task",
        title=(
            "Issuer-first containment executed; OIDC trust rollback and scope reduction queued"
            if is_oidc
            else "Issuer-first containment executed; sibling-credential rotation and federation queued"
        ),
        summary=(
            (
                f"Within the approved scope: the OIDC-issued token is issuer-verified dead at {issuer_closed_at} "
                "and the GitHub OIDC trust policy is being restored to protected refs only. Flagging that containment "
                "is NOT complete on token revocation alone — the wildcard trust can mint another session until it is "
                "rolled back, export/payment-method scope must be removed from untrusted refs, and preview and "
                "production identities should be split. External customer notification is intentionally excluded — not approved."
            )
            if is_oidc
            else (
                f"Within the approved scope: the exposed fallback token is issuer-verified dead at {issuer_closed_at} and the "
                "fail-open path is being disabled. Flagging that containment is NOT complete on rotation alone — the "
                "sibling Secrets Manager primary needs an independent two-key rotation, the fallback value must be "
                "purged from CI/deploy/images to prevent recontamination, and the incident class should be collapsed "
                "by moving to short-lived federated credentials. The exposure window stays 'closed' only because the "
                "issuer denies the old token. External customer notification is intentionally excluded — not approved."
            )
        ),
        confidence=0.92,
        severity="high",
        evidence_ids=_EVIDENCE,
        target_agent_ids=["agent-commander"],
        decision_impact="Moves the case into controlled, approval-bounded remediation while preventing the rotate-one-leave-a-sibling failure.",
        next_action="Commander can generate the final audit report; notification decisions remain with the human + Legal.",
        payload={
            "kind": "remediation_task",
            "data": {
                "approvedScope": approved_scope,
                "containmentOrder": (
                    "issuer-first (revoke active federated sessions) before policy cleanup; trust rollback prevents minting new sessions"
                    if is_oidc
                    else "issuer-first (revoke/rotate at provider) before code and history cleanup; cleanup alone can recontaminate from old clones"
                ),
                "windowClosedCriterion": (
                    f"Old federated credential issuer-verified inactive at {issuer_closed_at} (auth deny + gateway 401); window is only 'closed' because active sessions are denied and trust is being tightened."
                    if is_oidc
                    else f"Old credential issuer-verified inactive at {issuer_closed_at} (auth deny + gateway 401); window is only 'closed' because of this, not because of code deletion."
                ),
                "siblingCredentialsToAddress": (
                    [
                        {"name": fallback_token, "issuer": "GitHub OIDC / AWS STS", "ref": managed_secret, "state": "issuer-verified dead"},
                        {"name": primary_token, "issuer": "production workload identity", "ref": "protected main deployment", "state": "review for scope parity"},
                    ]
                    if is_oidc
                    else [
                        {"name": fallback_token, "issuer": "static env (PAYMENTS_API_FALLBACK_TOKEN)", "state": "issuer-verified dead"},
                        {"name": primary_token, "issuer": "AWS Secrets Manager", "ref": managed_secret, "state": "two-key rotation in progress"},
                    ]
                ),
                "excludedPendingApproval": ["External customer notification", "Incident closure"],
                "tasks": tasks,
                "derivedFacts": {
                    "source": "common.evidence_analysis.analyze_incident_evidence",
                    "issuerVerifiedInactiveAt": issuer_closed_at,
                    "managedSecretId": managed_secret,
                    "fallbackTokenId": fallback_token,
                    "primaryTokenIds": facts.auth.primary_token_ids,
                    "rootCauseKind": facts.code.root_cause_kind,
                },
            },
        },
    )
