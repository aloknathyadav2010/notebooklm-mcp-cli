# Setup Audit + Goal: Seamless Repo-Only Installation

## Goal (What we are optimizing for)

Make setup feel "one command" while ensuring users install and run from **this repository** (or an explicit fork/branch), not an unrelated package resolution path.

Target outcomes:
1. Default instructions are repo-pinned.
2. `nlm setup add json` can emit repo-pinned `uvx` config.
3. CLI diagnostics/update messages do not nudge users back to package-name-only flows.
4. Documentation and metadata are internally consistent.

---

## Current State (Static Audit Summary)

### Install guidance is mostly package-name based
- `README.md`, `docs/CLI_GUIDE.md`, and `docs/MCP_GUIDE.md` currently center on:
  - `uv tool install notebooklm-mcp-cli`
  - `pipx install notebooklm-mcp-cli`

**Risk:** users may install a PyPI release that does not match this repo branch/fork.

### JSON setup generator is hardcoded to package-name `uvx`
- `src/notebooklm_tools/cli/commands/setup.py` (`_setup_json`) currently emits:
  - `"command": "uvx"`
  - `"args": ["--from", "notebooklm-mcp-cli", "notebooklm-mcp"]`

**Risk:** even if docs are pinned, generated MCP config drifts back to package-name source.

### Diagnostics and update hints reinforce package-name install/upgrade
- `src/notebooklm_tools/cli/commands/skill.py` (`diagnose`) recommends only package-name installs.
- `src/notebooklm_tools/mcp/tools/skill_utility.py` (`skill_diagnose_cli`) gives same package-name message.
- `src/notebooklm_tools/cli/utils.py` and `src/notebooklm_tools/mcp/tools/server.py` expose package-name update commands.

**Risk:** repo-pinned users get redirected to generic upgrade behavior.

### Repository metadata still references upstream URLs
- `pyproject.toml` `[project.urls]` points to `jacob-bd/notebooklm-mcp-cli`.

**Risk:** mixed ownership/source-of-truth signals during onboarding and troubleshooting.

---

## Recommended Strategy

### 1) Define one canonical source model
Adopt a single explicit source selector used across docs + CLI:
- **Recommended:** git URL pinned to repo (and optional branch/tag/commit).
- **Alternative:** package-name install (labeled compatibility channel).

Example canonical install shape:
```bash
uv tool install --force "git+https://github.com/<owner>/notebooklm-mcp-cli.git@<ref>"
```

### 2) Make repo-pinned source first-class in setup JSON flow
Enhance `nlm setup add json` so users choose source strategy in `uvx` mode:
- `uvx --from git+https://... notebooklm-mcp` (recommended)
- `uvx --from notebooklm-mcp-cli notebooklm-mcp` (compat)

### 3) Keep diagnostics source-aware
Update diagnose/help/update messaging so it either:
- prints repo-pinned commands by default, or
- asks for/reads configured source mode and mirrors it.

### 4) Offer a repository-owned bootstrap entry point
Add `install.sh` in repo root for one-command onboarding.

Expected behavior:
- checks/install `uv` (or clear fallback instructions),
- installs from repo-pinned git URL,
- validates `nlm` + `notebooklm-mcp`,
- prints PATH remediation tips.

---

## Implementation Plan (Execution-Oriented)

### Phase A — Decide and centralize install source constants
**Files:** `src/notebooklm_tools/cli/constants.py` (new) or `src/notebooklm_tools/cli/commands/setup.py`, plus reuse points in diagnose/update modules.

Actions:
1. Introduce canonical constants for:
   - `DEFAULT_GIT_INSTALL_URL`
   - `DEFAULT_GIT_REF` (branch/tag)
   - package-name fallback string
2. Refactor command/help text generators to consume constants instead of hardcoded strings.

Exit criteria:
- No duplicated install-source strings across CLI/MCP messaging code paths.

### Phase B — Upgrade `nlm setup add json`
**File:** `src/notebooklm_tools/cli/commands/setup.py` (`_setup_json`)

Actions:
1. Add an interactive question for source strategy when `config_type == "uvx"`.
2. Build `args` for both repo-pinned and package-name modes.
3. Keep existing regular command/full-path modes unchanged.

Exit criteria:
- Generated JSON can be repo-pinned without manual edits.

### Phase C — Align docs to repo-first onboarding
**Files:** `README.md`, `docs/CLI_GUIDE.md`, `docs/MCP_GUIDE.md`

Actions:
1. Move repo-pinned install command to top position in each guide.
2. Keep package-name install in a clearly labeled alternate section.
3. Add a short rationale: "ensures install from this repo/ref".
4. Ensure MCP examples using `uvx --from ...` include pinned variant first.

Exit criteria:
- A new user following docs installs from this repo by default.

### Phase D — Align diagnostics and update messaging
**Files:**
- `src/notebooklm_tools/cli/commands/skill.py`
- `src/notebooklm_tools/mcp/tools/skill_utility.py`
- `src/notebooklm_tools/cli/utils.py`
- `src/notebooklm_tools/mcp/tools/server.py`

Actions:
1. Replace package-name-only remediation strings with repo-aware options.
2. Update `update_command` fields/messages to avoid forcing package-name-only upgrades.
3. If source mode cannot be detected, print both commands with "recommended" label.

Exit criteria:
- No command path in diagnostics contradicts repo-first strategy.

### Phase E — Metadata and ownership consistency
**File:** `pyproject.toml`

Actions:
1. Update `[project.urls]` to the intended repository owner/fork.
2. Validate that docs and URLs point to the same source of truth.

Exit criteria:
- Packaging metadata and install instructions reference the same repo.

### Phase F — Add one-command bootstrap script
**File:** `install.sh` (new)

Actions:
1. Implement a POSIX shell script for repo-pinned install.
2. Include basic checks (`uv`, PATH, command presence).
3. Print post-install "next steps" and validation commands.

Exit criteria:
- `curl .../install.sh | bash` is a supported path documented in README.

---

## Validation Checklist (No Runtime Required for Planning)

- `rg -n "uv tool install notebooklm-mcp-cli|uvx --from notebooklm-mcp-cli" README.md docs src`
  - expected: package-name-only defaults removed from primary guidance.
- `nlm setup add json` flow review confirms repo-pinned `uvx` output option exists.
- Diagnose/update strings in CLI + MCP code do not force package-name-only commands.
- `pyproject.toml` URL owner matches documented install source.

---

## Suggested Rollout Order

1. Phase A + B (source model + JSON generator)
2. Phase D (diagnostics/update messaging)
3. Phase C + E (docs + metadata consistency)
4. Phase F (bootstrap script + README entry)

This sequence reduces user-visible inconsistency quickly and makes docs reflect already-implemented behavior.

---

## Success Criteria

- Default setup/install instructions are repo-pinned.
- Generated MCP JSON can be repo-pinned without manual edits.
- Diagnostic/update hints are source-consistent.
- Users can complete onboarding from this repository via a single documented command path.
