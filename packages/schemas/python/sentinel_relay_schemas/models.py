from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

Severity = Literal["informational", "low", "medium", "high", "critical"]
IncidentStatus = Literal[
    "draft",
    "open",
    "triaging",
    "investigating",
    "awaiting_approval",
    "approved_for_containment",
    "remediating",
    "report_ready",
    "closed",
]
IncidentPhase = Literal[
    "intake",
    "triage",
    "evidence_collection",
    "hypothesis_review",
    "risk_review",
    "human_approval",
    "containment",
    "remediation",
    "reporting",
    "closed",
]
DecisionGate = Literal["none", "human_required", "approved", "rejected", "deferred"]
AgentStatus = Literal["offline", "idle", "assigned", "working", "challenging", "waiting", "blocked", "complete"]
AgentKind = Literal["ai_agent", "human_actor", "system"]
AgentCapability = Literal[
    "case_command",
    "log_forensics",
    "threat_assessment",
    "code_review",
    "risk_compliance",
    "remediation",
    "human_approval",
    "report_generation",
]
EvidenceKind = Literal[
    "log",
    "code_diff",
    "policy",
    "ticket",
    "timeline",
    "decision",
    "configuration",
    "external_indicator",
    "report",
]
EvidenceSensitivity = Literal["public_demo", "internal", "confidential", "restricted"]
MessageType = Literal[
    "case_opened",
    "room_created",
    "agent_joined",
    "task_assignment",
    "finding",
    "challenge",
    "verification",
    "risk_assessment",
    "approval_request",
    "approval_decision",
    "remediation_task",
    "report_section",
    "state_update",
    "handoff",
    "watchdog_alert",
]
MessageVisibility = Literal["judge_demo", "internal", "security_lead_only"]
ApprovalStatus = Literal["pending", "approved", "rejected", "deferred", "expired"]
ApprovalDecisionValue = Literal["approved", "rejected", "deferred"]
TaskStatus = Literal["blocked", "todo", "in_progress", "review", "done", "deferred"]


class AgentProfile(BaseModel):
    id: str
    name: str
    shortName: str
    kind: AgentKind
    role: str
    responsibility: str
    capability: AgentCapability
    status: AgentStatus
    currentTask: str | None = None
    allowedDecisions: list[str]
    requiresHumanApprovalFor: list[str]
    createdAt: datetime | None = None


class EvidenceReference(BaseModel):
    id: str
    kind: EvidenceKind
    source: str
    title: str
    summary: str
    location: str | None = None
    excerpt: str | None = None
    confidence: float = Field(ge=0, le=1)
    sensitivity: EvidenceSensitivity
    collectedAt: datetime | None = None
    collectedByAgentId: str | None = None
    hash: str | None = None
    limitations: list[str] = Field(default_factory=list)


class IncidentCase(BaseModel):
    id: str
    roomId: str
    title: str
    summary: str
    severity: Severity
    status: IncidentStatus
    openedAt: datetime
    updatedAt: datetime
    businessUnit: str
    affectedSystem: str
    currentPhase: str
    phase: IncidentPhase
    decisionGate: DecisionGate
    owner: str | None = None
    tags: list[str]


class IncidentStateSnapshot(BaseModel):
    caseId: str
    roomId: str
    status: IncidentStatus
    severity: Severity
    phase: IncidentPhase
    decisionGate: DecisionGate
    updatedAt: datetime
    activeAgentIds: list[str]
    openApprovalRequestIds: list[str]
    unresolvedChallengeIds: list[str]
    openTaskIds: list[str]


class AgentMessage(BaseModel):
    id: str
    schemaVersion: str
    caseId: str
    roomId: str
    sequence: int = Field(ge=1)
    agentId: str
    agentName: str
    type: MessageType
    title: str
    summary: str
    confidence: float = Field(ge=0, le=1)
    severity: Severity
    evidenceIds: list[str]
    targetAgentIds: list[str] | None = None
    createdAt: datetime
    visibility: MessageVisibility
    decisionImpact: str | None = None
    nextAction: str | None = None
    correlationId: str | None = None
    payload: dict[str, Any] | None = None

    @field_validator("summary")
    @classmethod
    def summary_is_useful(cls, value: str) -> str:
        if len(value.strip()) < 20:
            raise ValueError("summary must be descriptive enough for audit replay")
        return value


class BandEnvelope(BaseModel):
    schemaVersion: str
    envelopeType: Literal["sentinel_relay.agent_message"]
    caseId: str
    roomId: str
    senderAgentId: str
    messageId: str
    sentAt: datetime
    traceId: str
    payload: AgentMessage


class TimelineEvent(BaseModel):
    id: str
    timestamp: datetime
    title: str
    summary: str
    evidenceIds: list[str]
    sourceMessageId: str | None = None
    actorAgentId: str | None = None
    sortOrder: int | None = None


class ApprovalRequest(BaseModel):
    id: str
    caseId: str
    requestedByAgentId: str
    action: str
    reason: str
    severity: Severity
    evidenceIds: list[str]
    riskIfApproved: str
    riskIfRejected: str
    requiredApprover: str
    status: ApprovalStatus
    createdAt: datetime | None = None
    expiresAt: datetime | None = None


class ApprovalDecision(BaseModel):
    id: str
    requestId: str
    decision: ApprovalDecisionValue
    decidedBy: str
    rationale: str
    decidedAt: datetime
    approvedActionScope: list[str]
    explicitlyNotApproved: list[str]


class RemediationTask(BaseModel):
    id: str
    title: str
    ownerAgentId: str
    status: TaskStatus
    severity: Severity
    rationale: str
    evidenceIds: list[str]
    acceptanceCriteria: list[str]
    rollbackPlan: str | None = None
    testPlan: list[str] | None = None


class ReportSection(BaseModel):
    id: str
    type: str
    title: str
    content: str
    evidenceIds: list[str]
    sourceMessageIds: list[str]


class FinalReport(BaseModel):
    caseId: str
    title: str
    generatedAt: datetime
    generatedByAgentId: str
    severity: Severity
    executiveSummary: str
    rootCause: str
    riskAssessment: str
    customerImpact: str
    approvedActions: list[str]
    remediationTasks: list[str]
    openQuestions: list[str]
    sections: list[ReportSection]
    auditTrailMessageIds: list[str]


class DemoIncident(BaseModel):
    schemaVersion: str
    case: IncidentCase
    state: IncidentStateSnapshot
    agents: list[AgentProfile]
    messages: list[AgentMessage]
    evidence: list[EvidenceReference]
    timeline: list[TimelineEvent]
    approvalRequest: ApprovalRequest
    approvalDecision: ApprovalDecision
    remediationTasks: list[RemediationTask]
    finalReport: FinalReport
