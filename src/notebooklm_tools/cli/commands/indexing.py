"""Simple indexing utility commands for non-power users."""

from __future__ import annotations

import json

import typer
from rich.console import Console

from notebooklm_tools.services.indexing_utility import (
    build_plan,
    delete_profile,
    get_profile,
    load_store,
    set_profile,
    set_server,
)


console = Console()
app = typer.Typer(
    help="Simple indexing utility: manage repo/file rules and notebook mapping",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

server_app = typer.Typer(
    help="Manage MCP server targets (local today, cloud-ready profile for future)",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@app.command("set")
def indexing_set(
    name: str = typer.Argument(..., help="Profile name (e.g. work-docs)"),
    repo: str = typer.Option(".", "--repo", help="Repository/root directory to scan"),
    include: list[str] | None = typer.Option(None, "--include", help="Include glob (repeatable)"),
    exclude: list[str] | None = typer.Option(None, "--exclude", help="Exclude glob (repeatable)"),
    notebook_id: str | None = typer.Option(None, "--notebook-id", help="NotebookLM notebook ID"),
    notebook_title: str | None = typer.Option(None, "--notebook-title", help="Notebook title label"),
    mcp_server: str = typer.Option("local", "--mcp-server", help="MCP server target id"),
) -> None:
    """Create or update a user-friendly indexing profile."""
    profile = set_profile(
        name,
        repo_root=repo,
        include_patterns=include,
        exclude_patterns=exclude,
        notebook_id=notebook_id,
        notebook_title=notebook_title,
        mcp_server_id=mcp_server,
    )

    console.print(f"[green]✓[/green] Saved indexing profile: [bold]{name}[/bold]")
    console.print(json.dumps(profile, indent=2))


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
    store = load_store()
    profiles = store.get("profiles", {})
    if not profiles:
        console.print("No indexing profiles yet. Use [bold]nlm indexing set[/bold].")
        return

    for name, profile in profiles.items():
        console.print(f"- [bold]{name}[/bold] -> {profile.get('repo_root')} (mcp={profile.get('mcp_server_id')})")


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


@server_app.command("set")
def server_set(
    server_id: str = typer.Argument(..., help="Server id (e.g. local, cloud-team-a)"),
    endpoint: str = typer.Option(..., "--endpoint", help="Endpoint URI or transport hint"),
    mode: str = typer.Option("local", "--mode", help="local|cloud"),
    description: str = typer.Option("", "--description", help="Friendly note"),
) -> None:
    """Create/update MCP server target profile."""
    server = set_server(server_id, endpoint=endpoint, mode=mode, description=description)
    console.print(f"[green]✓[/green] Saved server target: [bold]{server_id}[/bold]")
    console.print_json(json.dumps(server))


@server_app.command("list")
def server_list() -> None:
    """List MCP server targets."""
    store = load_store()
    servers = store.get("servers", {})
    for sid, server in servers.items():
        console.print(f"- [bold]{sid}[/bold] ({server.get('mode')}): {server.get('endpoint')}")


app.add_typer(server_app, name="server")
