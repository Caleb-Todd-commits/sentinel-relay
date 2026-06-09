# Step 6 Demo Walkthrough

## Goal

Use this walkthrough when recording the project demo or presenting live.

The War Room should be the central screen. The viewer should not need to inspect the code to understand why Band matters.

## Opening line

> Sentinel Relay is a Band-powered incident command center where specialized agents investigate a possible API key exposure, challenge weak conclusions, request human approval, and generate an audit-ready response record.

## Click path

### 1. Open `/war-room`

Point out:

- command bar,
- case ID,
- approval state,
- severity,
- message count,
- judge briefing panel.

Say:

> The UI is intentionally built around the coordination layer. This is not a chatbot answer; it is a shared incident room.

### 2. Click **Start incident**

Point out:

- Band incident room opened,
- agents registered,
- first message appears,
- audit replay trail begins.

Say:

> The first action is room creation and participant registration. Band is present at the start of the workflow.

### 3. Click through specialist assignment and early evidence

Point out:

- agent roster status changes,
- message stream target agents,
- evidence board unlocks items,
- collaboration map reveals handoffs.

Say:

> Each agent contributes a specific kind of context instead of one model trying to make the whole decision.

### 4. Pause on **Risk challenges customer-impact claim**

This is the most important moment.

Point out:

- critical moment card,
- challenge message styling,
- unresolved challenge count,
- decision board state,
- evidence limitations.

Say:

> This is the core differentiator. The system does not reward agents for agreeing. Risk & Compliance blocks an unsupported customer-impact claim until the evidence is strong enough.

### 5. Click to approval gate

Point out:

- remediation blocked,
- approval request,
- risk if approved/rejected,
- required approver.

Say:

> High-impact actions do not execute automatically. The human approval is part of the shared coordination state.

### 6. Click **Approve containment**

Point out:

- approved scope,
- explicitly not approved customer notification,
- remediation unlocks.

Say:

> The decision is scoped. Containment is allowed, but customer notification remains deferred because customer data scope is not proven.

### 7. Complete demo

Point out:

- remediation tasks,
- final report preview,
- audit replay trail,
- report page CTA.

Say:

> The final output is not a hallucinated summary. It is generated from messages, evidence, approvals, and decisions that were created during the workflow.

## Do not say

Avoid saying:

- “This is just mocked for now.”
- “We did not finish Band yet.”
- “Imagine this was connected.”

Say instead:

- “This is deterministic replay mode for demo reliability.”
- “The UI is built against the same structured message contract that the Band provider will use.”
- “Mock mode protects the demo while Band mode is connected behind the provider layer.”
