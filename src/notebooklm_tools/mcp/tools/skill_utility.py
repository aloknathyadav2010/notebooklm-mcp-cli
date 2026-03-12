"""Skill-first MCP utility tools for onboarding and daily workflow."""

from __future__ import annotations

import shutil
from typing import Any, Literal

from notebooklm_tools.install_source import uv_tool_install_command
from ._utils import get_client, get_query_timeout, logged_tool
from .indexing import notebook_index_local, notebook_reindex_local
from ...cli.commands import skill as skill_cli
from ...services import chat as chat_service
from ...services.indexing_utility import (
    get_profile,
    list_profiles,
    set_profile,
    update_profile_notebook,
)


@logged_tool()
def skill_profiles() -> dict[str, Any]:
    """List saved skill profiles and their linked notebook status."""
    profiles = list_profiles()
    return {
        "status": "success",
        "count": len(profiles),
        "profiles": profiles,
    }


@logged_tool()
def skill_bootstrap(
    profile: str = "project-files",
    repo: str = ".",
    max_files: int = 50,
    wait: bool = True,
) -> dict[str, Any]:
    """Bootstrap skill workflow: auth check + profile + index/reindex."""
    try:
        get_client()
    except Exception as e:
        return {
            "status": "error",
            "error": f"Login required. Run `nlm login` once, then retry. Details: {e}",
        }

    profile_data = get_profile(profile)
    if not profile_data:
        profile_data = set_profile(profile, repo_root=repo)

    notebook_id = profile_data.get("notebook_id")
    repo_root = profile_data.get("repo_root") or repo
    notebook_title = profile_data.get("notebook_title") or f"Local Index - {profile}"

    if notebook_id:
        result = notebook_reindex_local(
            notebook_id=notebook_id,
            root_dir=repo_root,
            max_files=max_files,
            wait=wait,
        )
    else:
        result = notebook_index_local(
            root_dir=repo_root,
            notebook_title=notebook_title,
            max_files=max_files,
            wait=wait,
        )

    if result.get("status") != "success":
        return {
            "status": "error",
            "error": result.get("error", "unknown error"),
            "profile": profile,
        }

    if not notebook_id:
        notebook = result.get("notebook", {})
        nb_id = notebook.get("id")
        nb_title = notebook.get("title")
        if nb_id:
            update_profile_notebook(profile, nb_id, nb_title)

    return {
        "status": "success",
        "profile": profile,
        "workflow": "bootstrap",
        "result": result,
    }


@logged_tool()
def skill_ask(
    profile: str,
    question: str,
    file: str | None = None,
) -> dict[str, Any]:
    """Ask NotebookLM using notebook linked to a skill profile."""
    profile_data = get_profile(profile)
    if not profile_data:
        return {"status": "error", "error": f"Profile not found: {profile}"}

    notebook_id = profile_data.get("notebook_id")
    if not notebook_id:
        return {
            "status": "error",
            "error": "No notebook linked to this profile. Run skill_bootstrap first.",
            "profile": profile,
        }

    try:
        client = get_client()
    except Exception as e:
        return {
            "status": "error",
            "error": f"Login required. Run `nlm login` once, then retry. Details: {e}",
        }

    query_text = f"Focus on file '{file}'. {question}" if file else question

    try:
        result = chat_service.query(
            client,
            notebook_id,
            query_text,
            timeout=get_query_timeout(),
        )
    except Exception as e:
        return {"status": "error", "error": str(e)}

    return {
        "status": "success",
        "profile": profile,
        "notebook_id": notebook_id,
        "question": question,
        "file": file,
        "answer": result.get("answer", ""),
        "raw": result,
    }


@logged_tool()
def skill_reindex(
    profile: str = "project-files",
    max_files: int = 50,
    wait: bool = True,
) -> dict[str, Any]:
    """Reindex notebook linked to a skill profile."""
    profile_data = get_profile(profile)
    if not profile_data:
        return {"status": "error", "error": f"Profile not found: {profile}"}

    notebook_id = profile_data.get("notebook_id")
    if not notebook_id:
        return {
            "status": "error",
            "error": "No notebook linked to this profile. Run skill_bootstrap first.",
            "profile": profile,
        }

    try:
        get_client()
    except Exception as e:
        return {
            "status": "error",
            "error": f"Login required. Run `nlm login` once, then retry. Details: {e}",
        }

    result = notebook_reindex_local(
        notebook_id=notebook_id,
        root_dir=profile_data.get("repo_root"),
        max_files=max_files,
        wait=wait,
    )
    if result.get("status") != "success":
        return {
            "status": "error",
            "error": result.get("error", "unknown error"),
            "profile": profile,
        }

    return {
        "status": "success",
        "profile": profile,
        "workflow": "reindex",
        "result": result,
    }


@logged_tool()
def skill_add_to_workspace(
    framework: str | None = None,
    level: Literal["project", "user"] = "project",
    force: bool = False,
) -> dict[str, Any]:
    """Copy bundled NLM skill files into a framework skill directory."""
    selected = framework or skill_cli._detect_framework()
    if not selected:
        selected = "antigravity"

    if selected not in skill_cli.TOOL_CONFIGS or selected == "other":
        valid = [k for k in skill_cli.TOOL_CONFIGS if k != "other"]
        return {
            "status": "error",
            "error": f"Unknown framework '{selected}'",
            "valid_frameworks": valid,
        }

    config = skill_cli.TOOL_CONFIGS[selected]
    install_path = skill_cli._resolve_install_path(selected, level, config)
    if not install_path:
        return {
            "status": "error",
            "error": f"Framework '{selected}' does not support level '{level}'",
        }

    skill_file = install_path / "SKILL.md"
    if skill_file.exists() and not force:
        return {
            "status": "success",
            "framework": selected,
            "level": level,
            "path": str(install_path.resolve()),
            "changed": False,
            "message": "Skill already present. Set force=true to overwrite.",
        }

    skill_cli.install_skill_md(install_path)
    return {
        "status": "success",
        "framework": selected,
        "level": level,
        "path": str(install_path.resolve()),
        "changed": True,
        "message": "Skill added to workspace.",
    }


@logged_tool()
def skill_diagnose_cli() -> dict[str, Any]:
    """Check whether `nlm` is discoverable in PATH."""
    nlm_path = shutil.which("nlm")
    if nlm_path:
        return {
            "status": "success",
            "found": True,
            "nlm_path": nlm_path,
            "message": "nlm is available in PATH.",
        }

    return {
        "status": "success",
        "found": False,
        "message": f"`nlm` not found in PATH. Install via `{uv_tool_install_command(force=True)}`.",
    }
