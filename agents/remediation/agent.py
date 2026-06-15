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

from common.schema import AgentTurnContext, build_message

AGENT_ID = "agent-remediation"
AGENT_NAME = "Remediation Agent"

_EVIDENCE = ["ev-code-diff", "ev-auth-events"]


def handle_turn(ctx: AgentTurnContext) -> dict[str, Any]:
    approved_scope = ctx.task.get("approvedScope") or [
        "Rotate fallback token",
        "Disable fallback token path",
    ]
    tasks = [
        {
            "id": "rem-001",
            "title": "Invalidate the exposed fallback token at its issuer (issuer-first containment)",
            "status": "done",
            "severity": "high",
            "rationale": (
                "The fallback bearer token for svc-payments-api was used by external IPs. Issuer-side "
                "revocation — not code cleanup — is what stops access. Issuer logs confirm it is now dead."
            ),
            "evidenceIds": ["ev-auth-events"],
            "acceptanceCriteria": [
                "Old fallback token returns 401/deny at the issuer (CONFIRMED: auth deny + gateway 401 at 21:12:02Z)",
                "No further 200s on the fallback token after 21:12:02Z",
            ],
            "rollbackPlan": "Do not re-enable the fallback token; if a service breaks, restore from the Secrets Manager primary, never the static fallback.",
        },
        {
            "id": "rem-002",
            "title": "Two-key rotate the Secrets Manager primary (svc-payments-prod-v2) — sibling credential",
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
        title="Issuer-first containment executed; sibling-credential rotation and federation queued",
        summary=(
            "Within the approved scope: the exposed fallback token is issuer-verified dead at 21:12:02Z and the "
            "fail-open path is being disabled. Flagging that containment is NOT complete on rotation alone — the "
            "sibling Secrets Manager primary needs an independent two-key rotation, the fallback value must be "
            "purged from CI/deploy/images to prevent recontamination, and the incident class should be collapsed "
            "by moving to short-lived federated credentials. The exposure window stays 'closed' only because the "
            "issuer denies the old token. External customer notification is intentionally excluded — not approved."
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
                "containmentOrder": "issuer-first (revoke/rotate at provider) before code and history cleanup; cleanup alone can recontaminate from old clones",
                "windowClosedCriterion": "Old credential issuer-verified inactive at 21:12:02Z (auth deny + gateway 401); window is only 'closed' because of this, not because of code deletion.",
                "siblingCredentialsToAddress": [
                    {"name": "svc-payments-fallback-redacted", "issuer": "static env (PAYMENTS_API_FALLBACK_TOKEN)", "state": "issuer-verified dead"},
                    {"name": "svc-payments-prod-v2", "issuer": "AWS Secrets Manager", "state": "two-key rotation in progress"},
                ],
                "excludedPendingApproval": ["External customer notification", "Incident closure"],
                "tasks": tasks,
            },
        },
    )
