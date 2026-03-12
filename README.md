# NotebookLM MCP + CLI (New User Onboarding Guide)

`notebooklm-mcp-cli` gives you two interfaces in one package:

- **`nlm` CLI** for direct terminal workflows.
- **`notebooklm-mcp` MCP server** for tools like Claude Desktop.

If you are brand new, this guide walks you through setup end-to-end with concrete steps for each install option.

> **Roadmap vision:** See `docs/PROJECT_VISION_CONTEXTBRIDGE.md` for the high-level ContextBridge architecture and phased direction.
> **Setup goal + audit:** See `docs/README_SETUP_AUDIT_GOAL_SEAMLESS_INSTALL.md` for install-source issues and the one-command setup target.

---

## 1) What you can do with this package

- Create/manage NotebookLM notebooks.
- Upload sources (URL, text, Drive, local files).
- Query notebook contents.
- Generate Studio artifacts.
- Run **local indexing** for folders of files.
- Use **skill-first workflows** (`bootstrap`, `ask`, `reindex`) from CLI **and now via MCP tools**.

---

## 2) Prerequisites (do this first)

1. **Python 3.10+**
   ```bash
   python --version
   ```
2. (Recommended) one installer: **uv** or **pipx**
   - uv: <https://docs.astral.sh/uv/>
   - pipx: <https://pypa.github.io/pipx/>
3. A Google account with NotebookLM access.

---

## 3) Installation options (pick one)

## Option A — Install with `uv` (recommended)

### Step A1: Install tool globally
```bash
uv tool install notebooklm-mcp-cli
```

### Step A2: Verify commands are available
```bash
nlm --version
notebooklm-mcp --help
```

### Step A3: If command is missing, refresh install
```bash
uv tool install --force notebooklm-mcp-cli
```

---

## Option B — Install with `pipx`

### Step B1: Install tool globally
```bash
pipx install notebooklm-mcp-cli
```

### Step B2: Verify
```bash
nlm --version
notebooklm-mcp --help
```

### Step B3: If needed, force reinstall
```bash
pipx install --force notebooklm-mcp-cli
```

---

## Option C — Run from source (for contributors)

### Step C1: Clone and enter repo
```bash
git clone <your-fork-or-repo-url>
cd notebooklm-mcp-cli
```

### Step C2: Install editable
```bash
pip install -e .
```

### Step C3: Verify local run
```bash
PYTHONPATH=src python -m notebooklm_tools.cli.main --help
PYTHONPATH=src python -m notebooklm_tools.mcp.server --help
```

---

## 4) First-time authentication (required)

Run:
```bash
nlm login
```

Then confirm:
```bash
nlm login --check
```

If you switch Google accounts later:
```bash
nlm login switch <profile>
```

---

## 5) Quickstart with CLI (skill-first)

### Step 1: Bootstrap local indexing
```bash
nlm skill bootstrap project-files --repo .
```

### Step 2: Ask questions
```bash
nlm skill ask project-files "What are the main decisions in this project?"
```

Optional file-focused ask:
```bash
nlm skill ask project-files "Summarize this" --file docs/spec.pdf
```

### Step 3: Reindex when files change
```bash
nlm skill reindex project-files
```

### Step 4 (optional): Copy skill docs into your workspace
```bash
nlm skill add claude-code --level project
```

---

## 6) MCP setup for Claude Desktop

Use `notebooklm-mcp` with stdio transport.

Add a server entry in your Claude Desktop MCP config (example):

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "notebooklm-mcp",
      "args": ["--transport", "stdio"]
    }
  }
}
```

Then restart Claude Desktop.

### Verify connection
Ask Claude to call:
- `server_info`
- `notebook_list`

If auth errors appear, run `nlm login` in terminal and retry.

---

## 7) New MCP skill utility tools

In addition to core NotebookLM tools, MCP now includes skill workflow helpers:

- `skill_profiles` — list saved skill profiles.
- `skill_bootstrap` — auth check + profile setup + index/reindex.
- `skill_ask` — ask using profile-linked notebook.
- `skill_reindex` — refresh indexed notebook for a profile.
- `skill_add_to_workspace` — copy bundled `SKILL.md` + references to framework path.
- `skill_diagnose_cli` — report whether `nlm` is in PATH.

This lets you test skill workflows directly from Claude Desktop without manually invoking CLI commands.

---

## 8) Optional profile-based indexing commands

If you want more control than `nlm skill bootstrap`:

```bash
nlm indexing set my-work --repo .
nlm indexing plan my-work --max-files 50
nlm indexing run my-work
nlm indexing show my-work
nlm indexing list
```

---

## 9) Troubleshooting checklist

1. `nlm` not found:
   - reinstall with `uv tool install --force notebooklm-mcp-cli`.
2. MCP auth issues:
   - run `nlm login` again.
3. Wrong account:
   - run `nlm login switch <profile>`.
4. CLI works but Claude cannot:
   - confirm Claude Desktop MCP config points to `notebooklm-mcp` and restart app.

---

## 10) Useful commands

```bash
# CLI help
nlm --help
nlm skill --help

# MCP server help
notebooklm-mcp --help

# Run MCP server manually (stdio)
notebooklm-mcp --transport stdio

# Run tests from source checkout
PYTHONPATH=src pytest -q
```
