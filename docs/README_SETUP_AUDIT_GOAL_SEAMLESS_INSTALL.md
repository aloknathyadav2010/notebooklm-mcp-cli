# Setup Audit + Goal: Seamless One-Command, Repo-Pinned Installation

## Goal (What we are optimizing for)

Deliver a **single terminal command** setup flow that:
1. Installs from **this repository/branch** (not an unrelated package source).
2. Works for first-time users with minimal prerequisites.
3. Produces deterministic CLI/MCP behavior across environments.

---

## Findings from Setup Audit

### 1) Default install path can pull non-fork source
Current docs and helper text often use package-name installs (`uv tool install notebooklm-mcp-cli`), which may resolve to a release that does not match this repo branch/fork.

**Impact:** users can install a different build than expected.

### 2) MCP JSON generator defaults are not repo-pinned
The JSON setup flow currently emits `uvx --from notebooklm-mcp-cli notebooklm-mcp` in uvx mode.

**Impact:** runtime source is package-name based, not explicitly tied to this repository.

### 3) Metadata and update hints can point to upstream assumptions
Project URLs and some user-facing update/install recommendations are aligned to generic package flows.

**Impact:** confusion about where updates come from and how to stay on the intended code line.

### 4) Missing canonical bootstrap script
There is no single checked-in bootstrap script enforcing a repo-pinned install path.

**Impact:** onboarding requires interpretation and can drift across machines.

---

## Recommended Direction

### Canonical install command (repo/branch pinned)
Use a git URL install as primary guidance:

```bash
uv tool install --force "git+https://github.com/aloknathyadav2010/notebooklm-mcp-cli.git@newflow"
```

### One-command onboarding
Publish a root `install.sh` and support a single curl command:

```bash
curl -fsSL https://raw.githubusercontent.com/aloknathyadav2010/notebooklm-mcp-cli/newflow/install.sh | bash
```

The script should:
- install `uv` if missing,
- run repo-pinned install,
- verify `nlm` and `notebooklm-mcp`,
- print PATH remediation guidance.

---

## Practical Work Plan

### Phase 1: Docs & Messaging
- Make repo-pinned install the primary recommendation.
- Keep package-name install as an explicitly labeled alternative channel.
- Add prominent “why this command” note: guarantees source from this repo.

### Phase 2: Setup Tooling
- Extend `nlm setup add json` to support source selection:
  - repo-pinned git source (recommended),
  - package-name source (compatibility).

### Phase 3: Consistency Pass
- Align project URLs and user-facing update/remediation text.
- Ensure doctor/diagnose guidance includes repo-pinned commands.

### Phase 4: Validation
- Validate in clean shell scenarios (with/without uv, prior install present).
- Confirm generated MCP JSON points to selected source strategy.

---

## Success Criteria

- New users can install in **one command**.
- Installed binaries (`nlm`, `notebooklm-mcp`) are sourced from this repository/branch by default.
- Setup guidance is consistent across README, MCP docs, and CLI diagnostics.
