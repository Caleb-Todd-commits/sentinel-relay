import type { DemoIncident } from "@/lib/types";

export const sentinelRelayDemo: DemoIncident = {
  "schemaVersion": "0.4.0",
  "case": {
    "id": "INC-1042",
    "roomId": "band-room-inc-1042",
    "title": "Possible API Key Exposure After Friday Deploy",
    "summary": "A suspicious API usage spike appeared shortly after a Friday deployment. The demo incident asks multiple specialized agents to determine whether a token was exposed, whether customer data was accessed, what actions require approval, and what remediation should happen next.",
    "severity": "high",
    "status": "investigating",
    "openedAt": "2026-06-12T21:08:00Z",
    "updatedAt": "2026-06-12T21:18:00Z",
    "businessUnit": "Payments Platform",
    "affectedSystem": "Customer Records API",
    "currentPhase": "Coordinated investigation",
    "phase": "hypothesis_review",
    "decisionGate": "human_required",
    "owner": "Human Security Lead",
    "tags": [
      "hackathon-demo",
      "api-key-exposure",
      "high-stakes-workflow",
      "band-coordination"
    ]
  },
  "state": {
    "caseId": "INC-1042",
    "roomId": "band-room-inc-1042",
    "status": "investigating",
    "severity": "high",
    "phase": "hypothesis_review",
    "decisionGate": "human_required",
    "updatedAt": "2026-06-12T21:18:00Z",
    "activeAgentIds": [
      "agent-commander",
      "agent-forensics",
      "agent-threat-intel",
      "agent-code-review",
      "agent-risk-compliance",
      "agent-remediation"
    ],
    "openApprovalRequestIds": [],
    "unresolvedChallengeIds": [
      "msg-006"
    ],
    "openTaskIds": [
      "rem-002",
      "rem-003",
      "rem-004"
    ]
  },
  "agents": [
    {
      "id": "agent-commander",
      "name": "Incident Commander Agent",
      "shortName": "Commander",
      "kind": "ai_agent",
      "role": "Case coordination and task routing",
      "responsibility": "Opens the incident room, assigns agents, maintains state, requests approvals, and decides when the case can move to report generation.",
      "capability": "case_command",
      "status": "working",
      "currentTask": "Coordinate findings and maintain the incident state.",
      "allowedDecisions": [
        "assign tasks",
        "request verification",
        "summarize state",
        "request human approval",
        "generate report when ready"
      ],
      "requiresHumanApprovalFor": [
        "production containment",
        "external customer notification",
        "closing incident"
      ],
      "createdAt": "2026-06-12T21:08:00Z"
    },
    {
      "id": "agent-forensics",
      "name": "Forensics Agent",
      "shortName": "Forensics",
      "kind": "ai_agent",
      "role": "Log analysis and evidence timeline",
      "responsibility": "Reviews auth and API gateway logs, extracts suspicious activity, and submits evidence-backed timeline events.",
      "capability": "log_forensics",
      "status": "complete",
      "currentTask": "Log review completed; awaiting verification from other agents.",
      "allowedDecisions": [
        "submit evidence-backed findings",
        "build timeline events",
        "request indicator verification"
      ],
      "requiresHumanApprovalFor": [
        "declaring customer impact",
        "revoking production credentials"
      ],
      "createdAt": "2026-06-12T21:08:00Z"
    },
    {
      "id": "agent-threat-intel",
      "name": "Threat Intel Agent",
      "shortName": "Threat Intel",
      "kind": "ai_agent",
      "role": "Indicator and behavior assessment",
      "responsibility": "Evaluates suspicious tokens, IP behavior, geo-anomalies, and confidence signals without overstating weak indicators.",
      "capability": "threat_assessment",
      "status": "complete",
      "currentTask": "Confidence assessment submitted.",
      "allowedDecisions": [
        "assess indicator confidence",
        "lower or raise confidence",
        "flag weak evidence"
      ],
      "requiresHumanApprovalFor": [
        "declaring breach scope",
        "notifying customers"
      ],
      "createdAt": "2026-06-12T21:08:00Z"
    },
    {
      "id": "agent-code-review",
      "name": "Code Review Agent",
      "shortName": "Code Review",
      "kind": "ai_agent",
      "role": "Deployment and config review",
      "responsibility": "Inspects recent diffs and configuration changes to determine whether the suspicious token could have been exposed by code.",
      "capability": "code_review",
      "status": "complete",
      "currentTask": "Recent diff inspected; remediation path identified.",
      "allowedDecisions": [
        "identify risky diff",
        "propose fix",
        "create remediation checklist"
      ],
      "requiresHumanApprovalFor": [
        "merging production code",
        "rotating live secrets"
      ],
      "createdAt": "2026-06-12T21:08:00Z"
    },
    {
      "id": "agent-risk-compliance",
      "name": "Risk & Compliance Agent",
      "shortName": "Risk",
      "kind": "ai_agent",
      "role": "Policy review, challenge, and escalation",
      "responsibility": "Checks the incident policy, challenges unsupported conclusions, and determines what requires human approval.",
      "capability": "risk_compliance",
      "status": "challenging",
      "currentTask": "Challenge active: prove customer data scope before external notification.",
      "allowedDecisions": [
        "challenge unsupported claims",
        "classify policy requirement",
        "recommend escalation"
      ],
      "requiresHumanApprovalFor": [
        "external notification",
        "legal/comms disclosure",
        "closing incident as resolved"
      ],
      "createdAt": "2026-06-12T21:08:00Z"
    },
    {
      "id": "agent-remediation",
      "name": "Remediation Agent",
      "shortName": "Remediation",
      "kind": "ai_agent",
      "role": "Containment and fix planning",
      "responsibility": "Generates containment steps, fix checklist, test criteria, and a mock PR summary after approval is granted.",
      "capability": "remediation",
      "status": "waiting",
      "currentTask": "Waiting for human approval before marking containment tasks approved.",
      "allowedDecisions": [
        "draft remediation plan",
        "create acceptance criteria",
        "prepare mock PR summary"
      ],
      "requiresHumanApprovalFor": [
        "executing production containment",
        "invalidating live credentials without approval"
      ],
      "createdAt": "2026-06-12T21:08:00Z"
    },
    {
      "id": "human-security-lead",
      "name": "Human Security Lead",
      "shortName": "Human",
      "kind": "human_actor",
      "role": "Security approval authority",
      "responsibility": "Reviews high-impact recommended actions and decides what can proceed.",
      "capability": "human_approval",
      "status": "complete",
      "currentTask": "Containment decision recorded.",
      "allowedDecisions": [
        "approve containment",
        "reject containment",
        "defer customer notification",
        "request more evidence"
      ],
      "requiresHumanApprovalFor": [],
      "createdAt": "2026-06-12T21:08:00Z"
    }
  ],
  "messages": [
    {
      "id": "msg-001",
      "schemaVersion": "0.4.0",
      "caseId": "INC-1042",
      "roomId": "band-room-inc-1042",
      "sequence": 1,
      "agentId": "agent-commander",
      "agentName": "Incident Commander Agent",
      "type": "case_opened",
      "title": "Band incident room opened",
      "summary": "Opened a shared Band room for INC-1042 and registered the forensics, threat intel, code review, risk/compliance, and remediation agents.",
      "confidence": 1,
      "severity": "high",
      "evidenceIds": [],
      "targetAgentIds": [
        "agent-forensics",
        "agent-code-review",
        "agent-risk-compliance"
      ],
      "createdAt": "2026-06-12T21:08:00Z",
      "visibility": "judge_demo",
      "decisionImpact": "Creates the shared coordination space for all agent handoffs.",
      "nextAction": "Assign evidence review tasks to specialist agents.",
      "correlationId": "trace-inc-1042-001",
      "payload": {
        "kind": "generic",
        "data": {
          "roomCreated": true,
          "registeredAgentIds": [
            "agent-forensics",
            "agent-threat-intel",
            "agent-code-review",
            "agent-risk-compliance",
            "agent-remediation"
          ]
        }
      }
    },
    {
      "id": "msg-002",
      "schemaVersion": "0.4.0",
      "caseId": "INC-1042",
      "roomId": "band-room-inc-1042",
      "sequence": 2,
      "agentId": "agent-commander",
      "agentName": "Incident Commander Agent",
      "type": "task_assignment",
      "title": "Specialist review tasks assigned",
      "summary": "Forensics will parse logs, Code Review will inspect the Friday diff, Threat Intel will assess indicators, and Risk will evaluate policy implications.",
      "confidence": 1,
      "severity": "high",
      "evidenceIds": [],
      "targetAgentIds": [
        "agent-forensics",
        "agent-threat-intel",
        "agent-code-review",
        "agent-risk-compliance"
      ],
      "createdAt": "2026-06-12T21:08:18Z",
      "visibility": "judge_demo",
      "decisionImpact": "Prevents one agent from making the full decision alone.",
      "nextAction": "Wait for evidence-backed findings.",
      "correlationId": "trace-inc-1042-002",
      "payload": {
        "kind": "task_assignment",
        "data": {
          "taskId": "task-triage-001",
          "assignedToAgentId": "agent-forensics",
          "objective": "Parse logs and produce timeline findings.",
          "expectedOutput": "Evidence-backed finding and timeline events.",
          "acceptanceCriteria": [
            "Cite log source",
            "Assign confidence",
            "Request verification if needed"
          ]
        }
      }
    },
    {
      "id": "msg-003",
      "schemaVersion": "0.4.0",
      "caseId": "INC-1042",
      "roomId": "band-room-inc-1042",
      "sequence": 3,
      "agentId": "agent-forensics",
      "agentName": "Forensics Agent",
      "type": "finding",
      "title": "Suspicious API token usage identified",
      "summary": "API gateway logs show token tok_live_7f used from a new region to access a customer export endpoint shortly after deployment.",
      "confidence": 0.84,
      "severity": "high",
      "evidenceIds": [
        "ev-api-spike",
        "ev-auth-anomaly"
      ],
      "targetAgentIds": [
        "agent-threat-intel",
        "agent-code-review"
      ],
      "createdAt": "2026-06-12T21:09:11Z",
      "visibility": "judge_demo",
      "decisionImpact": "Raises likelihood of credential misuse but does not yet prove source of exposure.",
      "nextAction": "Ask Code Review to verify whether token material appeared in the deployment diff.",
      "correlationId": "trace-inc-1042-003",
      "payload": {
        "kind": "finding",
        "data": {
          "claim": "Suspicious token usage occurred shortly after deployment.",
          "supportingEvidenceIds": [
            "ev-api-spike",
            "ev-auth-anomaly"
          ],
          "contradictingEvidenceIds": [],
          "limitations": [
            "Does not prove how token was exposed.",
            "Does not prove customer data scope."
          ],
          "requestedVerifications": [
            "Check recent deployment diff for token exposure.",
            "Assess indicator reputation and behavior."
          ]
        }
      }
    },
    {
      "id": "msg-004",
      "schemaVersion": "0.4.0",
      "caseId": "INC-1042",
      "roomId": "band-room-inc-1042",
      "sequence": 4,
      "agentId": "agent-threat-intel",
      "agentName": "Threat Intel Agent",
      "type": "verification",
      "title": "Indicator confidence is elevated but not conclusive",
      "summary": "The source IP and access timing are suspicious, but IP reputation alone is insufficient. The stronger signal is behavior: unusual region, export endpoint, and timing after deploy.",
      "confidence": 0.76,
      "severity": "medium",
      "evidenceIds": [
        "ev-api-spike",
        "ev-auth-anomaly"
      ],
      "targetAgentIds": [
        "agent-risk-compliance"
      ],
      "createdAt": "2026-06-12T21:10:02Z",
      "visibility": "judge_demo",
      "decisionImpact": "Supports continued investigation while avoiding overclaiming breach confirmation.",
      "nextAction": "Risk agent should wait for code/config verification before recommending external communication.",
      "correlationId": "trace-inc-1042-004",
      "payload": {
        "kind": "generic",
        "data": {
          "confidenceBand": "medium",
          "strongestSignals": [
            "new region",
            "export endpoint",
            "post-deploy timing"
          ],
          "weakSignals": [
            "IP reputation alone"
          ]
        }
      }
    },
    {
      "id": "msg-005",
      "schemaVersion": "0.4.0",
      "caseId": "INC-1042",
      "roomId": "band-room-inc-1042",
      "sequence": 5,
      "agentId": "agent-code-review",
      "agentName": "Code Review Agent",
      "type": "finding",
      "title": "Recent diff likely exposed token material",
      "summary": "The Friday patch includes a fallback config value resembling the suspicious token. This supports a likely accidental secret exposure root cause.",
      "confidence": 0.91,
      "severity": "high",
      "evidenceIds": [
        "ev-code-diff"
      ],
      "targetAgentIds": [
        "agent-risk-compliance",
        "agent-remediation"
      ],
      "createdAt": "2026-06-12T21:11:33Z",
      "visibility": "judge_demo",
      "decisionImpact": "Increases confidence that the suspicious token may have been exposed through deployment artifacts.",
      "nextAction": "Prepare secret rotation and config hardening tasks, pending approval.",
      "correlationId": "trace-inc-1042-005",
      "payload": {
        "kind": "finding",
        "data": {
          "claim": "Recent config diff likely exposed token-like material.",
          "supportingEvidenceIds": [
            "ev-code-diff"
          ],
          "contradictingEvidenceIds": [],
          "limitations": [
            "The demo token is redacted.",
            "Diff exposure does not alone prove customer record access."
          ],
          "requestedVerifications": [
            "Risk agent should confirm approval requirements."
          ]
        }
      }
    },
    {
      "id": "msg-006",
      "schemaVersion": "0.4.0",
      "caseId": "INC-1042",
      "roomId": "band-room-inc-1042",
      "sequence": 6,
      "agentId": "agent-risk-compliance",
      "agentName": "Risk & Compliance Agent",
      "type": "challenge",
      "title": "Challenge: exposure is likely, customer impact not yet proven",
      "summary": "The evidence supports likely token exposure and unauthorized API use, but confirmed customer data exposure requires endpoint scope verification before external notification.",
      "confidence": 0.88,
      "severity": "high",
      "evidenceIds": [
        "ev-api-spike",
        "ev-code-diff",
        "ev-policy-approval"
      ],
      "targetAgentIds": [
        "agent-commander",
        "agent-forensics"
      ],
      "createdAt": "2026-06-12T21:12:07Z",
      "visibility": "judge_demo",
      "decisionImpact": "Prevents the system from overstating breach scope and triggers human approval before high-impact actions.",
      "nextAction": "Request approval for containment while holding customer notification pending scope confirmation.",
      "correlationId": "trace-inc-1042-006",
      "payload": {
        "kind": "challenge",
        "data": {
          "challengedMessageId": "msg-003",
          "reason": "Suspicious usage and token exposure are supported, but customer data exposure scope is not verified.",
          "requiredNextStep": "Confirm endpoint access scope before external notification.",
          "blocking": true,
          "suggestedOwnerAgentId": "agent-forensics"
        }
      }
    },
    {
      "id": "msg-007",
      "schemaVersion": "0.4.0",
      "caseId": "INC-1042",
      "roomId": "band-room-inc-1042",
      "sequence": 7,
      "agentId": "agent-commander",
      "agentName": "Incident Commander Agent",
      "type": "approval_request",
      "title": "Human approval requested for containment",
      "summary": "Requesting approval to revoke the suspicious token, rotate secrets, block the token path, and delay external notification until data scope is verified.",
      "confidence": 0.94,
      "severity": "high",
      "evidenceIds": [
        "ev-policy-approval",
        "ev-code-diff"
      ],
      "targetAgentIds": [
        "agent-remediation"
      ],
      "createdAt": "2026-06-12T21:13:22Z",
      "visibility": "judge_demo",
      "decisionImpact": "Ensures production-impacting actions are not taken autonomously.",
      "nextAction": "Wait for human security lead decision.",
      "correlationId": "trace-inc-1042-007",
      "payload": {
        "kind": "generic",
        "data": {
          "approvalRequestId": "approval-request-1",
          "requestedActions": [
            "revoke token",
            "rotate secrets",
            "patch config fallback"
          ],
          "notRequestedActions": [
            "external customer notification"
          ]
        }
      }
    },
    {
      "id": "msg-008",
      "schemaVersion": "0.4.0",
      "caseId": "INC-1042",
      "roomId": "band-room-inc-1042",
      "sequence": 8,
      "agentId": "human-security-lead",
      "agentName": "Human Security Lead",
      "type": "approval_decision",
      "title": "Containment approved, customer notice held",
      "summary": "Approved immediate containment: revoke token, rotate secrets, and patch config handling. Customer notification remains held until record access scope is verified.",
      "confidence": 1,
      "severity": "high",
      "evidenceIds": [
        "ev-human-approval"
      ],
      "targetAgentIds": [
        "agent-remediation",
        "agent-risk-compliance"
      ],
      "createdAt": "2026-06-12T21:14:01Z",
      "visibility": "judge_demo",
      "decisionImpact": "Unlocks remediation tasks while keeping communication decisions controlled.",
      "nextAction": "Remediation agent should create fix tasks and test criteria.",
      "correlationId": "trace-inc-1042-008",
      "payload": {
        "kind": "generic",
        "data": {
          "decision": "approved",
          "scope": [
            "token revocation",
            "secret rotation",
            "config patch"
          ],
          "held": [
            "external customer notification"
          ]
        }
      }
    },
    {
      "id": "msg-009",
      "schemaVersion": "0.4.0",
      "caseId": "INC-1042",
      "roomId": "band-room-inc-1042",
      "sequence": 9,
      "agentId": "agent-remediation",
      "agentName": "Remediation Agent",
      "type": "remediation_task",
      "title": "Containment and fix checklist prepared",
      "summary": "Generated a safe remediation plan: revoke exposed token, rotate affected secrets, remove fallback token material, add secret scanning, and add deploy guardrails.",
      "confidence": 0.93,
      "severity": "high",
      "evidenceIds": [
        "ev-code-diff",
        "ev-human-approval"
      ],
      "targetAgentIds": [
        "agent-code-review",
        "agent-commander"
      ],
      "createdAt": "2026-06-12T21:15:12Z",
      "visibility": "judge_demo",
      "decisionImpact": "Moves the case from investigation to controlled remediation.",
      "nextAction": "Generate final report once remediation summary is reviewed.",
      "correlationId": "trace-inc-1042-009",
      "payload": {
        "kind": "generic",
        "data": {
          "remediationTaskIds": [
            "rem-001",
            "rem-002",
            "rem-003",
            "rem-004"
          ]
        }
      }
    },
    {
      "id": "msg-010",
      "schemaVersion": "0.4.0",
      "caseId": "INC-1042",
      "roomId": "band-room-inc-1042",
      "sequence": 10,
      "agentId": "agent-commander",
      "agentName": "Incident Commander Agent",
      "type": "report_section",
      "title": "Audit-ready report generated",
      "summary": "Compiled the incident timeline, evidence references, challenge record, approval decision, remediation tasks, and remaining open questions into the final report.",
      "confidence": 0.97,
      "severity": "high",
      "evidenceIds": [
        "ev-api-spike",
        "ev-code-diff",
        "ev-policy-approval",
        "ev-human-approval"
      ],
      "targetAgentIds": [],
      "createdAt": "2026-06-12T21:17:48Z",
      "visibility": "judge_demo",
      "decisionImpact": "Creates the judge-facing proof of traceable multi-agent coordination.",
      "nextAction": "Use replay mode to demonstrate how the decision was reached through Band.",
      "correlationId": "trace-inc-1042-010",
      "payload": {
        "kind": "generic",
        "data": {
          "reportId": "report-inc-1042",
          "sectionTypes": [
            "executive_summary",
            "timeline",
            "evidence",
            "root_cause",
            "risk_assessment",
            "actions_taken",
            "audit_trail"
          ]
        }
      }
    }
  ],
  "evidence": [
    {
      "id": "ev-api-spike",
      "kind": "log",
      "source": "api_gateway_logs.json",
      "title": "API token used from unusual region",
      "summary": "A token associated with the payments service was used from an IP and region not previously associated with the account shortly after the deployment window.",
      "location": "records[3].source_ip",
      "excerpt": "token_id=tok_live_7f region=eu-west-1 endpoint=/v1/customers/export",
      "confidence": 0.84,
      "sensitivity": "public_demo",
      "collectedAt": "2026-06-12T21:09:11Z",
      "collectedByAgentId": "agent-forensics",
      "limitations": [
        "Demo data is synthetic and redacted."
      ]
    },
    {
      "id": "ev-auth-anomaly",
      "kind": "log",
      "source": "auth_logs.csv",
      "title": "Service token activity outside normal pattern",
      "summary": "Authentication logs show repeated token validation attempts from a new autonomous system after the Friday deploy.",
      "location": "row 4",
      "excerpt": "2026-06-12T21:06:11Z,tok_live_7f,success,185.199.109.133,new_region",
      "confidence": 0.78,
      "sensitivity": "public_demo",
      "collectedAt": "2026-06-12T21:09:11Z",
      "collectedByAgentId": "agent-forensics",
      "limitations": [
        "IP reputation is not sufficient alone to prove compromise."
      ]
    },
    {
      "id": "ev-code-diff",
      "kind": "code_diff",
      "source": "recent_diff.patch",
      "title": "Config diff appears to expose token material",
      "summary": "A deployment patch added a fallback environment value that resembles token material into an example config file.",
      "location": "diff hunk 2",
      "excerpt": "+ CUSTOMER_API_TOKEN=tok_live_7f_REDACTED_DEMO_VALUE",
      "confidence": 0.91,
      "sensitivity": "public_demo",
      "collectedAt": "2026-06-12T21:11:33Z",
      "collectedByAgentId": "agent-code-review",
      "limitations": [
        "The token value is redacted for demo safety."
      ]
    },
    {
      "id": "ev-policy-approval",
      "kind": "policy",
      "source": "incident_policy.md",
      "title": "Policy requires approval before external notice",
      "summary": "Customer notification and production containment actions require a human security lead approval when exposure scope is not fully confirmed.",
      "location": "Section 3.2",
      "excerpt": "External disclosure requires security lead approval and verified impact scope.",
      "confidence": 0.96,
      "sensitivity": "public_demo",
      "collectedAt": "2026-06-12T21:12:07Z",
      "collectedByAgentId": "agent-risk-compliance",
      "limitations": []
    },
    {
      "id": "ev-customer-ticket",
      "kind": "ticket",
      "source": "customer_ticket.txt",
      "title": "Customer reports unexpected account export notification",
      "summary": "A customer received an export notice they did not initiate, which increases concern but does not alone establish confirmed breach scope.",
      "location": "ticket body",
      "excerpt": "We got an export notification from the customer records portal that nobody on our team requested.",
      "confidence": 0.72,
      "sensitivity": "public_demo",
      "collectedAt": "2026-06-12T21:12:07Z",
      "collectedByAgentId": "agent-risk-compliance",
      "limitations": [
        "Single customer report requires correlation with endpoint access logs."
      ]
    },
    {
      "id": "ev-human-approval",
      "kind": "decision",
      "source": "Human approval gate",
      "title": "Containment approved, external notice held",
      "summary": "The human approver authorizes token revocation and rotation but holds external customer notification until accessed record scope is verified.",
      "location": "approval-request-1",
      "excerpt": "Approved: revoke token and rotate secrets. Hold: external notification pending scope confirmation.",
      "confidence": 1,
      "sensitivity": "public_demo",
      "collectedAt": "2026-06-12T21:14:01Z",
      "collectedByAgentId": "human-security-lead",
      "limitations": []
    }
  ],
  "timeline": [
    {
      "id": "tl-001",
      "timestamp": "2026-06-12T21:08:00Z",
      "title": "Incident opened",
      "summary": "Commander creates the Band incident room and recruits specialist agents.",
      "evidenceIds": [],
      "sourceMessageId": "msg-001",
      "actorAgentId": "agent-commander",
      "sortOrder": 1
    },
    {
      "id": "tl-002",
      "timestamp": "2026-06-12T21:09:11Z",
      "title": "Suspicious token usage detected",
      "summary": "Forensics identifies API token usage from a new region against a customer export endpoint.",
      "evidenceIds": [
        "ev-api-spike",
        "ev-auth-anomaly"
      ],
      "sourceMessageId": "msg-003",
      "actorAgentId": "agent-forensics",
      "sortOrder": 2
    },
    {
      "id": "tl-003",
      "timestamp": "2026-06-12T21:11:33Z",
      "title": "Code diff supports exposure hypothesis",
      "summary": "Code Review finds token-like material in the recent config patch.",
      "evidenceIds": [
        "ev-code-diff"
      ],
      "sourceMessageId": "msg-005",
      "actorAgentId": "agent-code-review",
      "sortOrder": 3
    },
    {
      "id": "tl-004",
      "timestamp": "2026-06-12T21:12:07Z",
      "title": "Risk challenge issued",
      "summary": "Risk & Compliance challenges breach classification until endpoint scope is confirmed.",
      "evidenceIds": [
        "ev-policy-approval"
      ],
      "sourceMessageId": "msg-006",
      "actorAgentId": "agent-risk-compliance",
      "sortOrder": 4
    },
    {
      "id": "tl-005",
      "timestamp": "2026-06-12T21:14:01Z",
      "title": "Human approval recorded",
      "summary": "Security lead approves containment while holding customer notification.",
      "evidenceIds": [
        "ev-human-approval"
      ],
      "sourceMessageId": "msg-008",
      "actorAgentId": "human-security-lead",
      "sortOrder": 5
    },
    {
      "id": "tl-006",
      "timestamp": "2026-06-12T21:15:12Z",
      "title": "Remediation plan prepared",
      "summary": "Remediation agent creates token rotation, config hardening, and deploy guardrail tasks.",
      "evidenceIds": [
        "ev-code-diff",
        "ev-human-approval"
      ],
      "sourceMessageId": "msg-009",
      "actorAgentId": "agent-remediation",
      "sortOrder": 6
    },
    {
      "id": "tl-007",
      "timestamp": "2026-06-12T21:17:48Z",
      "title": "Final report generated",
      "summary": "Commander compiles the traceable incident report with evidence, challenge, approval, and remediation context.",
      "evidenceIds": [
        "ev-api-spike",
        "ev-code-diff",
        "ev-policy-approval"
      ],
      "sourceMessageId": "msg-010",
      "actorAgentId": "agent-commander",
      "sortOrder": 7
    }
  ],
  "approvalRequest": {
    "id": "approval-request-1",
    "caseId": "INC-1042",
    "requestedByAgentId": "agent-commander",
    "action": "Revoke suspicious token, rotate affected secrets, block unsafe fallback config, and hold external notification pending scope verification.",
    "reason": "Evidence indicates likely token exposure and unauthorized use, but impact scope is still being verified. Containment is lower risk than waiting.",
    "severity": "high",
    "evidenceIds": [
      "ev-policy-approval",
      "ev-code-diff"
    ],
    "riskIfApproved": "May temporarily disrupt dependent services that use the token, but limits potential ongoing access.",
    "riskIfRejected": "Potentially exposed token may remain valid while investigation continues.",
    "requiredApprover": "Human security lead",
    "status": "approved",
    "createdAt": "2026-06-12T21:13:22Z",
    "expiresAt": "2026-06-12T21:43:22Z"
  },
  "approvalDecision": {
    "id": "approval-decision-1",
    "requestId": "approval-request-1",
    "decision": "approved",
    "decidedBy": "Human Security Lead",
    "rationale": "Approve immediate containment because the token exposure evidence is strong. Hold customer notification until record access scope is verified.",
    "decidedAt": "2026-06-12T21:14:01Z",
    "approvedActionScope": [
      "Revoke suspicious token",
      "Rotate affected secrets",
      "Patch unsafe fallback config"
    ],
    "explicitlyNotApproved": [
      "External customer notification",
      "Public disclosure",
      "Incident closure"
    ]
  },
  "remediationTasks": [
    {
      "id": "rem-001",
      "title": "Revoke suspicious token tok_live_7f",
      "ownerAgentId": "agent-remediation",
      "status": "done",
      "severity": "high",
      "rationale": "The token appears in suspicious API usage and likely appeared in the deployment artifact.",
      "evidenceIds": [
        "ev-api-spike",
        "ev-code-diff",
        "ev-human-approval"
      ],
      "acceptanceCriteria": [
        "Token revoked",
        "Dependent services moved to rotated token",
        "Audit event attached to case"
      ],
      "rollbackPlan": "Re-issue scoped service credential only after security lead approval.",
      "testPlan": [
        "Confirm old token fails authentication",
        "Confirm service health with rotated token"
      ]
    },
    {
      "id": "rem-002",
      "title": "Rotate affected customer API secrets",
      "ownerAgentId": "agent-remediation",
      "status": "in_progress",
      "severity": "high",
      "rationale": "Secret rotation reduces risk from any derived or adjacent exposure.",
      "evidenceIds": [
        "ev-code-diff",
        "ev-human-approval"
      ],
      "acceptanceCriteria": [
        "New secrets issued",
        "Old secrets invalidated",
        "Service health verified"
      ],
      "rollbackPlan": "Restore from secure secret manager version if rotation causes service outage.",
      "testPlan": [
        "Run smoke tests",
        "Check error rate after rotation"
      ]
    },
    {
      "id": "rem-003",
      "title": "Remove fallback token from config example",
      "ownerAgentId": "agent-code-review",
      "status": "review",
      "severity": "high",
      "rationale": "The config fallback is the likely accidental exposure mechanism.",
      "evidenceIds": [
        "ev-code-diff"
      ],
      "acceptanceCriteria": [
        "Patch removes token-like fallback",
        "Unit test blocks token-like examples",
        "Reviewer signs off"
      ],
      "rollbackPlan": "Revert only if replacement config blocks deployment; never restore token-like fallback.",
      "testPlan": [
        "Run config parser tests",
        "Run secret-pattern unit test"
      ]
    },
    {
      "id": "rem-004",
      "title": "Add deploy-time secret scanning guardrail",
      "ownerAgentId": "agent-code-review",
      "status": "todo",
      "severity": "medium",
      "rationale": "Prevent recurrence by blocking token-like values before deployment.",
      "evidenceIds": [
        "ev-code-diff"
      ],
      "acceptanceCriteria": [
        "Scanner runs in CI",
        "Build fails on token pattern",
        "Documentation updated"
      ],
      "rollbackPlan": "Allow manual security override only with audit log entry.",
      "testPlan": [
        "Commit fixture token and confirm CI blocks",
        "Commit safe placeholder and confirm CI passes"
      ]
    }
  ],
  "finalReport": {
    "caseId": "INC-1042",
    "title": "Audit Report: Possible API Key Exposure After Friday Deploy",
    "generatedAt": "2026-06-12T21:17:48Z",
    "generatedByAgentId": "agent-commander",
    "severity": "high",
    "executiveSummary": "Sentinel Relay coordinated a multi-agent investigation into suspicious API token activity after a Friday deploy. Agents found elevated evidence of token exposure, challenged unsupported breach claims, obtained human approval for containment, and generated a remediation plan while preserving an audit trail of each decision.",
    "rootCause": "The most likely root cause is accidental exposure of token-like material in a recent config diff. Additional endpoint access scope verification is still required before declaring confirmed customer data exposure.",
    "riskAssessment": "Severity remains high because the suspicious token reached a customer export endpoint. Confidence is high for token exposure and unauthorized use, but moderate for confirmed customer impact until accessed records are verified.",
    "customerImpact": "Potential customer impact exists because a customer export endpoint was accessed. Customer notification is held pending scope verification under the incident policy.",
    "approvedActions": [
      "Revoke suspicious token",
      "Rotate affected secrets",
      "Patch unsafe fallback config",
      "Hold external notification pending scope verification"
    ],
    "remediationTasks": [
      "rem-001",
      "rem-002",
      "rem-003",
      "rem-004"
    ],
    "openQuestions": [
      "Which exact customer records were accessed by the suspicious token?",
      "Was the token exposed outside the internal deployment artifact?",
      "Should legal/comms prepare a standby customer notice once scope is verified?"
    ],
    "sections": [
      {
        "id": "sec-exec",
        "type": "executive_summary",
        "title": "Executive Summary",
        "content": "Sentinel Relay coordinated a multi-agent investigation into suspicious API token activity after a Friday deploy.",
        "evidenceIds": [
          "ev-api-spike",
          "ev-code-diff",
          "ev-human-approval"
        ],
        "sourceMessageIds": [
          "msg-003",
          "msg-005",
          "msg-008",
          "msg-010"
        ]
      },
      {
        "id": "sec-timeline",
        "type": "timeline",
        "title": "Incident Timeline",
        "content": "The timeline shows room creation, forensic finding, code confirmation, risk challenge, human approval, remediation, and report generation.",
        "evidenceIds": [
          "ev-api-spike",
          "ev-code-diff",
          "ev-policy-approval"
        ],
        "sourceMessageIds": [
          "msg-001",
          "msg-002",
          "msg-003",
          "msg-004",
          "msg-005",
          "msg-006",
          "msg-007",
          "msg-008",
          "msg-009",
          "msg-010"
        ]
      },
      {
        "id": "sec-root-cause",
        "type": "root_cause",
        "title": "Likely Root Cause",
        "content": "The most likely root cause is accidental exposure of token-like material in a recent config diff.",
        "evidenceIds": [
          "ev-code-diff"
        ],
        "sourceMessageIds": [
          "msg-005"
        ]
      },
      {
        "id": "sec-risk",
        "type": "risk_assessment",
        "title": "Risk Assessment",
        "content": "Severity remains high because suspicious API access reached a customer export endpoint, but confirmed customer impact remains under verification.",
        "evidenceIds": [
          "ev-api-spike",
          "ev-policy-approval"
        ],
        "sourceMessageIds": [
          "msg-004",
          "msg-006"
        ]
      },
      {
        "id": "sec-actions",
        "type": "actions_taken",
        "title": "Approved Actions",
        "content": "Human approval authorized token revocation, secret rotation, and config patching while holding customer notification.",
        "evidenceIds": [
          "ev-human-approval"
        ],
        "sourceMessageIds": [
          "msg-007",
          "msg-008"
        ]
      }
    ],
    "auditTrailMessageIds": [
      "msg-001",
      "msg-002",
      "msg-003",
      "msg-004",
      "msg-005",
      "msg-006",
      "msg-007",
      "msg-008",
      "msg-009",
      "msg-010"
    ]
  }
};

export const DEMO_TOTAL_STEPS = sentinelRelayDemo.messages.length;
