# NotebookLM Skill-First Local File Understanding

`notebooklm-mcp-cli` now follows a **skill-first design** focused on one primary workflow:

> Help agents understand local non-code files (PDF, Word, audio, video, images, text) by indexing them into NotebookLM, then querying/reindexing seamlessly.

---

## New Design (What matters)

The project now emphasizes:

1. **Skill-first actions** via `nlm skill ...`
   - `bootstrap` (auth check + profile + index/reindex)
   - `ask` (query indexed notebook, optional file focus)
   - `reindex` (refresh notebook from local files)
2. **Automatic local file selection**
   - recursive scan
   - `.gitignore` aware
   - skips heavy/system folders
   - prioritizes supported files when NotebookLM limits are hit
3. **Persistent local state**
   - profile + notebook mapping
   - indexing metadata for repeatable reindex runs

---

## Quickstart (Skill-first)

### 1) Login once
```bash
nlm skill diagnose
nlm login --check || nlm login
```

### 2) Bootstrap skill workflow
```bash
nlm skill bootstrap project-files --repo .
```

This command:
- verifies auth,
- creates/reuses profile,
- creates notebook + indexes (first run),
- reindexes (subsequent runs).

### 3) Ask notebook questions
```bash
nlm skill ask project-files "What are the key decisions in the docs?"
```

Optional file-focused query:
```bash
nlm skill ask project-files "Summarize this file" --file docs/spec.pdf
```

### 4) Reindex when files change
```bash
nlm skill reindex project-files
```


### 5) Link skill for your agent (optional but recommended)
```bash
nlm skill add
```

This auto-detects the active framework and copies `SKILL.md` + `references/` into the workspace skill path.

If detection is ambiguous, pass a framework explicitly:

```bash
nlm skill add claude-code --level project
nlm skill add antigravity --level project
```

Legacy install flow still works via `nlm skill install <tool>`.

---

## File Indexing Behavior

- Scans the selected repo/directory recursively.
- Supports: text, PDF, video, audio, image, Word documents.
- Respects `.gitignore`.
- Skips common folders like `.git`, `node_modules`, `venv`, caches, and build outputs.
- If over NotebookLM limits, uses priority + size-based selection.

---

## Optional Profile Commands

If you want explicit control, use:

```bash
nlm indexing set my-work --repo .
nlm indexing plan my-work --max-files 50
nlm indexing run my-work
nlm indexing show my-work
nlm indexing list
```

---

## Repo Structure (Relevant parts)

- `skills/notebooklm-understanding/SKILL.md` — skill-facing workflow
- `src/notebooklm_tools/cli/commands/skill.py` — skill action commands
- `src/notebooklm_tools/cli/commands/indexing.py` — optional profile commands
- `src/notebooklm_tools/services/local_indexing.py` — scan/classify/select/metadata
- `src/notebooklm_tools/services/indexing_utility.py` — profile persistence

---

## Current Status

This repository is actively being simplified around the skill-first UX.
Legacy details from earlier MCP/CLI-heavy docs are intentionally removed from this README.
