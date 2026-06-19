# Security policy

## Scope

Sentinel Relay is a public prototype for synthetic cybersecurity incident analysis. It is not an incident-response control plane and must not receive real secrets, production logs, customer records, personal data, or confidential incident evidence.

The open-ended **Try your own scenario** field sends the submitted description to the configured AI/ML API provider for analysis. Use fictional or fully sanitized text only.

## Data rules

Never commit or submit:

- API keys, session tokens, or Band credentials
- `.env` files or `agent_config.yaml`
- real production logs or screenshots containing secrets
- customer, employee, or attacker personal data
- unredacted vulnerability or incident details

Bundled evidence is synthetic. IP addresses use documentation ranges and token-like values are redacted labels.

## Runtime boundaries

- Provider credentials remain server-side.
- The public custom-analysis route applies a best-effort six-requests-per-minute application limit per forwarded IP.
- Visitors are never asked for bring-your-own keys.
- Seeded high-impact actions stop at explicit human approval.
- Remediation output is advisory and does not execute production changes.
- Verified replay keeps the workflow useful without claiming a degraded integration is live.

## Reporting a vulnerability

Report security issues privately to the repository owner. Do not open a public issue containing exploit details, credentials, or sensitive evidence. A sanitized tracking issue may be created after the sensitive details are removed.
