# Sentinel Relay — presentation and voiceover script

Target runtime: 2:35–2:55. Read naturally; the timings include short visual pauses.

## Recording order

| Time | Visual | Action |
|---|---|---|
| 0:00–0:20 | `cover.png` | Hold on title |
| 0:20–0:50 | `screenshots/workspace.png` | Show the full workspace and seeded scenario |
| 0:50–1:25 | Live application | Start `INC-1042`; let agent findings advance |
| 1:25–1:55 | `screenshots/approval.png` | Pause on requested scope before approving |
| 1:55–2:20 | `screenshots/result.png` | Show Summary, then briefly select Evidence and Audit |
| 2:20–2:45 | `screenshots/custom-question.png` | Show the open-ended question and specialist responses |
| 2:45–2:55 | `cover.png` | Closing line |

## Read-aloud script

### 0:00–0:20 — Problem

“Security incidents are not single-prompt problems. Investigation, engineering review, threat assessment, compliance judgment, approval, remediation, and reporting belong to different specialists—and every handoff can lose evidence or accountability.”

### 0:20–0:50 — Product

“Sentinel Relay is a Band-powered multi-agent incident workspace. One screen keeps the incident, the active agent, and the current decision visible. Six specialized agents investigate, challenge one another, and stop before high-impact action until a human Security Lead approves a precise scope.”

### 0:50–1:25 — Investigation

“I’ll start incident INC-1042, a possible API-key exposure after a Friday deployment. The Band Leader coordinates Forensics, Code Review, Threat Intel, and Risk and Compliance. Their messages remain role-specific: logs establish the access window, code review finds the unsafe fallback path, and threat analysis calibrates confidence without inventing attribution.”

“The key behavior is disagreement. Risk accepts the evidence for urgent containment but rejects the stronger claim of confirmed downstream exfiltration. Customer notification stays held until scope and Legal review are complete.”

### 1:25–1:55 — Human approval

“The workflow now stops. Remediation cannot continue until a human reviews the exact request: rotate the fallback token, disable the fallback path, and patch configuration. Notification and incident closure are explicitly outside this approval.”

“I’ll approve only that containment scope.”

### 1:55–2:20 — Result

“After approval, Remediation and the Band Leader complete the accountable response. Summary states the conclusion and root cause. Evidence lists the supporting artifacts. Audit preserves the ordered agent trail. The execution badge also tells us whether this was live Band execution or verified replay—degradation is never hidden.”

### 2:20–2:45 — Open-ended analysis

“Sentinel Relay is not limited to the two bundled incidents. Here I can enter a fictional, sanitized security problem. The Band Leader frames it, specialist agents add only relevant perspectives, and later agents react to the shared findings. This generalization path uses server-side AI/ML API orchestration and never asks the visitor for a provider key.”

### 2:45–2:55 — Close

“Sentinel Relay turns specialist AI outputs into an accountable incident decision: evidence first, disagreement visible, and high-impact action human-controlled.”

## Recording notes

- Use the stable URL: https://sentinel-relay-alpha.vercel.app
- Record signed out.
- Never type real incident data into the open-ended field.
- Pause for one beat before pressing **Approve containment →**.
- If the execution badge says `Verified replay`, describe it exactly that way.
- The four screenshots can be regenerated with:

```bash
node scripts/submission/capture-demo.mjs https://sentinel-relay-alpha.vercel.app submission/screenshots
```
