# ContextBridge Bootstrap (starter)

This repo provides a clean install flow for bootstrapping a ContextBridge-style project from the product vision doc while using [`jacob-bd/notebooklm-mcp-cli`](https://github.com/jacob-bd/notebooklm-mcp-cli) as a dependency.

## What this starter sets up

- Installs `notebooklm-mcp-cli` directly from GitHub as a Python dependency.
- Syncs your local `skills/` folders into common IDE skill directories:
  - `~/.codex/skills`
  - `~/.cursor/skills`
  - `~/.vscode/skills`
  - `~/.antigravity/skills`
- Ensures MCP server entries for `contextbridge-install --ensure-only` in:
  - Cursor project config: `.cursor/mcp.json`
  - Claude Desktop config: `~/.config/Claude/claude_desktop_config.json` (or macOS equivalent)
  - Antigravity config: `~/.config/antigravity/mcp.json`

## Quickstart

```bash
./scripts/install_contextbridge.sh
```

Or run manually:

```bash
python -m pip install -e .
contextbridge-install --project-root . --skills-dir skills
```

## CLI options

```bash
contextbridge-install \
  --project-root . \
  --skills-dir skills \
  --ide-target ~/.my-custom-ide/skills \
  --overwrite
```

Flags:

- `--ide-target`: Add extra skill sync targets (repeatable).
- `--overwrite`: Replace existing skill folders in targets.
- `--skip-dependency-install`: Skip installing `notebooklm-mcp-cli`.
- `--skip-cursor-config`: Skip writing `.cursor/mcp.json`.
- `--skip-claude-config`: Skip writing Claude Desktop MCP config.
- `--skip-antigravity-config`: Skip writing Antigravity MCP config.
- `--ensure-only`: No-op mode used by MCP config health checks.

## Bringing in prior skills from backup branch

If your old skills live in another repo/branch, copy them into this repo's `skills/` folder and re-run installer:

```bash
cp -R /path/to/exported/skills/* ./skills/
./scripts/install_contextbridge.sh --overwrite
```

## Product vision alignment

This bootstrap intentionally supports the current MVP scope from `docs/PROJECT_VISION_CONTEXTBRIDGE.md`:

- distribution-ready MCP setup for IDE workflows,
- notebooklm dependency path for provider integration,
- repeatable local-first installation workflow before adding ingestion/retrieval features.
