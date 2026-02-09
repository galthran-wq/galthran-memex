from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8787


@dataclass
class GitHubConfig:
    owner: str = ""
    repo: str = ""
    default_branch: str = "main"


@dataclass
class KnowledgeConfig:
    root_dir: str = "knowledge"
    types: list[str] = field(
        default_factory=lambda: ["concept", "reference", "insight", "question", "note"]
    )
    recommended_tags: list[str] = field(
        default_factory=lambda: ["ml", "systems", "math", "programming"]
    )


@dataclass
class SemanticConfig:
    provider: str = "openai"
    model: str = "text-embedding-3-small"


@dataclass
class SearchConfig:
    backend: str = "bm25"
    semantic: SemanticConfig = field(default_factory=SemanticConfig)


@dataclass
class SyncConfig:
    auto_pull: bool = True
    pull_interval_seconds: int = 60


@dataclass
class Config:
    server: ServerConfig = field(default_factory=ServerConfig)
    github: GitHubConfig = field(default_factory=GitHubConfig)
    knowledge: KnowledgeConfig = field(default_factory=KnowledgeConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    sync: SyncConfig = field(default_factory=SyncConfig)

    cursor_api_key: str = ""
    openai_api_key: str = ""
    memex_auth_token: str = ""
    memex_git_url: str = ""
    memex_git_token: str = ""

    repo_root: Path = field(default_factory=lambda: Path.cwd())


def load_config(config_path: Path | None = None, repo_root: Path | None = None) -> Config:
    load_dotenv()

    root = repo_root or Path.cwd()
    path = config_path or root / "config.yaml"

    raw: dict = {}
    if path.exists():
        with open(path) as f:
            raw = yaml.safe_load(f) or {}

    server_raw = raw.get("server", {})
    github_raw = raw.get("github", {})
    knowledge_raw = raw.get("knowledge", {})
    search_raw = raw.get("search", {})
    semantic_raw = search_raw.get("semantic", {})
    sync_raw = raw.get("sync", {})

    return Config(
        server=ServerConfig(
            host=server_raw.get("host", "0.0.0.0"),
            port=server_raw.get("port", 8787),
        ),
        github=GitHubConfig(
            owner=github_raw.get("owner", ""),
            repo=github_raw.get("repo", ""),
            default_branch=github_raw.get("default_branch", "main"),
        ),
        knowledge=KnowledgeConfig(
            root_dir=knowledge_raw.get("root_dir", "knowledge"),
            types=knowledge_raw.get(
                "types", ["concept", "reference", "insight", "question", "note"]
            ),
            recommended_tags=knowledge_raw.get(
                "recommended_tags", ["ml", "systems", "math", "programming"]
            ),
        ),
        search=SearchConfig(
            backend=search_raw.get("backend", "bm25"),
            semantic=SemanticConfig(
                provider=semantic_raw.get("provider", "openai"),
                model=semantic_raw.get("model", "text-embedding-3-small"),
            ),
        ),
        sync=SyncConfig(
            auto_pull=sync_raw.get("auto_pull", True),
            pull_interval_seconds=sync_raw.get("pull_interval_seconds", 60),
        ),
        cursor_api_key=os.getenv("CURSOR_API_KEY", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        memex_auth_token=os.getenv("MEMEX_AUTH_TOKEN", ""),
        memex_git_url=os.getenv("MEMEX_GIT_URL", ""),
        memex_git_token=os.getenv("MEMEX_GIT_TOKEN", ""),
        repo_root=root,
    )
