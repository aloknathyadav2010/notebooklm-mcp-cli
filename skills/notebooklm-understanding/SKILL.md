---
name: notebooklm-understanding
description: Skill-first workflow for understanding local non-code files (PDF, video, audio, image, docs, text) through NotebookLM with zero-setup bootstrap, reindexing, and querying.
---

# NotebookLM Understanding Skill

## Goal
Let users work entirely through the skill surface (no manual setup flow).

## Commands (agent-driven)
1. Bootstrap / first run:
```bash
nlm skill bootstrap project-files --repo .
```
2. Ask notebook-wide question:
```bash
nlm skill ask project-files "What are the main risks discussed in the docs?"
```
3. Ask file-focused question:
```bash
nlm skill ask project-files "Summarize key decisions" --file docs/design.pdf
```
4. Reindex after file changes:
```bash
nlm skill reindex project-files
```

## Behavior
- If auth is missing, command prompts to run `nlm login` once.
- First bootstrap creates notebook and indexes files.
- Later bootstrap/reindex updates the same notebook.
- Indexing respects `.gitignore` and common excluded folders.
