from __future__ import annotations

import asyncio
import logging
import subprocess
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from server.config import Config, load_config
from server.kb import KnowledgeBase
from server.tools import register_tools

logger = logging.getLogger("memex")


def _clone_repo(config: Config) -> Path:
    work_dir = Path("/tmp/memex-repo")
    if work_dir.exists():
        logger.info("Repo already cloned at %s, pulling...", work_dir)
        subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=work_dir,
            capture_output=True,
            timeout=60,
        )
        return work_dir

    clone_url = config.memex_git_url
    if config.memex_git_token and "github.com" in clone_url:
        clone_url = clone_url.replace(
            "https://github.com",
            f"https://x-access-token:{config.memex_git_token}@github.com",
        )

    logger.info("Cloning %s...", config.memex_git_url)
    subprocess.run(
        ["git", "clone", "--depth=1", clone_url, str(work_dir)],
        capture_output=True,
        timeout=120,
        check=True,
    )
    return work_dir


def create_server(config: Config | None = None) -> FastMCP:
    if config is None:
        config = load_config()

    if config.memex_git_url:
        repo_root = _clone_repo(config)
        config.repo_root = repo_root

    kb = KnowledgeBase(config)

    mcp = FastMCP(
        "memex",
        host=config.server.host,
        port=config.server.port,
        stateless_http=True,
    )

    register_tools(mcp, kb, config)

    return mcp


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    config = load_config()
    mcp = create_server(config)
    logger.info(
        "Starting Memex MCP server on %s:%s",
        config.server.host,
        config.server.port,
    )
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    run()
