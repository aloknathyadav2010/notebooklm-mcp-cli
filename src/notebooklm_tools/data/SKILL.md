---
name: nlm-skill
description: "CLI-first guide for NotebookLM using the `nlm` command. Use this skill for auth, notebook/source management, querying, indexing, generation, and downloads with standard Bash tools."
---

# NotebookLM CLI Expert

This skill is **CLI-only** and assumes `nlm` is the primary interface.

## Startup Checklist (Run First)

1. Ensure `nlm` is callable:
```bash
nlm skill diagnose
```

2. Authenticate:
```bash
nlm login --check || nlm login
```

3. If `nlm` is missing from PATH, install/fix it:
```bash
uv tool install --force notebooklm-mcp-cli
```

## Zero-Setup Workspace Flow

Use this when the user wants fast understanding of local project files.

```bash
nlm skill bootstrap project-files --repo .
nlm skill ask project-files "What are the key decisions in this repo?"
```

After local file changes:
```bash
nlm skill reindex project-files
```

## Skill Injection / Linking

To make this skill visible immediately in a workspace, run:

```bash
nlm skill add
```

- Auto-detects framework from workspace markers (`.agent`, `.claude`, `.cursor`, `.codex`, etc.)
- Defaults to Antigravity project path (`.agent/skills/nlm-skill`) when detection is unclear
- Use `--force` to overwrite existing files

Explicit framework example:
```bash
nlm skill add claude-code --level project
```

Alias command:
```bash
nlm skill inject
```

## Core CLI Commands

### Authentication
```bash
nlm login
nlm login --check
nlm login switch <profile>
nlm login profile list
```

### Notebooks
```bash
nlm notebook list
nlm notebook create "Title"
nlm notebook query <notebook-id> "question"
nlm notebook delete <notebook-id> --confirm
```

### Sources
```bash
nlm source add <notebook-id> --url "https://..."
nlm source add <notebook-id> --text "content" --title "Title"
nlm source add <notebook-id> --file ./path/to/file.pdf
nlm source list <notebook-id>
nlm source delete <source-id> --confirm
```

### Studio Generation
```bash
nlm audio create <notebook-id> --confirm
nlm report create <notebook-id> --confirm
nlm slides create <notebook-id> --confirm
nlm studio status <notebook-id>
```

### Downloads / Exports
```bash
nlm download source <source-id> -o ./source.txt
nlm download studio <asset-id> -o ./asset.mp3
```

## Critical Rules

1. Always authenticate before operations.
2. Always ask user before destructive commands.
3. Always include `--confirm` on generation/delete commands that require confirmation.
4. Never use interactive REPL for agents (`nlm chat start`); use one-shot commands.
5. Use default compact output for token efficiency; use `--json` only when parsing.

## Help & Discovery

```bash
nlm --help
nlm --ai
nlm <command> --help
```
