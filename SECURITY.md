# Security Policy

## Scope

Sentinel Relay is a hackathon prototype using fake/sample cybersecurity incident data. It should not process real secrets, real production logs, real customer data, or real incident evidence.

## Do Not Commit

Never commit:

- API keys
- Band credentials
- OpenAI keys
- AI/ML API keys
- Featherless keys
- `.env`
- `agent_config.yaml`
- real production logs
- real customer data
- screenshots containing secrets

## Safe Demo Data

Use only fake/demo values such as:

```txt
tok_demo_redacted
sk_demo_redacted
user_demo_123
198.51.100.42
203.0.113.10
```

## Environment Variables

Add new required environment variables to:

```txt
.env.example
README.md
relevant docs
```

## Reporting a Security Issue

Because this is a hackathon prototype, report issues directly to the team lead in the group chat and create a GitHub issue labeled:

```txt
risk:security-sensitive
```

Do not post real secrets in the issue.
