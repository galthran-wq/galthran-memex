from __future__ import annotations

import hashlib
import json
import logging
import math
from pathlib import Path

from server.kb import Entry, SearchResult

logger = logging.getLogger("memex.semantic")


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _entry_text(entry: Entry) -> str:
    return f"{entry.title} {entry.summary} {' '.join(entry.tags)} {entry.body}"


def _entry_hash(entry: Entry) -> str:
    return hashlib.md5(_entry_text(entry).encode()).hexdigest()


class SemanticBackend:
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        cache_path: Path | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._cache_path = cache_path or Path(".memex/embeddings.json")
        self._entries: list[Entry] = []
        self._embeddings: dict[str, list[float]] = {}
        self._hashes: dict[str, str] = {}
        self._backlink_counts: dict[str, int] = {}
        self._client: object | None = None

        self._load_cache()

    def set_backlink_counts(self, counts: dict[str, int]) -> None:
        self._backlink_counts = counts

    def _load_cache(self) -> None:
        if self._cache_path.exists():
            try:
                data = json.loads(self._cache_path.read_text())
                self._embeddings = data.get("embeddings", {})
                self._hashes = data.get("hashes", {})
            except Exception:
                logger.warning("Failed to load embeddings cache, starting fresh")

    def _save_cache(self) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "embeddings": self._embeddings,
            "hashes": self._hashes,
        }
        self._cache_path.write_text(json.dumps(data))

    def _get_openai_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self._api_key)
            except ImportError:
                raise RuntimeError("openai package not installed. Install with: uv pip install openai")
        return self._client

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        client = self._get_openai_client()
        response = client.embeddings.create(input=texts, model=self._model)
        return [item.embedding for item in response.data]

    def _embed_single(self, text: str) -> list[float]:
        return self._embed_texts([text])[0]

    def index(self, entries: list[Entry]) -> None:
        self._entries = entries

        to_embed: list[tuple[str, str]] = []
        for entry in entries:
            h = _entry_hash(entry)
            if entry.path in self._hashes and self._hashes[entry.path] == h:
                continue
            to_embed.append((entry.path, _entry_text(entry)))
            self._hashes[entry.path] = h

        stale = set(self._embeddings.keys()) - {e.path for e in entries}
        for path in stale:
            del self._embeddings[path]
            self._hashes.pop(path, None)

        if to_embed:
            logger.info("Embedding %d new/changed entries...", len(to_embed))
            batch_size = 100
            for i in range(0, len(to_embed), batch_size):
                batch = to_embed[i : i + batch_size]
                paths = [p for p, _ in batch]
                texts = [t for _, t in batch]
                try:
                    vectors = self._embed_texts(texts)
                    for path, vec in zip(paths, vectors):
                        self._embeddings[path] = vec
                except Exception as e:
                    logger.warning("Failed to embed batch: %s", e)

            self._save_cache()

    def search(self, query: str, limit: int = 20) -> list[SearchResult]:
        if not self._entries or not self._embeddings:
            return []

        try:
            query_vec = self._embed_single(query)
        except Exception as e:
            logger.warning("Failed to embed query: %s", e)
            return []

        scored: list[tuple[Entry, float]] = []
        for entry in self._entries:
            vec = self._embeddings.get(entry.path)
            if vec is None:
                continue
            score = _cosine_similarity(query_vec, vec)
            scored.append((entry, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for entry, score in scored[:limit]:
            if score < 0.1:
                break
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
