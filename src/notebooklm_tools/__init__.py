"""NotebookLM Tools - Unified CLI and MCP server for Google NotebookLM."""

from typing import TYPE_CHECKING

__version__ = "0.4.5"

if TYPE_CHECKING:
    from notebooklm_tools.core.client import NotebookLMClient


__all__ = ["NotebookLMClient", "__version__"]


def __getattr__(name: str):
    """Lazily import heavy modules on first access."""
    if name == "NotebookLMClient":
        from notebooklm_tools.core.client import NotebookLMClient

        return NotebookLMClient
    raise AttributeError(name)
