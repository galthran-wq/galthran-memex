from __future__ import annotations

from server.kb import KnowledgeBase


def build_prompt(
    summary: str,
    kb: KnowledgeBase,
    images: list[str] | None = None,
) -> str:
    parts: list[str] = []

    parts.append("You are adding knowledge to a personal knowledge base.\n")
    parts.append("## Knowledge to Add\n")
    parts.append(summary)
    parts.append("")

    results = kb.search(summary, limit=5)
    if results:
        parts.append("## Potentially Related Entries\n")
        for r in results:
            entry = kb.read_entry(r.path)
            if entry:
                parts.append(f"### {entry.path}\n")
                parts.append(entry.raw)
                parts.append("")

    entries = kb.all_entries()
    if entries:
        parts.append("## All Existing Entries\n")
        if len(entries) <= 500:
            parts.append("path | title | type | tags | summary")
            for e in entries:
                tags = ", ".join(e.tags)
                parts.append(f"{e.path} | {e.title} | {e.type} | {tags} | {e.summary}")
        else:
            top_entries = sorted(
                entries,
                key=lambda e: len(e.edges) + kb.get_backlink_count(e.path),
                reverse=True,
            )[:50]
            related_paths = {r.path for r in results}
            relevant = [e for e in entries if e.path in related_paths]
            combined = {e.path: e for e in top_entries + relevant}
            parts.append(
                f"Showing {len(combined)} of {len(entries)} entries "
                f"(top connected + most relevant). Use CLI for full list."
            )
            parts.append("path | title | type | tags | summary")
            for e in combined.values():
                tags = ", ".join(e.tags)
                parts.append(f"{e.path} | {e.title} | {e.type} | {tags} | {e.summary}")
        parts.append("")

    if images:
        parts.append("## Available Images\n")
        parts.append(
            "These images have been uploaded and are available for use in entries. "
            "Reference them with markdown image syntax: `![alt text](/path)`"
        )
        for img in images:
            parts.append(f"- /{img}")
        parts.append("")

    parts.append("## Instructions\n")
    parts.append("- Read .cursor/rules/ for entry format and conventions")
    parts.append("- Decompose the knowledge above into atomic entries (one concept per file)")
    parts.append("- Check existing entries — update rather than duplicate")
    parts.append("- Add edges from new entries to related existing entries")
    parts.append("- Update related existing entries with edges pointing back to new entries")
    parts.append(
        "- For dynamic queries, use the CLI: "
        '`uv run python -m server.cli search "query"`, '
        "`uv run python -m server.cli list --type concept`, "
        "`uv run python -m server.cli read /knowledge/slug.md`"
    )
    if images:
        parts.append(
            "- Use the available images in relevant entries where they add value "
            "(e.g. architecture diagrams, figures from papers)"
        )
    parts.append("- Open a PR with all changes")

    return "\n".join(parts)
