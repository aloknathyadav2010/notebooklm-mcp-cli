from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

NOTEBOOKLM_DEP_URL = "git+https://github.com/jacob-bd/notebooklm-mcp-cli.git"


@dataclass
class InstallReport:
    dependency_installed: bool
    copied_skills: list[Path]
    ide_targets_updated: list[Path]
    mcp_configs_updated: list[Path]


def _expand(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def _unique_paths(paths: Iterable[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(resolved)
    return unique


def _write_mcp_server_entry(config_path: Path, server_name: str, command: str, args: list[str]) -> Path:
    config_path.parent.mkdir(parents=True, exist_ok=True)

    data = {"mcpServers": {}}
    if config_path.exists():
        data = json.loads(config_path.read_text())
        data.setdefault("mcpServers", {})

    data["mcpServers"][server_name] = {"command": command, "args": args}
    config_path.write_text(json.dumps(data, indent=2) + "\n")
    return config_path


def install_notebooklm_dependency(skip: bool = False) -> bool:
    if skip:
        return False

    subprocess.run(
        ["python", "-m", "pip", "install", NOTEBOOKLM_DEP_URL],
        check=True,
    )
    return True


def discover_ide_skill_targets(custom_targets: Iterable[str] | None = None) -> list[Path]:
    default_targets = [
        "~/.codex/skills",
        "~/.cursor/skills",
        "~/.vscode/skills",
        "~/.antigravity/skills",
    ]

    if custom_targets:
        default_targets.extend(custom_targets)

    return _unique_paths(Path(raw).expanduser() for raw in default_targets)


def sync_skills(skills_dir: str | Path, targets: Iterable[Path], overwrite: bool = False) -> tuple[list[Path], list[Path]]:
    src = _expand(skills_dir)
    if not src.exists() or not src.is_dir():
        raise FileNotFoundError(f"skills directory not found: {src}")

    copied: list[Path] = []
    updated_targets: list[Path] = []

    for target in _unique_paths(targets):
        target.mkdir(parents=True, exist_ok=True)
        updated_targets.append(target)

        for skill in src.iterdir():
            if not skill.is_dir():
                continue

            destination = target / skill.name
            if destination.exists() and overwrite:
                shutil.rmtree(destination)
            if destination.exists() and not overwrite:
                continue

            shutil.copytree(skill, destination)
            copied.append(destination)

    return copied, updated_targets


def ensure_cursor_mcp_config(project_root: str | Path, server_name: str = "contextbridge") -> Path:
    root = _expand(project_root)
    config_path = root / ".cursor" / "mcp.json"
    return _write_mcp_server_entry(
        config_path=config_path,
        server_name=server_name,
        command="contextbridge-install",
        args=["--ensure-only"],
    )


def ensure_claude_desktop_mcp_config(server_name: str = "contextbridge") -> Path:
    candidates = [
        Path("~/.config/Claude/claude_desktop_config.json"),
        Path("~/Library/Application Support/Claude/claude_desktop_config.json"),
    ]
    config_path = _expand(candidates[0])

    for candidate in candidates:
        expanded = candidate.expanduser()
        if expanded.exists():
            config_path = expanded.resolve()
            break

    return _write_mcp_server_entry(
        config_path=config_path,
        server_name=server_name,
        command="contextbridge-install",
        args=["--ensure-only"],
    )


def ensure_antigravity_mcp_config(server_name: str = "contextbridge") -> Path:
    config_path = _expand("~/.config/antigravity/mcp.json")
    return _write_mcp_server_entry(
        config_path=config_path,
        server_name=server_name,
        command="contextbridge-install",
        args=["--ensure-only"],
    )


def run_installer(
    project_root: str | Path,
    skills_dir: str | Path,
    ide_targets: Iterable[str] | None = None,
    overwrite: bool = False,
    skip_dependency_install: bool = False,
    ensure_cursor: bool = True,
    ensure_claude: bool = True,
    ensure_antigravity: bool = True,
) -> InstallReport:
    dependency_done = install_notebooklm_dependency(skip=skip_dependency_install)
    targets = discover_ide_skill_targets(ide_targets)
    copied, updated_targets = sync_skills(skills_dir=skills_dir, targets=targets, overwrite=overwrite)

    mcp_configs_updated: list[Path] = []
    if ensure_cursor:
        mcp_configs_updated.append(ensure_cursor_mcp_config(project_root=project_root))
    if ensure_claude:
        mcp_configs_updated.append(ensure_claude_desktop_mcp_config())
    if ensure_antigravity:
        mcp_configs_updated.append(ensure_antigravity_mcp_config())

    return InstallReport(
        dependency_installed=dependency_done,
        copied_skills=copied,
        ide_targets_updated=updated_targets,
        mcp_configs_updated=mcp_configs_updated,
    )
