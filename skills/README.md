# Skills

This folder makes skill-centric workflows visible from the repository structure.

Current MVP:
- `notebooklm-understanding/` — zero-setup bootstrap + query + reindex around NotebookLM indexing.

## Get Started (All Supported Agents)

Use these commands to validate and install the NotebookLM skill with **no manual file copying**.

### 1) Required setup (once)

```bash
# from this repository
uv sync

# run CLI directly from source
uv run nlm --help
```

### 2) Install for each agent

Use these commands to install the NotebookLM skill in the default location for each agent:

```bash
nlm skill install claude-code
nlm skill install cursor
nlm skill install codex
nlm skill install opencode
nlm skill install gemini-cli
nlm skill install antigravity
nlm skill install cline
nlm skill install openclaw
```

For project-local installs instead of user-level installs, add `--level project`.

### 3) Verify skill actions work

```bash
nlm skill bootstrap project-files --repo .
nlm skill ask project-files "What are the key decisions in the docs?"
nlm skill reindex project-files
```
