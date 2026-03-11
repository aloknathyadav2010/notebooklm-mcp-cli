# AGENTS.md

This file provides a concise contributor/agent overview for this repository.

## Project Overview

`notebooklm-mcp-cli` is a unified Python package that ships:
- `nlm`: a NotebookLM CLI.
- `notebooklm-mcp`: an MCP server exposing NotebookLM tools for coding assistants.

Core capabilities:
- Notebook CRUD and source management (URL/text/Drive/file).
- Query/chat over notebook content.
- Studio generation (audio/video/reports/slides/infographics/etc.).
- Sharing, exports, downloads, research workflows.
- **Local indexing tools** for recursive ingestion of local files into NotebookLM:
  - `notebook_index_local`
  - `notebook_reindex_local`

## Architecture Map

- `src/notebooklm_tools/core/`: low-level NotebookLM API client and mixins.
- `src/notebooklm_tools/services/`: shared business logic and validation.
- `src/notebooklm_tools/cli/`: Typer CLI commands (`nlm`).
- `src/notebooklm_tools/mcp/`: FastMCP server + tool modules.
- `tests/`: unit/integration/e2e coverage.

## Local Indexing (New Workflow)

Implementation files:
- `src/notebooklm_tools/services/local_indexing.py`
- `src/notebooklm_tools/mcp/tools/indexing.py`

Behavior summary:
- Scans root directory recursively for supported text/PDF/video/image/Word files.
- Applies a max-file cap with priority for text/PDF/video, then by largest size.
- Persists metadata in `.notebooklm/indexed_notebooks.json` by default.
- Reindex flow clears existing notebook sources, then re-uploads selected files.

## Dev Commands

```bash
# Lint/type/test examples
python -m py_compile src/notebooklm_tools/mcp/server.py
PYTHONPATH=src pytest -q

# Run CLI
PYTHONPATH=src python -m notebooklm_tools.cli.main --help

# Run MCP server
PYTHONPATH=src python -m notebooklm_tools.mcp.server --transport stdio
```

## Notes for Agents

- Prefer service-layer logic for reusable behavior; keep MCP/CLI thin.
- Register new MCP tools in:
  - `src/notebooklm_tools/mcp/tools/__init__.py`
  - `src/notebooklm_tools/mcp/server.py`
- Add focused tests under `tests/services/` and/or relevant module folders.
