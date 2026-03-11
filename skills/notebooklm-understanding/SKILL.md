---
name: notebooklm-understanding
description: Skill-first workflow for understanding local non-code files (PDF, video, audio, image, docs, text) through NotebookLM with zero-setup bootstrap, reindexing, and querying.
---

# NotebookLM Understanding Skill

## Goal
Let users work entirely through the skill surface (no manual setup flow).

## Commands (agent-driven)
0. One-time setup (no manual file copying)
```bash
# Option A: zero-install invocation (recommended for skill runners)
uvx --from notebooklm-mcp-cli nlm --help

# Option B: from this repository
uv sync
uv run nlm --help
```

1. Install skill for your agent
```bash
nlm skill install claude-code --level project
nlm skill install cursor --level project
nlm skill install codex --level project
nlm skill install opencode --level project
nlm skill install gemini-cli --level project
nlm skill install antigravity --level project
nlm skill install cline --level project
nlm skill install openclaw --level project
```

2. Bootstrap / first run:
```bash
nlm skill bootstrap project-files --repo .
```
3. Ask notebook-wide question:
```bash
nlm skill ask project-files "What are the main risks discussed in the docs?"
```
4. Ask file-focused question:
```bash
nlm skill ask project-files "Summarize key decisions" --file docs/design.pdf
```
5. Reindex after file changes:
```bash
nlm skill reindex project-files
```

## Behavior
- If auth is missing, command prompts to run `nlm login` once.
- First bootstrap creates notebook and indexes files.
- Later bootstrap/reindex updates the same notebook.
- Indexing respects `.gitignore` and common excluded folders.
