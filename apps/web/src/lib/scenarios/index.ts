import type { AgentMessage, ApprovalDecision, ApprovalRequest, TaskStatus } from "@/lib/types";
import inc1042Messages from "./inc-1042-transcript.json";
import inc1043Messages from "./inc-1043-transcript.json";

export type ScenarioId = "INC-1042" | "INC-1043";

export type ScenarioMeta = {
  id: ScenarioId;
  caseId: string;
  title: string;
  summary: string;
  affectedSystem: string;
  rootCause: string;
  recordsAffected: string;
  credentialType: string;
  approvalRequest: ApprovalRequest;
  approvalDecision: ApprovalDecision;
  remediationTaskStatuses: Array<{ taskId: string; status: TaskStatus }>;
  messages: AgentMessage[];
};

const INC_1042: ScenarioMeta = {
  id: "INC-1042",
  caseId: "INC-1042",
  title: "Possible API Key Exposure After Friday Deploy",
  summary:
    "A suspicious API usage spike appeared shortly after a Friday deployment. Agents determine whether a fallback service token was exposed, what customer data was accessed, and what actions require human approval.",
  affectedSystem: "Customer Records API",
  rootCause: "Fallback token path introduced by deploy",
  recordsAffected: "10,227 customer records",
  credentialType: "Service API token (fallback path)",
  approvalRequest: {
    id: "appr-1042-1",
    caseId: "INC-1042",
    requestedByAgentId: "agent-commander",
    action: "Rotate fallback token; disable fallback token path; patch config",
    reason: "Forensics and Code Review confirm the fallback path was used from unexpected IPs. Containment requires credential rotation before patch.",
    severity: "high",
    evidenceIds: ["ev-api-gateway-logs", "ev-auth-events", "ev-code-diff", "ev-incident-policy"],
    riskIfApproved: "May briefly disrupt the service depending on the credential, but stops ongoing exposure.",
    riskIfRejected: "Exposed fallback token may remain usable while investigation continues.",
    requiredApprover: "Security Lead",
    status: "pending",
    createdAt: "2026-06-12T21:17:00Z",
  },
  approvalDecision: {
    id: "decision-appr-1042-1",
    requestId: "appr-1042-1",
    decision: "approved",
    decidedBy: "Human Security Lead",
    rationale: "Approved immediate containment: rotate the fallback token, disable the fallback path, and patch config. External customer notification remains held until record-access scope is verified with Legal.",
    decidedAt: "2026-06-12T21:17:30Z",
    approvedActionScope: ["Rotate fallback token", "Disable fallback token path", "Patch config"],
    explicitlyNotApproved: ["External customer notification", "Incident closure"],
  },
  remediationTaskStatuses: [
    { taskId: "rem-001", status: "done" },
    { taskId: "rem-002", status: "in_progress" },
    { taskId: "rem-003", status: "in_progress" },
    { taskId: "rem-004", status: "todo" },
    { taskId: "rem-005", status: "todo" },
    { taskId: "rem-006", status: "todo" },
  ],
  messages: inc1042Messages as AgentMessage[],
};

const INC_1043: ScenarioMeta = {
  id: "INC-1043",
  caseId: "INC-1043",
  title: "OIDC Trust Regression Exposed Analytics Exporter Token",
  summary:
    "An IAM trust-policy change widened GitHub OIDC access from the protected main branch to a repo-wide wildcard. A CI workflow minted a federated token that was used to export customer records.",
  affectedSystem: "Customer Records API",
  rootCause: "OIDC trust policy widened to unprotected refs",
  recordsAffected: "3,636 customer records",
  credentialType: "GitHub Actions OIDC token (federated)",
  approvalRequest: {
    id: "appr-1043-1",
    caseId: "INC-1043",
    requestedByAgentId: "agent-commander",
    action: "Revoke federated sessions; tighten OIDC trust policy; patch export scope",
    reason: "Forensics confirms federated sessions accessed customer exports from unexpected sources. Containment requires revoking active sessions before trust-policy patch.",
    severity: "high",
    evidenceIds: ["ev-api-gateway-logs", "ev-auth-events", "ev-code-diff", "ev-incident-policy"],
    riskIfApproved: "May briefly disrupt the service depending on the credential, but stops ongoing exposure.",
    riskIfRejected: "OIDC wildcard can continue minting production-scoped sessions while investigation continues.",
    requiredApprover: "Security Lead",
    status: "pending",
    createdAt: "2026-06-14T16:40:00Z",
  },
  approvalDecision: {
    id: "decision-appr-1043-1",
    requestId: "appr-1043-1",
    decision: "approved",
    decidedBy: "Human Security Lead",
    rationale: "Approved immediate containment: revoke federated sessions, tighten the OIDC trust policy, and patch export scope. External customer notification remains held until record-access scope is verified with Legal.",
    decidedAt: "2026-06-14T16:41:00Z",
    approvedActionScope: ["Revoke federated sessions", "Tighten OIDC trust policy", "Patch export scope"],
    explicitlyNotApproved: ["External customer notification", "Incident closure"],
  },
  remediationTaskStatuses: [
    { taskId: "rem-001", status: "done" },
    { taskId: "rem-002", status: "in_progress" },
    { taskId: "rem-003", status: "in_progress" },
    { taskId: "rem-004", status: "todo" },
    { taskId: "rem-005", status: "todo" },
    { taskId: "rem-006", status: "todo" },
  ],
  messages: inc1043Messages as AgentMessage[],
};

export const SCENARIOS: Record<ScenarioId, ScenarioMeta> = {
  "INC-1042": INC_1042,
  "INC-1043": INC_1043,
};

export function getScenario(id: string): ScenarioMeta | undefined {
  return SCENARIOS[id as ScenarioId];
}
