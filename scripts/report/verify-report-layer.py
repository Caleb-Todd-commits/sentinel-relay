#!/usr/bin/env python3
"""Static verification for Step 9 final report and audit replay files.

This is intentionally dependency-light so teammates can run it before node_modules
are installed. It checks that the judge-facing report layer exists and that the
sample incident still contains the audit/report records Step 9 expects.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "apps/web/src/app/report/page.tsx",
    "apps/web/src/lib/report/auditReportModel.ts",
    "apps/web/src/lib/report/index.ts",
    "apps/web/src/components/report/ReportHero.tsx",
    "apps/web/src/components/report/ReportMetricsGrid.tsx",
    "apps/web/src/components/report/ReportSectionCard.tsx",
    "apps/web/src/components/report/EvidenceMatrix.tsx",
    "apps/web/src/components/report/AuditTrailTable.tsx",
    "apps/web/src/components/report/ApprovalDecisionRecord.tsx",
    "apps/web/src/components/report/RemediationReportCard.tsx",
    "apps/web/src/components/report/ReportIntegrityPanel.tsx",
    "apps/web/src/components/report/ReportExportPanel.tsx",
    "apps/web/src/components/report/OpenQuestionsCard.tsx",
    "docs/51_FINAL_REPORT_AND_AUDIT_REPLAY.md",
    "docs/52_REPORT_UI_COMPONENTS.md",
    "docs/53_REPORT_TRACEABILITY_MODEL.md",
    "docs/54_STEP9_VERIFICATION_REPORT.md",
    "docs/55_STEP9_TEAM_HANDOFF.md",
]

REQUIRED_REPORT_TERMS = [
    "AuditTrailRecord",
    "EvidenceMatrixRow",
    "ReportIntegrityCheck",
    "buildAuditReportModel",
    "buildAuditTrail",
    "buildEvidenceMatrix",
]

REQUIRED_PAGE_COMPONENTS = [
    "ReportHero",
    "ReportMetricsGrid",
    "ReportIntegrityPanel",
    "AuditTrailTable",
    "EvidenceMatrix",
    "RemediationReportCard",
    "ReportExportPanel",
]


def read_demo_json() -> dict:
    # The canonical sample incident is valid JSON and easier to verify than the TS export.
    path = ROOT / "packages/sample-data/demo_incident.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def assert_file(path: str) -> None:
    candidate = ROOT / path
    if not candidate.exists():
        raise SystemExit(f"Missing required file: {path}")


def assert_contains(path: str, terms: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [term for term in terms if term not in text]
    if missing:
        raise SystemExit(f"{path} missing required terms: {', '.join(missing)}")


def main() -> None:
    for path in REQUIRED_FILES:
        assert_file(path)

    assert_contains("apps/web/src/lib/report/auditReportModel.ts", REQUIRED_REPORT_TERMS)
    assert_contains("apps/web/src/app/report/page.tsx", REQUIRED_PAGE_COMPONENTS)

    incident = read_demo_json()
    report = incident.get("finalReport", {})
    messages = incident.get("messages", [])
    evidence = incident.get("evidence", [])
    tasks = incident.get("remediationTasks", [])

    if len(report.get("auditTrailMessageIds", [])) < 8:
        raise SystemExit("Final report must include at least 8 audit trail message IDs.")
    if len(report.get("sections", [])) < 5:
        raise SystemExit("Final report must include at least 5 sections.")
    if not any(message.get("type") == "challenge" for message in messages):
        raise SystemExit("Audit trail must include a visible challenge message.")
    if not any(message.get("type") == "approval_decision" for message in messages):
        raise SystemExit("Audit trail must include an approval decision message.")
    if len(evidence) < 5:
        raise SystemExit("Demo incident should include at least 5 evidence items.")
    if len(tasks) < 4:
        raise SystemExit("Demo incident should include at least 4 remediation tasks.")

    print("Step 9 report layer verification passed.")
    print(f"Report sections: {len(report.get('sections', []))}")
    print(f"Audit events: {len(report.get('auditTrailMessageIds', []))}")
    print(f"Evidence items: {len(evidence)}")
    print(f"Remediation tasks: {len(tasks)}")


if __name__ == "__main__":
    main()
