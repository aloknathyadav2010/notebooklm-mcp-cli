"""Install-source constants and helpers for repo-pinned onboarding."""

from __future__ import annotations

DEFAULT_GIT_INSTALL_URL = "https://github.com/aloknathyadav2010/notebooklm-mcp-cli.git"
DEFAULT_GIT_REF = "newflow"


def git_spec(ref: str = DEFAULT_GIT_REF) -> str:
    """Return pip/uv install spec for the canonical git source."""
    return f"git+{DEFAULT_GIT_INSTALL_URL}@{ref}"


def uv_tool_install_command(force: bool = False, ref: str = DEFAULT_GIT_REF) -> str:
    """Return repo-pinned uv tool install command."""
    force_flag = " --force" if force else ""
    return f'uv tool install{force_flag} "{git_spec(ref)}"'


def uv_tool_uninstall_command() -> str:
    """Return command to uninstall the global tool."""
    return "uv tool uninstall notebooklm-mcp-cli"


def uv_tool_update_command(ref: str = DEFAULT_GIT_REF) -> str:
    """Return recommended update command for repo-pinned installs."""
    return uv_tool_install_command(force=True, ref=ref)


def uvx_repo_args(ref: str = DEFAULT_GIT_REF) -> list[str]:
    """Return uvx args for repo-pinned execution."""
    return ["--from", git_spec(ref), "notebooklm-mcp"]
