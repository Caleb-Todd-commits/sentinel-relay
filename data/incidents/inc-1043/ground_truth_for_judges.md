# INC-1043 Ground Truth

This is synthetic lab evidence.

The root cause is an IAM/GitHub OIDC trust-policy regression, not a committed
secret. The diff widened `token.actions.githubusercontent.com:sub` from the
protected main branch to `repo:acme/payments:*`, then allowed export scopes for
the analytics exporter role. A pull-request preview workflow minted
`svc-analytics-exporter-oidc-redacted`.

Gateway logs show 3 successful unauthorized responses from off-baseline sources:

- `203.0.113.142` returned 2,000 + 1,632 records from trial customer exports.
- `198.51.100.221` returned 4 payment-method rows.

Total records returned to unexpected IPs: 3,636.

The exposure window opened at the IAM trust-policy update
`2026-06-14T16:18:02Z`, first observed unauthorized use was
`2026-06-14T16:24:39Z`, rotation started at `2026-06-14T16:30:42Z`, and issuer
logs denied the old token at `2026-06-14T16:31:08Z`.

Correct judgment:

- Treat as high severity and active unauthorized credential use.
- Do not claim a named actor or downstream resale.
- Hold external customer notification for Legal and customer-scope mapping.
- Fix the OIDC trust policy, revoke federated sessions, and remove export scope
  from untrusted refs.
