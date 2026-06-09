# 23 — Agent Input and Output Contracts

This file defines what every agent should receive, produce, and avoid.

## Global agent input

Every agent should receive:

- `case`: the active IncidentCase
- `roomId`: Band room ID
- `agentProfile`: its own AgentProfile
- `recentMessages`: relevant AgentMessages
- `evidence`: available EvidenceReferences
- `currentState`: IncidentStateSnapshot
- `task`: the specific assignment or request

## Global agent output

Every agent should output an `AgentMessage`.

No agent should output only freeform text.

## Commander Agent

### Inputs

- incident case
- current state snapshot
- messages from other agents
- approval request status

### Outputs

- `case_opened`
- `task_assignment`
- `approval_request`
- `state_update`
- `report_section`

### Not allowed

- approving production containment by itself
- declaring customer notification approved by itself
- closing unresolved incidents without human approval

## Forensics Agent

### Inputs

- API logs
- auth logs
- previous findings
- requested verifications

### Outputs

- `finding`
- `verification`
- `handoff`

### Required behavior

Every finding must include:

- evidence IDs,
- confidence score,
- limitations,
- requested verification if incomplete.

## Threat Intel Agent

### Inputs

- suspicious IPs,
- user/token behavior,
- timing patterns,
- Forensics findings.

### Outputs

- `verification`
- `risk_assessment`
- `challenge` if confidence is overstated.

### Required behavior

Threat Intel should separate weak and strong signals.

Weak:

- IP reputation alone.

Strong:

- unusual region,
- sensitive endpoint,
- timing after deploy,
- token match to suspicious artifact.

## Code Review Agent

### Inputs

- recent diff,
- config files,
- deployment notes,
- Forensics findings.

### Outputs

- `finding`
- `verification`
- remediation suggestions.

### Required behavior

The agent should identify root-cause hypotheses, not claim final breach scope.

## Risk & Compliance Agent

### Inputs

- policy file,
- findings,
- evidence,
- Threat Intel confidence,
- Code Review result.

### Outputs

- `challenge`
- `risk_assessment`
- approval requirements.

### Required behavior

This agent should challenge unsupported claims. It is the safety brake.

## Remediation Agent

### Inputs

- approved actions,
- code/config finding,
- risk constraints,
- acceptance criteria.

### Outputs

- `remediation_task`
- mock PR plan,
- testing plan,
- rollback plan.

### Required behavior

The Remediation Agent can draft fixes before approval, but should not mark high-impact production actions as approved until the `ApprovalDecision` exists.

## Human Security Lead

The human actor creates `approval_decision` messages.

This is what makes the workflow enterprise-grade.

## Agent prompt rule

Every agent prompt should include this instruction:

> Return a structured `AgentMessage` using the Sentinel Relay schema. Do not return only narrative text. Every material claim must reference evidence IDs or explicitly state that evidence is missing.
