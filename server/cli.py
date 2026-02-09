from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from server.config import load_config
from server.kb import KnowledgeBase


def _make_kb() -> KnowledgeBase:
    config = load_config()
    config.sync.auto_pull = False
    return KnowledgeBase(config)


def cmd_search(args: argparse.Namespace) -> None:
    kb = _make_kb()
    results = kb.search(args.query, limit=args.limit)
    if not results:
        print("No results found.")
        return
    for r in results:
        print(f"[{r.type}] {r.title}")
        print(f"  path: {r.path}")
        print(f"  tags: {', '.join(r.tags)}")
        print(f"  summary: {r.summary}")
        print(f"  score: {r.score}  backlinks: {r.backlink_count}")
        print()


def cmd_list(args: argparse.Namespace) -> None:
    kb = _make_kb()
    entries = kb.list_entries(
        type_filter=args.type,
        tag_filter=args.tag,
    )
    if not entries:
        print("No entries found.")
        return
    for e in entries:
        bl = kb.get_backlink_count(e.path)
        print(f"[{e.type}] {e.title}")
        print(f"  path: {e.path}")
        print(f"  tags: {', '.join(e.tags)}")
        print(f"  summary: {e.summary}")
        print(f"  edges: {len(e.edges)}  backlinks: {bl}")
        print()


def cmd_read(args: argparse.Namespace) -> None:
    kb = _make_kb()
    entry = kb.read_entry(args.path)
    if not entry:
        print(f"Entry not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    backlinks = kb.get_backlinks(args.path)

    print(f"# {entry.title}")
    print(f"type: {entry.type}")
    print(f"summary: {entry.summary}")
    print(f"tags: {', '.join(entry.tags)}")
    print(f"created: {entry.created}")
    if entry.updated:
        print(f"updated: {entry.updated}")
    if entry.edges:
        print(f"\nedges:")
        for edge in entry.edges:
            desc = f" — {edge.description}" if edge.description else ""
            print(f"  [{edge.label}] {edge.path}{desc}")
    if entry.sources:
        print(f"\nsources:")
        for s in entry.sources:
            title = f" ({s.title})" if s.title else ""
            print(f"  {s.url}{title}")
    if backlinks:
        print(f"\nbacklinks:")
        for bl in backlinks:
            desc = f" — {bl.description}" if bl.description else ""
            print(f"  [{bl.label}] {bl.path} ({bl.title}){desc}")
    print(f"\n---\n{entry.body}")


def cmd_stats(args: argparse.Namespace) -> None:
    kb = _make_kb()
    tc = kb.type_counts()
    tg = kb.tag_counts()
    total = kb.entry_count()
    total_edges = sum(len(e.edges) for e in kb.all_entries())
    print(f"Entries: {total}")
    print(f"Edges: {total_edges}")
    print(f"\nBy type:")
    for t, c in sorted(tc.items(), key=lambda x: x[1], reverse=True):
        print(f"  {t}: {c}")
    print(f"\nBy tag:")
    for t, c in sorted(tg.items(), key=lambda x: x[1], reverse=True):
        print(f"  {t}: {c}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="memex-cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=20)
    p_search.set_defaults(func=cmd_search)

    p_list = sub.add_parser("list")
    p_list.add_argument("--type", default=None)
    p_list.add_argument("--tag", default=None)
    p_list.set_defaults(func=cmd_list)

    p_read = sub.add_parser("read")
    p_read.add_argument("path")
    p_read.set_defaults(func=cmd_read)

    p_stats = sub.add_parser("stats")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
