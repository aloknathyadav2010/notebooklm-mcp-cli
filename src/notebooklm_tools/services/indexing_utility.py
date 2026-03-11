"""Simple user-facing indexing utility (profiles + MCP server targets)."""

from __future__ import annotations

from fnmatch import fnmatch
import json
from pathlib import Path
from typing import Any

from notebooklm_tools.services.local_indexing import scan_local_files, select_files_for_upload
import os


DEFAULT_STORE = {
    "profiles": {},
    "servers": {
        "local": {
            "id": "local",
            "mode": "local",
            "endpoint": "stdio://notebooklm-mcp",
            "description": "Local MCP server on user machine",
        }
    },
}


def _get_storage_dir() -> Path:
    """Get storage directory without requiring full config dependencies."""
    base = Path(os.environ.get("NOTEBOOKLM_MCP_CLI_PATH", str(Path.home() / ".notebooklm-mcp-cli")))
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_store_path() -> Path:
    """Path for indexing utility state."""
    return _get_storage_dir() / "indexing_utility.json"


def load_store() -> dict[str, Any]:
    """Load utility store with defaults."""
    path = get_store_path()
    if not path.exists():
        return json.loads(json.dumps(DEFAULT_STORE))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return json.loads(json.dumps(DEFAULT_STORE))

    data.setdefault("profiles", {})
    data.setdefault("servers", {})
    if "local" not in data["servers"]:
        data["servers"]["local"] = DEFAULT_STORE["servers"]["local"]
    return data


def save_store(store: dict[str, Any]) -> Path:
    """Persist utility store."""
    path = get_store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")
    return path


def set_server(
    server_id: str,
    *,
    endpoint: str,
    mode: str = "local",
    description: str = "",
) -> dict[str, Any]:
    """Create/update an MCP server target profile."""
    store = load_store()
    store["servers"][server_id] = {
        "id": server_id,
        "mode": mode,
        "endpoint": endpoint,
        "description": description,
    }
    save_store(store)
    return store["servers"][server_id]


def set_profile(
    name: str,
    *,
    repo_root: str,
    include_patterns: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    notebook_id: str | None = None,
    notebook_title: str | None = None,
    mcp_server_id: str = "local",
) -> dict[str, Any]:
    """Create/update an indexing profile for normal users."""
    store = load_store()
    root = str(Path(repo_root).expanduser().resolve())
    profile = {
        "name": name,
        "repo_root": root,
        "include_patterns": include_patterns or [],
        "exclude_patterns": exclude_patterns or [],
        "notebook_id": notebook_id,
        "notebook_title": notebook_title,
        "mcp_server_id": mcp_server_id,
    }
    store["profiles"][name] = profile
    save_store(store)
    return profile


def get_profile(name: str) -> dict[str, Any] | None:
    """Get one profile by name."""
    return load_store().get("profiles", {}).get(name)


def delete_profile(name: str) -> bool:
    """Delete profile by name."""
    store = load_store()
    existed = name in store.get("profiles", {})
    if existed:
        store["profiles"].pop(name, None)
        save_store(store)
    return existed


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch(path, p) for p in patterns)


def build_plan(profile_name: str, max_files: int = 50) -> dict[str, Any]:
    """Build a dry-run indexing plan from stored profile file rules."""
    profile = get_profile(profile_name)
    if not profile:
        raise ValueError(f"Profile not found: {profile_name}")

    repo_root = profile["repo_root"]
    include_patterns = profile.get("include_patterns") or []
    exclude_patterns = profile.get("exclude_patterns") or []

    all_candidates = scan_local_files(repo_root)

    filtered = []
    for c in all_candidates:
        rel = str(Path(c.path).resolve().relative_to(Path(repo_root).resolve()))

        if include_patterns and not _matches_any(rel, include_patterns):
            continue
        if exclude_patterns and _matches_any(rel, exclude_patterns):
            continue
        filtered.append(c)

    selected, skipped = select_files_for_upload(filtered, max_files=max_files)

    return {
        "profile": profile,
        "candidate_count": len(filtered),
        "selected_count": len(selected),
        "skipped_count": len(skipped),
        "selected_files": [
            {"path": f.path, "size_bytes": f.size_bytes, "media_type": f.media_type}
            for f in selected
        ],
        "skipped_files": [
            {"path": f.path, "size_bytes": f.size_bytes, "media_type": f.media_type}
            for f in skipped
        ],
    }
