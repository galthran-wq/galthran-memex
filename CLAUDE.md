# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Memex is a personal knowledge base system with an MCP (Model Context Protocol) server. It manages atomic knowledge entries as markdown files with typed edges, providing AI agents with tools to search, read, and add knowledge.

**Write path**: User requests knowledge addition → MCP `kb_add` tool → Cursor Cloud Agent spawns → Agent reads `.cursor/rules/knowledge-base.mdc`, creates properly formatted entries with cross-references → Opens PR for review.

**Read path**: MCP server reads from local disk (fast, no API calls).

## Core Commands

### Running the server
```bash
uv run memex                    # Start MCP server on localhost:8787
docker compose up               # Run with Docker
```

### CLI tools (for querying KB)
```bash
uv run python -m server.cli search "query"
uv run python -m server.cli list --type concept --tag ml
uv run python -m server.cli read /knowledge/entry.md
uv run python -m server.cli stats
```

### Viewer (GitHub Pages site)
```bash
uv run python viewer/build.py   # Build data.json from knowledge entries
```

## Architecture

### Knowledge Model
- **Entries**: Flat structure at `knowledge/{slug}.md` (slug is lowercase-hyphenated from title)
- **Types**: `concept`, `reference`, `insight`, `question`, `note`
- **Edges**: Typed relationships in YAML frontmatter (e.g., `uses`, `based_on`, `alternative`)
- **Backlinks**: Computed dynamically by server from forward edges
- **Assets**: Images in `knowledge/assets/`, referenced as `![alt](/knowledge/assets/file.png)`

### Entry Structure
YAML frontmatter with `title`, `type`, `summary`, `tags`, `created`, `edges`, `sources`, followed by markdown body with section templates per type (see `.cursor/rules/knowledge-base.mdc:36-68`).

### Server Components
- `server/main.py` - FastMCP server setup, repo cloning for remote deployment
- `server/tools.py` - MCP tools: `kb_search`, `kb_list`, `kb_read`, `kb_add`, `kb_status`, `kb_upload`
- `server/kb.py` - KnowledgeBase class, entry parsing, edge/backlink management
- `server/cursor_client.py` - Cursor Cloud Agents API client for `kb_add`
- `server/github_client.py` - GitHub API client for image uploads and branch management
- `server/semantic.py` - Optional OpenAI embeddings for semantic search
- `server/cli.py` - Command-line interface for KB queries
- `server/config.py` - Config loading from `config.yaml` and environment

### Search Backends
Configured in `config.yaml` under `search.backend`:
- `bm25` (default) - BM25Okapi term-frequency ranking
- `substring` - Zero-dependency fallback
- `semantic` - OpenAI embeddings (requires `OPENAI_API_KEY`)

### Viewer
Static single-page app with entry list, filters, and vis.js graph visualization. Deployed to GitHub Pages automatically when PRs changing `knowledge/**` or `viewer/**` are merged to master.

## Configuration

### Local setup
1. Copy `.env.example` to `.env` and set `CURSOR_API_KEY`
2. Edit `config.yaml` - set `github.owner` and `github.repo`
3. Add to Cursor MCP config (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "memex": {
      "url": "http://localhost:8787/mcp"
    }
  }
}
```

### Remote deployment (Docker)
Set environment variables:
- `MEMEX_GIT_URL` - repo URL for cloning
- `MEMEX_GIT_TOKEN` - GitHub PAT for private repos
- `MEMEX_AUTH_TOKEN` - Bearer token for MCP endpoint auth
- `CURSOR_API_KEY` - For kb_add (Cloud Agents API)
- `OPENAI_API_KEY` - For semantic search (optional)

## Key Rules from .cursor/rules/knowledge-base.mdc

When modifying knowledge entries:
1. **Atomicity**: One entry = one concept (split only if concept is general and reusable)
2. **Cross-references**: Every connection must be a typed edge in frontmatter with label and description
3. **Bidirectional edges**: When creating entry A with edge to B, update B to add edge back to A
4. **Reuse**: Check if entry exists before creating (use CLI search/list)
5. **Slug format**: lowercase-hyphenated, no special characters
6. **LaTeX**: Use `$...$` for inline math, `$$...$$` for display math

## Dependencies

- Python 3.12+ (uses `uv` for package management)
- Core: `mcp[cli]`, `httpx`, `pyyaml`, `python-dotenv`, `rank-bm25`
- Optional: `openai` (semantic search), `mistune` (viewer)
