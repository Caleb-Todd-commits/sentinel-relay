# Sentinel Relay — Demo Scripts

The scripts in this folder are used to rehearse and validate the **prize-path demo**:
the evidence-driven, Band-coordinated incident workflow for case
`INC-1042 — Possible API Key Exposure After Friday Deploy`.

| Script | Purpose |
|---|---|
| `run-evidence-band-workflow.py` | Runs the full evidence-driven workflow through the live Band app routes and prints a JSON run summary. |
| `verify-evidence-pack.py` | Validates the synthetic incident evidence packet before a run. |

## What `run-evidence-band-workflow.py` does

This script is the "prize-path rehearsal". In order, it:

1. Loads a realistic incident evidence packet (default `data/incidents/inc-1042`).
2. Derives per-specialist findings from the packet (Forensics, Code Review, Threat Intel).
3. Uses the AI/ML API for the **Risk & Compliance policy gate** and the
   **Band Leader synthesis** (with deterministic fallbacks when the API is unavailable).
4. Posts the resulting collaboration trail through the app's `/api/collaboration` routes
   so it shows up in the War Room.

The script **never prints secret values** and expects the Next.js app to already be
running with Band Mode configured from the root `.env`.

## Prerequisites

1. **App running** with Band Mode:
   ```bash
   corepack pnpm dev
   ```
2. **Root `.env`** configured. Relevant variables:

   | Variable | Default | Notes |
   |---|---|---|
   | `AIMLAPI_API_KEY` | — | Required for live calls; falls back deterministically if unset (unless `--require-aimlapi`). |
   | `AIMLAPI_BASE_URL` | `https://api.aimlapi.com/v1` | |
   | `AIMLAPI_MODEL` | `gpt-4o-mini` | |
   | `SENTINEL_RELAY_APP_URL` | `http://127.0.0.1:3000` | Overridable with `--app-url`. |

3. **Evidence packet** present at `data/incidents/inc-1042` (or use another with
   `--incident-id` / `--evidence-dir`).

## Usage

```bash
# From the repo root, with the app already running:
python scripts/demo/run-evidence-band-workflow.py
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--app-url` | `$SENTINEL_RELAY_APP_URL` or `http://127.0.0.1:3000` | Base URL of the running app. |
| `--incident-id` | — | Synthetic incident id, e.g. `INC-1042` or `INC-1043`. |
| `--evidence-dir` | — | Path to a synthetic incident fixture directory. |
| `--timeout` | `45` | Per-request timeout (seconds). |
| `--skip-aimlapi` | off | Use deterministic fallbacks instead of calling the AI/ML API. |
| `--require-aimlapi` | off | Fail the run if the AI/ML API cannot be called live. |

### Examples

```bash
# Deterministic rehearsal (no external AI/ML calls) — most stable for a demo:
python scripts/demo/run-evidence-band-workflow.py --skip-aimlapi

# Strict live run — fail loudly if the AI/ML API is misconfigured:
python scripts/demo/run-evidence-band-workflow.py --require-aimlapi

# Run a different synthetic incident:
python scripts/demo/run-evidence-band-workflow.py --incident-id INC-1043
```

## Output

On success, the script prints a JSON summary to stdout, including:

- `caseId`, `roomId`, `evidenceDir`
- `messagesPosted`, `registeredAgents`
- `approvalRequests`, `approvalDecisions`, `taskStatuses`, `auditEvents`
- `recordsReturnedBySuspiciousReads`
- `aimlapi` (model, base URL, and provider status for the policy-gate / Band-leader synthesis)
- `latestMessageIds`

Exit codes:

- `0` — success (a warning is printed to stderr if the Band routes recorded `remoteWarnings`).
- `1` — failure (the error is printed to stderr, prefixed with `FAIL`).

## Troubleshooting

- **`Cannot reach Sentinel Relay app ...`** — the app isn't running. Start it with `corepack pnpm dev`.
- **`Band app routes are not configured`** — Band Mode variables are missing from the root `.env`.
- **`AIMLAPI_API_KEY is required ...`** — you passed `--require-aimlapi` without an API key.
  Set the key or drop the flag to use fallbacks.
