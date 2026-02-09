from __future__ import annotations

import re
import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import yaml
from rank_bm25 import BM25Okapi

from server.config import Config


@dataclass
class Edge:
    path: str
    label: str
    description: str = ""


@dataclass
class Source:
    url: str
    title: str = ""


@dataclass
class Entry:
    path: str
    slug: str
    title: str
    type: str
    summary: str
    tags: list[str]
    created: str
    updated: str
    edges: list[Edge]
    sources: list[Source]
    body: str
    raw: str


@dataclass
class Backlink:
    path: str
    title: str
    label: str
    description: str = ""


@dataclass
class SearchResult:
    path: str
    title: str
    type: str
    tags: list[str]
    summary: str
    score: float
    backlink_count: int


class SearchBackend(Protocol):
    def index(self, entries: list[Entry]) -> None: ...
    def search(self, query: str, limit: int = 20) -> list[SearchResult]: ...


class BM25Backend:
    def __init__(self) -> None:
        self._entries: list[Entry] = []
        self._bm25: BM25Okapi | None = None
        self._backlink_counts: dict[str, int] = {}

    def set_backlink_counts(self, counts: dict[str, int]) -> None:
        self._backlink_counts = counts

    def index(self, entries: list[Entry]) -> None:
        self._entries = entries
        corpus = []
        for e in entries:
            text = f"{e.title} {e.summary} {' '.join(e.tags)} {e.body}"
            corpus.append(text.lower().split())
        if corpus:
            self._bm25 = BM25Okapi(corpus)
        else:
            self._bm25 = None

    def search(self, query: str, limit: int = 20) -> list[SearchResult]:
        if not self._bm25 or not self._entries:
            return []
        tokens = query.lower().split()
        scores = self._bm25.get_scores(tokens)
        scored = sorted(
            zip(self._entries, scores), key=lambda x: x[1], reverse=True
        )
        results = []
        for entry, score in scored[:limit]:
            text = f"{entry.title} {entry.summary} {' '.join(entry.tags)} {entry.body}".lower()
            if not any(t in text for t in tokens):
                continue
            results.append(
                SearchResult(
                    path=entry.path,
                    title=entry.title,
                    type=entry.type,
                    tags=entry.tags,
                    summary=entry.summary,
                    score=round(score, 4),
                    backlink_count=self._backlink_counts.get(entry.path, 0),
                )
            )
        return results


class SubstringBackend:
    def __init__(self) -> None:
        self._entries: list[Entry] = []
        self._backlink_counts: dict[str, int] = {}

    def set_backlink_counts(self, counts: dict[str, int]) -> None:
        self._backlink_counts = counts

    def index(self, entries: list[Entry]) -> None:
        self._entries = entries

    def search(self, query: str, limit: int = 20) -> list[SearchResult]:
        terms = query.lower().split()
        results = []
        for entry in self._entries:
            text = f"{entry.title} {entry.summary} {' '.join(entry.tags)} {entry.body}".lower()
            score = sum(1 for t in terms if t in text)
            if score > 0:
                results.append(
                    SearchResult(
                        path=entry.path,
                        title=entry.title,
                        type=entry.type,
                        tags=entry.tags,
                        summary=entry.summary,
                        score=float(score),
                        backlink_count=self._backlink_counts.get(entry.path, 0),
                    )
                )
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_entry(path: Path, repo_root: Path) -> Entry | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception:
        return None

    m = _FRONTMATTER_RE.match(raw)
    if not m:
        return None

    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None

    if not isinstance(fm, dict) or "title" not in fm:
        return None

    rel_path = "/" + str(path.relative_to(repo_root))
    slug = path.stem

    edges_raw = fm.get("edges", []) or []
    edges = []
    for e in edges_raw:
        if isinstance(e, dict) and "path" in e and "label" in e:
            edges.append(Edge(
                path=e["path"],
                label=e["label"],
                description=e.get("description", ""),
            ))

    sources_raw = fm.get("sources", []) or []
    sources = []
    for s in sources_raw:
        if isinstance(s, dict) and "url" in s:
            sources.append(Source(url=s["url"], title=s.get("title", "")))

    body = raw[m.end():]

    return Entry(
        path=rel_path,
        slug=slug,
        title=fm.get("title", ""),
        type=fm.get("type", "note"),
        summary=fm.get("summary", ""),
        tags=fm.get("tags", []) or [],
        created=str(fm.get("created", "")),
        updated=str(fm.get("updated", "")),
        edges=edges,
        sources=sources,
        body=body,
        raw=raw,
    )


class KnowledgeBase:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._entries: dict[str, Entry] = {}
        self._backlinks: dict[str, list[Backlink]] = defaultdict(list)
        self._backlink_counts: dict[str, int] = {}
        self._search_backend: BM25Backend | SubstringBackend
        self._semantic_backend = None
        self._last_pull: float = 0

        if config.search.backend == "substring":
            self._search_backend = SubstringBackend()
        else:
            self._search_backend = BM25Backend()

        if config.search.backend == "semantic" and config.openai_api_key:
            try:
                from server.semantic import SemanticBackend
                cache_path = config.repo_root / ".memex" / "embeddings.json"
                self._semantic_backend = SemanticBackend(
                    api_key=config.openai_api_key,
                    model=config.search.semantic.model,
                    cache_path=cache_path,
                )
            except Exception:
                pass

        self.refresh()

    @property
    def knowledge_dir(self) -> Path:
        return self._config.repo_root / self._config.knowledge.root_dir

    def refresh(self) -> None:
        self._entries.clear()
        self._backlinks.clear()

        kb_dir = self.knowledge_dir
        if not kb_dir.exists():
            return

        for md_path in kb_dir.glob("*.md"):
            entry = parse_entry(md_path, self._config.repo_root)
            if entry:
                self._entries[entry.path] = entry

        self._build_backlinks()

        self._backlink_counts = {
            path: len(bls) for path, bls in self._backlinks.items()
        }
        all_entries = list(self._entries.values())
        self._search_backend.set_backlink_counts(self._backlink_counts)
        self._search_backend.index(all_entries)

        if self._semantic_backend:
            self._semantic_backend.set_backlink_counts(self._backlink_counts)
            try:
                self._semantic_backend.index(all_entries)
            except Exception:
                pass

    def _build_backlinks(self) -> None:
        self._backlinks.clear()
        for entry in self._entries.values():
            for edge in entry.edges:
                self._backlinks[edge.path].append(
                    Backlink(
                        path=entry.path,
                        title=entry.title,
                        label=edge.label,
                        description=edge.description,
                    )
                )

    def try_pull(self) -> None:
        if not self._config.sync.auto_pull:
            return
        now = time.time()
        if now - self._last_pull < self._config.sync.pull_interval_seconds:
            return
        self._last_pull = now
        try:
            result = subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=self._config.repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and "Already up to date" not in result.stdout:
                self.refresh()
        except Exception:
            pass

    def list_entries(
        self,
        type_filter: str | None = None,
        tag_filter: str | None = None,
    ) -> list[Entry]:
        self.try_pull()
        results = []
        for entry in self._entries.values():
            if type_filter and entry.type != type_filter:
                continue
            if tag_filter and tag_filter not in entry.tags:
                continue
            results.append(entry)
        results.sort(key=lambda e: e.created, reverse=True)
        return results

    def read_entry(self, path: str) -> Entry | None:
        self.try_pull()
        return self._entries.get(path)

    def get_backlinks(self, path: str) -> list[Backlink]:
        return self._backlinks.get(path, [])

    def get_backlink_count(self, path: str) -> int:
        return self._backlink_counts.get(path, 0)

    def search(self, query: str, limit: int = 20) -> list[SearchResult]:
        self.try_pull()
        if self._semantic_backend:
            try:
                results = self._semantic_backend.search(query, limit)
                if results:
                    return results
            except Exception:
                pass
        return self._search_backend.search(query, limit)

    def all_entries(self) -> list[Entry]:
        return list(self._entries.values())

    def entry_count(self) -> int:
        return len(self._entries)

    def tag_counts(self) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for entry in self._entries.values():
            for tag in entry.tags:
                counts[tag] += 1
        return dict(counts)

    def type_counts(self) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for entry in self._entries.values():
            counts[entry.type] += 1
        return dict(counts)
