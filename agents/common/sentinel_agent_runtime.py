"""Shared runtime helper for Sentinel Relay remote agents.

The imports for Band/Thenvoi and LangGraph are intentionally inside the runtime
function so the repo can still be inspected and compiled before dependencies or
credentials are installed.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import NoReturn


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return

    current = Path(__file__).resolve()
    for parent in [current.parent, *current.parents]:
        env_file = parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)


def _missing_dependency(package: str, install_hint: str) -> NoReturn:
    raise SystemExit(
        f"Missing dependency: {package}.\n"
        f"Install agent dependencies first:\n\n"
        f"  cd agents\n"
        f"  uv sync\n\n"
        f"or:\n\n"
        f"  pip install {install_hint}\n"
    )


def describe_agent(agent_id: str, agent_name: str, env_prefix: str) -> dict[str, str]:
    return {
        "sentinel_agent_id": agent_id,
        "agent_name": agent_name,
        "env_prefix": env_prefix,
        "schema_version": "0.4.0",
        "expected_output": "AgentMessage",
        "schema_source": "packages/schemas",
    }


async def run_thenvoi_langgraph_agent(*, sentinel_agent_id: str, agent_name: str, env_prefix: str, prompt_path: Path) -> None:
    """Run a remote Band/Thenvoi agent with the LangGraph SDK adapter.

    Set `SENTINEL_RELAY_AGENT_OFFLINE_MODE=true` to print the contract without
    attempting a network connection.
    """

    _load_dotenv_if_available()

    if os.getenv("SENTINEL_RELAY_AGENT_OFFLINE_MODE") == "true":
        print(f"{agent_name} offline contract: {describe_agent(sentinel_agent_id, agent_name, env_prefix)}")
        print(f"Prompt file: {prompt_path}")
        return

    agent_id = os.getenv(f"{env_prefix}_AGENT_ID") or os.getenv("BAND_AGENT_ID")
    api_key = os.getenv(f"{env_prefix}_AGENT_API_KEY") or os.getenv("BAND_AGENT_API_KEY")

    if not agent_id or not api_key:
        raise SystemExit(
            f"{agent_name} is missing credentials. Set {env_prefix}_AGENT_ID and {env_prefix}_AGENT_API_KEY."
        )

    try:
        from langchain_openai import ChatOpenAI  # type: ignore
    except Exception:
        _missing_dependency("langchain-openai", "langchain-openai")

    try:
        from langgraph.checkpoint.memory import InMemorySaver  # type: ignore
    except Exception:
        _missing_dependency("langgraph", "langgraph")

    try:
        from thenvoi import Agent  # type: ignore
        from thenvoi.adapters import LangGraphAdapter  # type: ignore
    except Exception:
        _missing_dependency("thenvoi-sdk", '"thenvoi-sdk[langgraph]"')

    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    prompt = prompt_path.read_text() if prompt_path.exists() else f"You are {agent_name} for Sentinel Relay."

    # The current quickstart path uses LangGraphAdapter(llm, checkpointer). The
    # long role prompt is kept in the repo and should be merged into the graph
    # prompt if/when the team customizes the adapter beyond the baseline.
    del prompt
    adapter = LangGraphAdapter(llm=ChatOpenAI(model=model), checkpointer=InMemorySaver())
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)

    print(f"Starting {agent_name} as remote Band agent {agent_id}.")
    await agent.run()


def run_agent_entrypoint(*, sentinel_agent_id: str, agent_name: str, env_prefix: str, prompt_file: str) -> None:
    prompt_path = Path(prompt_file).resolve()
    asyncio.run(
        run_thenvoi_langgraph_agent(
            sentinel_agent_id=sentinel_agent_id,
            agent_name=agent_name,
            env_prefix=env_prefix,
            prompt_path=prompt_path,
        )
    )
