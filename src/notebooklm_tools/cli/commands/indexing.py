"""Simple indexing utility commands for non-power users."""

from __future__ import annotations

import json

import typer
from rich.console import Console

from notebooklm_tools.mcp.tools.indexing import notebook_index_local, notebook_reindex_local
from notebooklm_tools.services.indexing_utility import (
    build_plan,
    delete_profile,
    get_profile,
    list_profiles,
    set_profile,
    update_profile_notebook,
)


console = Console()
app = typer.Typer(
    help="Simple indexing utility: manage profile and run zero-setup index/reindex",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


def _require_auth() -> None:
    """Ensure user is logged in before indexing."""
    from notebooklm_tools.mcp.tools._utils import get_client

    try:
        # This validates auth by constructing client from cache/env.
        get_client()
    except Exception:
        console.print(
            "[yellow]Login required.[/yellow] Please run [bold]nlm login[/bold] once, then retry."
        )
        raise typer.Exit(1)


@app.command("set")
def indexing_set(
    name: str = typer.Argument(..., help="Profile name (e.g. my-project)"),
    repo: str = typer.Option(".", "--repo", help="Repository/root directory to scan"),
    include: list[str] | None = typer.Option(None, "--include", help="Include glob (repeatable)"),
    exclude: list[str] | None = typer.Option(None, "--exclude", help="Exclude glob (repeatable)"),
    notebook_id: str | None = typer.Option(None, "--notebook-id", help="NotebookLM notebook ID (optional)"),
    notebook_title: str | None = typer.Option(None, "--notebook-title", help="Notebook title label"),
) -> None:
    """Create/update an indexing profile."""
    profile = set_profile(
        name,
        repo_root=repo,
        include_patterns=include,
        exclude_patterns=exclude,
        notebook_id=notebook_id,
        notebook_title=notebook_title,
    )

    console.print(f"[green]✓[/green] Saved indexing profile: [bold]{name}[/bold]")
    console.print_json(json.dumps(profile))


@app.command("show")
def indexing_show(
    name: str = typer.Argument(..., help="Profile name"),
) -> None:
    """Show one indexing profile."""
    profile = get_profile(name)
    if not profile:
        console.print(f"[red]Profile not found:[/red] {name}")
        raise typer.Exit(1)
    console.print_json(json.dumps(profile))


@app.command("list")
def indexing_list() -> None:
    """List available indexing profiles."""
    profiles = list_profiles()
    if not profiles:
        console.print("No indexing profiles yet. Use [bold]nlm indexing set[/bold].")
        return

    for name, profile in profiles.items():
        nb = profile.get("notebook_id") or "(not indexed yet)"
        console.print(f"- [bold]{name}[/bold] -> {profile.get('repo_root')} notebook={nb}")


@app.command("delete")
def indexing_delete(
    name: str = typer.Argument(..., help="Profile name"),
) -> None:
    """Delete an indexing profile."""
    if not delete_profile(name):
        console.print(f"[red]Profile not found:[/red] {name}")
        raise typer.Exit(1)
    console.print(f"[green]✓[/green] Deleted profile: {name}")


@app.command("plan")
def indexing_plan(
    name: str = typer.Argument(..., help="Profile name"),
    max_files: int = typer.Option(50, "--max-files", help="NotebookLM upload cap to plan with"),
) -> None:
    """Dry-run: preview files that would be selected/skipped."""
    try:
        result = build_plan(name, max_files=max_files)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    console.print_json(json.dumps(result))


@app.command("run")
def indexing_run(
    name: str = typer.Argument(..., help="Profile name"),
    max_files: int = typer.Option(50, "--max-files", help="NotebookLM upload cap"),
    wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for source processing"),
) -> None:
    """Run indexing seamlessly: create notebook first time, reindex on subsequent runs."""
    profile = get_profile(name)
    if not profile:
        console.print(f"[red]Profile not found:[/red] {name}")
        raise typer.Exit(1)

    _require_auth()

    root_dir = profile["repo_root"]
    notebook_id = profile.get("notebook_id")
    notebook_title = profile.get("notebook_title") or f"Local Index - {name}"

    if notebook_id:
        result = notebook_reindex_local(
            notebook_id=notebook_id,
            root_dir=root_dir,
            max_files=max_files,
            wait=wait,
        )
    else:
        result = notebook_index_local(
            root_dir=root_dir,
            notebook_title=notebook_title,
            max_files=max_files,
            wait=wait,
        )

    if result.get("status") != "success":
        console.print(f"[red]Indexing failed:[/red] {result.get('error', 'unknown error')}")
        raise typer.Exit(1)

    if not notebook_id:
        notebook = result.get("notebook", {})
        nb_id = notebook.get("id")
        nb_title = notebook.get("title")
        if nb_id:
            update_profile_notebook(name, nb_id, nb_title)

    console.print("[green]✓[/green] Indexing completed")
    console.print_json(json.dumps(result))
