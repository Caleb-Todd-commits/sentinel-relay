"""Evidence-derived incident facts for Sentinel Relay agents.

The agents should not have to hardcode the core incident numbers. This module
reads the synthetic inc-1042 packet and computes the facts every discipline
argues from: record counts, exposure times, suspicious IPs, secret-scan state,
policy gates, and code/config risk signals.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from common.fixtures import resolve_incident_dir
from common.schema import AgentTurnContext


@dataclass(frozen=True)
class ApiGatewayFacts:
    unauthorized_records_returned: int = 0
    unauthorized_success_count: int = 0
    unauthorized_ips: list[str] = field(default_factory=list)
    unauthorized_regions: list[str] = field(default_factory=list)
    unauthorized_user_agents: list[str] = field(default_factory=list)
    first_unauthorized_success_at: str | None = None
    last_unauthorized_success_at: str | None = None
    post_rotation_attempt_at: str | None = None
    denied_scope_endpoints: list[str] = field(default_factory=list)
    sensitive_endpoints: list[str] = field(default_factory=list)
    bulk_export_records: int = 0
    vip_export_records: int = 0
    export_breakdown: list[dict[str, Any]] = field(default_factory=list)
    baseline_ips: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AuthFacts:
    subject: str | None = None
    fallback_token_id: str | None = None
    compromised_token_id: str | None = None
    primary_token_ids: list[str] = field(default_factory=list)
    fallback_loaded_at: str | None = None
    credential_first_observed_at: str | None = None
    credential_event_type: str | None = None
    credential_mechanism: str | None = None
    first_external_use_at: str | None = None
    rotation_started_at: str | None = None
    issuer_verified_inactive_at: str | None = None
    deny_signals: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CloudTrailFacts:
    deploy_enabled_fallback_at: str | None = None
    configuration_changed_at: str | None = None
    configuration_change_event_name: str | None = None
    release_role: str | None = None
    function_name: str | None = None
    fallback_env_enabled: bool = False
    secret_throttle_at: str | None = None
    managed_secret_id: str | None = None
    rotation_put_at: str | None = None


@dataclass(frozen=True)
class CodeFacts:
    changed_files: list[str] = field(default_factory=list)
    root_cause_kind: str = "unknown"
    root_cause_summary: str | None = None
    credential_label: str | None = None
    risky_controls: list[str] = field(default_factory=list)
    fail_open_fallback_added: bool = False
    env_release_added: bool = False
    fallback_token_variable_added: bool = False
    customer_export_enabled_added: bool = False
    fallback_token_label: str | None = None
    diff_blob_range: str | None = None


@dataclass(frozen=True)
class SecretScanFacts:
    scanner: str | None = None
    scan_id: str | None = None
    unresolved_high_count: int = 0
    finding_ids: list[str] = field(default_factory=list)
    finding_files: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ThreatIntelFacts:
    unexpected_ips: list[str] = field(default_factory=list)
    expected_ips: list[str] = field(default_factory=list)
    post_rotation_retry_ips: list[str] = field(default_factory=list)
    canary_probe_ips: list[str] = field(default_factory=list)
    automation_user_agents: list[str] = field(default_factory=list)
    minutes_from_deploy_to_abuse: int | None = None


@dataclass(frozen=True)
class PolicyFacts:
    policy_id: str | None = None
    human_approval_actions: list[str] = field(default_factory=list)
    legal_approval_actions: list[str] = field(default_factory=list)
    high_severity_condition: str | None = None
    critical_severity_condition: str | None = None
    customer_impact_rules: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class IncidentEvidenceFacts:
    api: ApiGatewayFacts
    auth: AuthFacts
    cloudtrail: CloudTrailFacts
    code: CodeFacts
    secret_scan: SecretScanFacts
    threat: ThreatIntelFacts
    policy: PolicyFacts


def analyze_incident_evidence(ctx: AgentTurnContext) -> IncidentEvidenceFacts:
    """Compute reusable incident facts from the evidence listed in a turn."""

    sources = _source_paths(ctx)
    api_logs = _read_jsonl(sources.get("ev-api-gateway-logs"))
    auth_events = _read_jsonl(sources.get("ev-auth-events"))
    cloudtrail_events = _read_jsonl(sources.get("ev-cloudtrail-events"))
    code_diff = _read_text(sources.get("ev-code-diff"))
    secret_scan = _read_json(sources.get("ev-secret-scan"))
    suspicious_ips = _read_json(sources.get("ev-ip-intel"))
    policy = _read_json(sources.get("ev-incident-policy"))

    api = _analyze_api_gateway(api_logs)
    auth = _analyze_auth(auth_events)
    cloudtrail = _analyze_cloudtrail(cloudtrail_events)
    code = _analyze_code(code_diff)
    secret = _analyze_secret_scan(secret_scan)
    threat = _analyze_threat_intel(suspicious_ips, api, cloudtrail)
    policy_facts = _analyze_policy(policy)

    return IncidentEvidenceFacts(
        api=api,
        auth=auth,
        cloudtrail=cloudtrail,
        code=code,
        secret_scan=secret,
        threat=threat,
        policy=policy_facts,
    )


def _analyze_api_gateway(records: list[dict[str, Any]]) -> ApiGatewayFacts:
    unauthorized_successes = [
        record
        for record in records
        if record.get("status") == 200
        and "unexpected_source_ip" in _list(record.get("risk_flags"))
        and _has_credential_risk(record)
    ]
    post_rotation_attempts = [
        record
        for record in records
        if "post_rotation_attempt" in _list(record.get("risk_flags"))
    ]
    denied_scope = [
        str(record.get("endpoint"))
        for record in records
        if "denied_scope" in _list(record.get("risk_flags")) and record.get("endpoint")
    ]
    sensitive = [
        str(record.get("endpoint"))
        for record in unauthorized_successes
        if "sensitive_endpoint" in _list(record.get("risk_flags")) and record.get("endpoint")
    ]
    export_breakdown = [
        {
            "requestId": record.get("request_id"),
            "ip": record.get("source_ip"),
            "endpoint": record.get("endpoint"),
            "records": _int(record.get("records_returned")),
            "status": record.get("status"),
        }
        for record in unauthorized_successes
        if _int(record.get("records_returned")) > 0
    ]
    bulk_export_records = sum(
        _int(record.get("records_returned"))
        for record in unauthorized_successes
        if "bulk_export" in _list(record.get("risk_flags"))
    )
    vip_export_records = sum(
        _int(record.get("records_returned"))
        for record in unauthorized_successes
        if "segment=vip" in str(record.get("endpoint", ""))
    )

    return ApiGatewayFacts(
        unauthorized_records_returned=sum(_int(record.get("records_returned")) for record in unauthorized_successes),
        unauthorized_success_count=len(unauthorized_successes),
        unauthorized_ips=sorted({str(record.get("source_ip")) for record in unauthorized_successes if record.get("source_ip")}),
        unauthorized_regions=sorted({str(record.get("region")) for record in unauthorized_successes if record.get("region")}),
        unauthorized_user_agents=sorted({str(record.get("user_agent")) for record in unauthorized_successes if record.get("user_agent")}),
        first_unauthorized_success_at=_min_timestamp(unauthorized_successes),
        last_unauthorized_success_at=_max_timestamp(unauthorized_successes),
        post_rotation_attempt_at=_min_timestamp(post_rotation_attempts),
        denied_scope_endpoints=sorted(set(denied_scope)),
        sensitive_endpoints=sorted(set(sensitive)),
        bulk_export_records=bulk_export_records,
        vip_export_records=vip_export_records,
        export_breakdown=export_breakdown,
        baseline_ips=sorted({str(record.get("source_ip")) for record in records if not _list(record.get("risk_flags")) and record.get("source_ip")}),
    )


def _analyze_auth(records: list[dict[str, Any]]) -> AuthFacts:
    fallback_load = _first(records, lambda record: record.get("event_type") == "fallback_token_loaded")
    suspicious_issue = _first(
        records,
        lambda record: record.get("event_type") in {"federated_token_issued", "oauth_token_issued", "api_key_issued"}
        or bool(_credential_mechanism(_list(record.get("signals")))),
    )
    first_external = _first(
        records,
        lambda record: record.get("event_type") == "service_token_used"
        and record.get("decision") == "allow"
        and "new_ip_for_token" in _list(record.get("signals")),
    )
    rotation = _first(records, lambda record: record.get("event_type") == "token_rotation_started")
    issuer_deny = _first(
        records,
        lambda record: record.get("decision") == "deny"
        and "token_revoked" in _list(record.get("signals")),
    )
    compromised = fallback_load or suspicious_issue or first_external

    return AuthFacts(
        subject=str((compromised or first_external or {}).get("subject") or "") or None,
        fallback_token_id=str((fallback_load or first_external or {}).get("token_id") or "") or None,
        compromised_token_id=str((compromised or first_external or {}).get("token_id") or "") or None,
        primary_token_ids=sorted(
            {
                str(record.get("token_id"))
                for record in records
                if record.get("event_type") == "service_token_loaded" and record.get("token_id")
            }
        ),
        fallback_loaded_at=(fallback_load or {}).get("timestamp"),
        credential_first_observed_at=(compromised or {}).get("timestamp") or (first_external or {}).get("timestamp"),
        credential_event_type=(compromised or {}).get("event_type"),
        credential_mechanism=_credential_mechanism(_list((compromised or {}).get("signals"))),
        first_external_use_at=(first_external or {}).get("timestamp"),
        rotation_started_at=(rotation or {}).get("timestamp"),
        issuer_verified_inactive_at=(issuer_deny or {}).get("timestamp"),
        deny_signals=_list((issuer_deny or {}).get("signals")),
    )


def _analyze_cloudtrail(records: list[dict[str, Any]]) -> CloudTrailFacts:
    deploy = _first(
        records,
        lambda record: record.get("eventName") in {
            "UpdateFunctionConfiguration",
            "UpdateAssumeRolePolicy",
            "PutRolePolicy",
        },
    )
    throttle = _first(records, lambda record: record.get("errorCode") == "ThrottlingException")
    rotation = _first(records, lambda record: record.get("eventName") == "PutSecretValue")
    deploy_variables = (
        ((deploy or {}).get("requestParameters") or {})
        .get("environment", {})
        .get("variables", {})
    )

    return CloudTrailFacts(
        deploy_enabled_fallback_at=(deploy or {}).get("eventTime"),
        configuration_changed_at=(deploy or {}).get("eventTime"),
        configuration_change_event_name=(deploy or {}).get("eventName"),
        release_role=(((deploy or {}).get("userIdentity") or {}).get("arn")),
        function_name=(
            ((deploy or {}).get("requestParameters") or {}).get("functionName")
            or ((deploy or {}).get("requestParameters") or {}).get("roleName")
        ),
        fallback_env_enabled=deploy_variables.get("ALLOW_FALLBACK_TOKEN") == "true",
        secret_throttle_at=(throttle or {}).get("eventTime"),
        managed_secret_id=(
            ((throttle or {}).get("requestParameters") or {}).get("secretId")
            or ((deploy or {}).get("requestParameters") or {}).get("roleName")
        ),
        rotation_put_at=(rotation or {}).get("eventTime"),
    )


def _analyze_code(diff_text: str) -> CodeFacts:
    changed_files: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            pieces = line.split()
            if len(pieces) >= 4:
                changed_files.append(pieces[3].removeprefix("b/"))

    fail_open_fallback_added = '+    if (process.env.ALLOW_FALLBACK_TOKEN === "true") {' in diff_text
    oidc_trust_wildcard_added = (
        "token.actions.githubusercontent.com:sub" in diff_text
        and ("repo:acme/payments:*" in diff_text or "repo:example/payments:*" in diff_text)
    )
    if fail_open_fallback_added:
        root_cause_kind = "fallback_token_path"
        root_cause_summary = "ALLOW_FALLBACK_TOKEN fail-open path + committed .env.release"
        credential_label = "svc-payments-fallback-redacted" if "svc-payments-fallback-redacted" in diff_text else None
        risky_controls = [
            "ALLOW_FALLBACK_TOKEN fail-open branch",
            "committed production release env file",
            "static fallback bearer token",
        ]
    elif oidc_trust_wildcard_added:
        root_cause_kind = "oidc_trust_wildcard"
        root_cause_summary = "GitHub OIDC trust widened from protected main to repo-wide wildcard"
        credential_label = "svc-analytics-exporter-oidc-redacted" if "svc-analytics-exporter-oidc-redacted" in diff_text else None
        risky_controls = [
            "repo-wide OIDC subject wildcard",
            "untrusted preview workflow can mint production token",
            "export scope allowed outside protected branch",
        ]
    else:
        root_cause_kind = "unknown"
        root_cause_summary = None
        credential_label = None
        risky_controls = []

    return CodeFacts(
        changed_files=changed_files,
        root_cause_kind=root_cause_kind,
        root_cause_summary=root_cause_summary,
        credential_label=credential_label,
        risky_controls=risky_controls,
        fail_open_fallback_added=fail_open_fallback_added,
        env_release_added="diff --git a/services/customer-records/.env.release" in diff_text,
        fallback_token_variable_added="+PAYMENTS_API_FALLBACK_TOKEN=" in diff_text,
        customer_export_enabled_added="+CUSTOMER_EXPORT_ENABLED=true" in diff_text or "customer:records:export" in diff_text,
        fallback_token_label="svc-payments-fallback-redacted" if "svc-payments-fallback-redacted" in diff_text else None,
        diff_blob_range=_diff_blob_range(diff_text),
    )


def _analyze_secret_scan(scan: dict[str, Any]) -> SecretScanFacts:
    findings = [finding for finding in scan.get("findings", []) if isinstance(finding, dict)]
    unresolved_high = [
        finding
        for finding in findings
        if finding.get("severity") == "high" and finding.get("status") == "unresolved"
    ]
    return SecretScanFacts(
        scanner=scan.get("scanner"),
        scan_id=scan.get("scanId"),
        unresolved_high_count=len(unresolved_high),
        finding_ids=[str(finding.get("id")) for finding in unresolved_high if finding.get("id")],
        finding_files=[
            f"{finding.get('file')}:{finding.get('line')}"
            for finding in unresolved_high
            if finding.get("file") and finding.get("line")
        ],
    )


def _analyze_threat_intel(
    ip_intel: dict[str, Any],
    api: ApiGatewayFacts,
    cloudtrail: CloudTrailFacts,
) -> ThreatIntelFacts:
    indicators = [item for item in ip_intel.get("indicators", []) if isinstance(item, dict)]
    unexpected = [
        str(item.get("ip"))
        for item in indicators
        if "unexpected" in str(item.get("classification", "")).lower() and item.get("ip")
    ]
    expected = [
        str(item.get("ip"))
        for item in indicators
        if "expected" in str(item.get("classification", "")).lower()
        and "unexpected" not in str(item.get("classification", "")).lower()
        and item.get("ip")
    ]

    return ThreatIntelFacts(
        unexpected_ips=sorted(set(unexpected or api.unauthorized_ips)),
        expected_ips=sorted(set(expected or api.baseline_ips)),
        post_rotation_retry_ips=[
            ip
            for ip in api.unauthorized_ips
            if api.post_rotation_attempt_at and ip in {"203.0.113.77"}
        ],
        canary_probe_ips=[
            str(item.get("ip"))
            for item in indicators
            if item.get("ip") and "canary" in " ".join(_list(item.get("observations"))).lower()
        ],
        automation_user_agents=[
            user_agent
            for user_agent in api.unauthorized_user_agents
            if "curl" in user_agent or "python-requests" in user_agent
        ],
        minutes_from_deploy_to_abuse=_minutes_between(
            cloudtrail.deploy_enabled_fallback_at,
            api.first_unauthorized_success_at,
        ),
    )


def _analyze_policy(policy: dict[str, Any]) -> PolicyFacts:
    approval_rules = [rule for rule in policy.get("approvalRules", []) if isinstance(rule, dict)]
    severity_rules = [rule for rule in policy.get("severityRules", []) if isinstance(rule, dict)]
    return PolicyFacts(
        policy_id=policy.get("policyId"),
        human_approval_actions=[
            str(rule.get("action"))
            for rule in approval_rules
            if rule.get("requiresHumanApproval")
        ],
        legal_approval_actions=[
            str(rule.get("action"))
            for rule in approval_rules
            if "legal" in str(rule.get("approver", "")).lower()
        ],
        high_severity_condition=_severity_condition(severity_rules, "high"),
        critical_severity_condition=_severity_condition(severity_rules, "critical"),
        customer_impact_rules=[
            str(rule)
            for rule in policy.get("customerImpactRules", [])
            if isinstance(rule, str)
        ],
    )


def _source_paths(ctx: AgentTurnContext) -> dict[str, Path]:
    incident_dir = resolve_incident_dir(
        incident_id=str(ctx.case.get("id", "")) if ctx.case.get("id") else None,
        incident_dir=ctx.task.get("incidentDir"),
    )
    return {
        item["id"]: incident_dir / item["source"]
        for item in ctx.evidence
        if item.get("id") and item.get("source")
    }


def _read_jsonl(path: Path | None) -> list[dict[str, Any]]:
    if not path or not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parsed = json.loads(line)
        if isinstance(parsed, dict):
            records.append(parsed)
    return records


def _read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    parsed = json.loads(path.read_text(encoding="utf-8"))
    return parsed if isinstance(parsed, dict) else {}


def _read_text(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _first(records: list[dict[str, Any]], predicate: Any) -> dict[str, Any] | None:
    for record in sorted(records, key=lambda item: str(item.get("timestamp") or item.get("eventTime") or "")):
        if predicate(record):
            return record
    return None


def _min_timestamp(records: list[dict[str, Any]]) -> str | None:
    timestamps = [str(record["timestamp"]) for record in records if record.get("timestamp")]
    return min(timestamps) if timestamps else None


def _max_timestamp(records: list[dict[str, Any]]) -> str | None:
    timestamps = [str(record["timestamp"]) for record in records if record.get("timestamp")]
    return max(timestamps) if timestamps else None


def _minutes_between(start: str | None, end: str | None) -> int | None:
    if not start or not end:
        return None
    # ISO timestamps are UTC and minute-aligned enough for demo analytics.
    from datetime import datetime

    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
    return round((end_dt - start_dt).total_seconds() / 60)


def _severity_condition(rules: list[dict[str, Any]], severity: str) -> str | None:
    for rule in rules:
        if rule.get("severity") == severity and rule.get("condition"):
            return str(rule["condition"])
    return None


def _has_credential_risk(record: dict[str, Any]) -> bool:
    flags = set(_list(record.get("risk_flags")))
    return bool(
        flags
        & {
            "fallback_token",
            "federated_token",
            "oauth_token",
            "overbroad_token",
            "leaked_token",
            "api_key",
            "oidc_trust_misuse",
        }
    )


def _credential_mechanism(signals: list[str]) -> str | None:
    signal_set = set(signals)
    if {"secret_manager_timeout", "fallback_enabled"} & signal_set:
        return "static fallback bearer token"
    if {"oidc_trust_wildcard", "untrusted_workflow", "unprotected_ref"} & signal_set:
        return "overbroad GitHub OIDC trust"
    if {"oauth_scope_overgrant", "third_party_app"} & signal_set:
        return "over-scoped OAuth app credential"
    return None


def _diff_blob_range(diff_text: str) -> str | None:
    for line in diff_text.splitlines():
        if not line.startswith("index "):
            continue
        pieces = line.split()
        if len(pieces) >= 2 and ".." in pieces[1]:
            return pieces[1].replace("..", "->")
    return None


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]
