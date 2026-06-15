"""Load the inc-1042 incident packet into agent-facing context objects.

Reads only the synthetic lab fixtures under ``data/incidents/inc-1042`` (real
log shapes, redacted values, documentation-range IPs). No network, no secrets.

The canonical case / state / agent-profile shapes mirror
``packages/schemas/examples/demo_incident.json`` but are defined here so the
agents lane runs standalone. Evidence is loaded live from the inc-1042 manifest
so the evidence board shows real items with real IDs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common.schema import deterministic_timestamp

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INCIDENT_DIR = _REPO_ROOT / "data" / "incidents" / "inc-1042"

CASE_ID = "INC-1042"
ROOM_ID = "band-room-inc-1042"

# Which agent is treated as the collector for each evidence kind.
_COLLECTOR_BY_KIND = {
    "log": "agent-forensics",
    "code_diff": "agent-code-review",
    "configuration": "agent-code-review",
    "external_indicator": "agent-threat-intel",
    "policy": "agent-risk-compliance",
}
_CONFIDENCE_BY_KIND = {
    "log": 0.86,
    "code_diff": 0.91,
    "configuration": 0.9,
    "external_indicator": 0.74,
    "policy": 0.96,
}

# Agent roster (AgentProfile shape from the shared schema).
AGENT_PROFILES: dict[str, dict[str, Any]] = {
    "agent-commander": {
        "id": "agent-commander",
        "name": "Band Leader",
        "shortName": "Band Leader",
        "kind": "ai_agent",
        "role": "Case coordination and task routing",
        "responsibility": "Opens the room, assigns specialists, maintains state, requests human approval, and generates the final report.",
        "capability": "case_command",
        "status": "working",
        "allowedDecisions": ["assign tasks", "request approval", "generate report"],
        "requiresHumanApprovalFor": ["production containment", "external customer notification", "closing incident"],
    },
    "agent-forensics": {
        "id": "agent-forensics",
        "name": "Forensics Agent",
        "shortName": "Forensics",
        "kind": "ai_agent",
        "role": "Log analysis and evidence timeline",
        "responsibility": "Quantifies exposure from gateway, auth, and CloudTrail logs.",
        "capability": "log_forensics",
        "status": "idle",
        "allowedDecisions": ["submit evidence-backed findings", "build timeline events"],
        "requiresHumanApprovalFor": ["declaring customer impact", "revoking production credentials"],
    },
    "agent-threat-intel": {
        "id": "agent-threat-intel",
        "name": "Threat Intel Agent",
        "shortName": "Threat Intel",
        "kind": "ai_agent",
        "role": "Indicator and behavior assessment",
        "responsibility": "Assesses source IPs and behavior without overstating weak indicators.",
        "capability": "threat_assessment",
        "status": "idle",
        "allowedDecisions": ["assess indicator confidence", "flag weak evidence"],
        "requiresHumanApprovalFor": ["declaring breach scope", "notifying customers"],
    },
    "agent-code-review": {
        "id": "agent-code-review",
        "name": "Code Review Agent",
        "shortName": "Code Review",
        "kind": "ai_agent",
        "role": "Deployment and config review",
        "responsibility": "Inspects the Friday diff and secret-scan output for the exposure mechanism.",
        "capability": "code_review",
        "status": "idle",
        "allowedDecisions": ["identify risky diff", "propose fix"],
        "requiresHumanApprovalFor": ["merging production code", "rotating live secrets"],
    },
    "agent-risk-compliance": {
        "id": "agent-risk-compliance",
        "name": "Risk & Compliance Agent",
        "shortName": "Risk",
        "kind": "ai_agent",
        "role": "Policy review, challenge, and escalation",
        "responsibility": "Applies the incident policy, challenges overclaims, and decides what needs human approval.",
        "capability": "risk_compliance",
        "status": "idle",
        "allowedDecisions": ["challenge unsupported claims", "classify policy requirement", "recommend escalation"],
        "requiresHumanApprovalFor": ["external notification", "closing incident as resolved"],
    },
    "agent-remediation": {
        "id": "agent-remediation",
        "name": "Remediation Agent",
        "shortName": "Remediation",
        "kind": "ai_agent",
        "role": "Containment and fix planning",
        "responsibility": "Generates containment steps, fix checklist, and test criteria after approval.",
        "capability": "remediation",
        "status": "idle",
        "allowedDecisions": ["draft remediation plan", "create acceptance criteria"],
        "requiresHumanApprovalFor": ["executing production containment"],
    },
    "agent-human-approver": {
        "id": "agent-human-approver",
        "name": "Human Security Lead",
        "shortName": "Human",
        "kind": "human_actor",
        "role": "Security approval authority",
        "responsibility": "Reviews high-impact recommended actions and decides what can proceed.",
        "capability": "human_approval",
        "status": "idle",
        "allowedDecisions": ["approve containment", "reject containment", "defer customer notification"],
        "requiresHumanApprovalFor": [],
    },
}

SPECIALIST_AGENT_IDS = [
    "agent-forensics",
    "agent-threat-intel",
    "agent-code-review",
    "agent-risk-compliance",
    "agent-remediation",
]


@dataclass
class IncidentPacket:
    """Loaded inc-1042 context shared by every agent turn."""

    case: dict[str, Any]
    state: dict[str, Any]
    agents: dict[str, dict[str, Any]]
    evidence: list[dict[str, Any]]
    policy: dict[str, Any]


def _first_meaningful_line(path: Path, limit: int = 160) -> str:
    if not path.exists():
        return ""
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if line:
                return line[:limit]
    return ""


def _title_from_description(description: str) -> str:
    return description.rstrip(".").split(". ")[0][:80]


def _build_evidence(incident_dir: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for index, item in enumerate(manifest.get("evidence", []), start=1):
        kind = item["kind"]
        path = incident_dir / item["path"]
        evidence.append(
            {
                "id": item["id"],
                "kind": kind,
                "source": item["path"],
                "title": _title_from_description(item["description"]),
                "summary": item["description"],
                "location": item["path"],
                "excerpt": _first_meaningful_line(path),
                "confidence": _CONFIDENCE_BY_KIND.get(kind, 0.8),
                "sensitivity": "public_demo",
                "collectedAt": deterministic_timestamp(index),
                "collectedByAgentId": _COLLECTOR_BY_KIND.get(kind, "agent-forensics"),
                "limitations": ["Synthetic lab evidence; redacted values only."],
            }
        )
    return evidence


def load_incident(incident_dir: Path | str = DEFAULT_INCIDENT_DIR) -> IncidentPacket:
    """Load the inc-1042 packet (manifest + policy + per-evidence excerpts)."""
    incident_dir = Path(incident_dir)
    manifest = json.loads((incident_dir / "evidence_manifest.json").read_text())
    policy = json.loads((incident_dir / "incident_policy.json").read_text())
    evidence = _build_evidence(incident_dir, manifest)

    case = {
        "id": CASE_ID,
        "roomId": ROOM_ID,
        "title": manifest.get("title", "Possible API Key Exposure After Friday Deploy"),
        "summary": (
            "A suspicious API usage spike appeared shortly after a Friday deploy. "
            "Specialist agents must determine whether a token was exposed, whether "
            "customer data was accessed, what requires human approval, and what "
            "remediation should happen next."
        ),
        "severity": "high",
        "status": "investigating",
        "openedAt": deterministic_timestamp(1),
        "updatedAt": deterministic_timestamp(14),
        "businessUnit": "Payments Platform",
        "affectedSystem": "Customer Records API",
        "currentPhase": "Coordinated investigation",
        "phase": "hypothesis_review",
        "decisionGate": "human_required",
        "owner": "Human Security Lead",
        "tags": ["hackathon-demo", "api-key-exposure", "band-coordination"],
    }
    state = {
        "caseId": CASE_ID,
        "roomId": ROOM_ID,
        "status": "investigating",
        "severity": "high",
        "phase": "hypothesis_review",
        "decisionGate": "human_required",
        "updatedAt": deterministic_timestamp(14),
        "activeAgentIds": ["agent-commander", *SPECIALIST_AGENT_IDS],
        "openApprovalRequestIds": [],
        "unresolvedChallengeIds": [],
        "openTaskIds": [],
    }
    return IncidentPacket(
        case=case,
        state=state,
        agents=AGENT_PROFILES,
        evidence=evidence,
        policy=policy,
    )
