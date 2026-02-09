from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from server.config import Config
from server.cursor_client import CursorClient, CursorClientError
from server.kb import KnowledgeBase
from server.prompt import build_prompt


def register_tools(mcp: FastMCP, kb: KnowledgeBase, config: Config) -> None:

    @mcp.tool(
        description=(
            "Search the knowledge base. Returns matching entries with "
            "title, path, type, tags, summary, and backlink count. "
            "Entries are atomic knowledge units linked via typed edges."
        )
    )
    def kb_search(query: str) -> str:
        results = kb.search(query, limit=20)
        if not results:
            return "No results found."
        lines = []
        for r in results:
            lines.append(
                f"[{r.type}] {r.title}\n"
                f"  path: {r.path}\n"
                f"  tags: {', '.join(r.tags)}\n"
                f"  summary: {r.summary}\n"
                f"  backlinks: {r.backlink_count}"
            )
        return "\n\n".join(lines)

    @mcp.tool(
        description=(
            "List knowledge base entries. Filter by type "
            "(concept, reference, insight, question, note) and/or tag. "
            "Returns title, type, summary, tags, and connection density "
            "for each entry."
        )
    )
    def kb_list(type: str | None = None, tag: str | None = None) -> str:
        entries = kb.list_entries(type_filter=type, tag_filter=tag)
        if not entries:
            return "No entries found."
        lines = []
        for e in entries:
            bl = kb.get_backlink_count(e.path)
            lines.append(
                f"[{e.type}] {e.title}\n"
                f"  path: {e.path}\n"
                f"  tags: {', '.join(e.tags)}\n"
                f"  summary: {e.summary}\n"
                f"  edges: {len(e.edges)}  backlinks: {bl}"
            )
        return "\n\n".join(lines)

    @mcp.tool(
        description=(
            "Read a knowledge base entry by path "
            "(e.g. /knowledge/rlhf.md). Returns frontmatter "
            "(title, summary, tags, edges, sources) and markdown body "
            "with cross-reference links. Also returns computed backlinks."
        )
    )
    def kb_read(path: str) -> str:
        entry = kb.read_entry(path)
        if not entry:
            return f"Entry not found: {path}"
        backlinks = kb.get_backlinks(path)
        parts = [
            f"# {entry.title}",
            f"type: {entry.type}",
            f"summary: {entry.summary}",
            f"tags: {', '.join(entry.tags)}",
            f"created: {entry.created}",
        ]
        if entry.updated:
            parts.append(f"updated: {entry.updated}")
        if entry.edges:
            parts.append("\nedges:")
            for edge in entry.edges:
                desc = f" — {edge.description}" if edge.description else ""
                parts.append(f"  [{edge.label}] {edge.path}{desc}")
        if entry.sources:
            parts.append("\nsources:")
            for s in entry.sources:
                title = f" ({s.title})" if s.title else ""
                parts.append(f"  {s.url}{title}")
        if backlinks:
            parts.append("\nbacklinks:")
            for bl in backlinks:
                desc = f" — {bl.description}" if bl.description else ""
                parts.append(f"  [{bl.label}] {bl.path} ({bl.title}){desc}")
        parts.append(f"\n---\n{entry.body}")
        return "\n".join(parts)

    @mcp.tool(
        description=(
            "Add knowledge to the base. Pass a natural language summary — "
            "concepts, insights, references, questions. A cloud agent will "
            "decompose it into atomic entries, create cross-references, "
            "and open a PR. Returns agent ID for status tracking."
        )
    )
    def kb_add(summary: str) -> str:
        if not summary or not summary.strip():
            return "Error: Summary cannot be empty"
        if not config.cursor_api_key:
            return "Error: CURSOR_API_KEY not configured"
        if not config.github.owner or not config.github.repo:
            return "Error: GitHub repository not configured in config.yaml"

        prompt_text = build_prompt(summary.strip(), kb)
        repo_url = f"https://github.com/{config.github.owner}/{config.github.repo}"

        client = CursorClient(config.cursor_api_key)
        try:
            result = client.launch_agent(
                prompt=prompt_text,
                repository=repo_url,
                ref=config.github.default_branch,
            )
        except CursorClientError as e:
            return f"Error: {e}"
        finally:
            client.close()

        return (
            f"Cloud agent launched.\n"
            f"Agent ID: {result.agent_id}\n"
            f"Dashboard: {result.agent_url}\n"
            f"Use kb_status with this agent_id to check progress."
        )

    @mcp.tool(
        description=(
            "Check status of a knowledge base update. "
            "Returns state (running/completed/failed) and PR URL when ready."
        )
    )
    def kb_status(agent_id: str) -> str:
        if not config.cursor_api_key:
            return "Error: CURSOR_API_KEY not configured"

        client = CursorClient(config.cursor_api_key)
        try:
            status = client.get_status(agent_id)
        except CursorClientError as e:
            return f"Error: {e}"
        finally:
            client.close()

        parts = [
            f"Status: {status.status}",
            f"Dashboard: {status.agent_url}",
        ]
        if status.pr_url:
            parts.append(f"PR: {status.pr_url}")
        return "\n".join(parts)
