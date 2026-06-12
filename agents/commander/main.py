"""Band Leader remote Band/Thenvoi worker."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.sentinel_agent_runtime import describe_agent, run_agent_entrypoint

AGENT_ID = "agent-commander"
AGENT_NAME = "Band Leader"
ENV_PREFIX = "BAND_LEADER"
SCHEMA_VERSION = "0.4.0"


def describe_contract() -> dict[str, str]:
    return describe_agent(AGENT_ID, AGENT_NAME, ENV_PREFIX)


if __name__ == "__main__":
    run_agent_entrypoint(
        sentinel_agent_id=AGENT_ID,
        agent_name=AGENT_NAME,
        env_prefix=ENV_PREFIX,
        prompt_file=str(Path(__file__).with_name("prompt.md")),
        legacy_env_prefixes=("COMMANDER",),
    )
