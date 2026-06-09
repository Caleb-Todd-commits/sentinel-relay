# Mock Flow Demo Script

Use this script when showing the Step 5 baseline to teammates or judges.

## 20-second explanation

“Sentinel Relay is a multi-agent cybersecurity incident command center. This mock flow shows the exact workflow we will later run through Band: agents coordinate in a shared incident room, pass structured evidence, challenge weak conclusions, request human approval, and generate an audit-ready report.”

## Demo path

1. Open `/demo`.
2. Explain the sample case: possible API key exposure after a Friday deploy.
3. Click **Launch War Room**.
4. Click **Start incident**.
5. Walk through each step with **Run next step**.
6. Pause at the Risk challenge.
7. Explain that this is the important moment: the agents do not blindly agree.
8. Pause at the approval gate.
9. Explain that remediation is blocked until a human approves containment.
10. Click **Approve containment**.
11. Continue until the final report unlocks.
12. Open `/report`.
13. Explain that the report is audit-ready because it cites the same evidence and messages shown in the War Room.

## What to emphasize

- The UI is not just chat.
- Every major claim has evidence.
- Band is represented as the shared coordination stream.
- The system shows disagreement.
- The human approval gate is scoped.
- Remediation follows approval.
- The report is traceable.

## Backup line if live Band fails later

“This mock replay is intentionally preserved as the fallback demo path. The same interface is designed to be fed by real Band messages, but the product remains judge-demoable even if an external service has issues during the live presentation.”
