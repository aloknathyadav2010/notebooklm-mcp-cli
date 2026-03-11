from pathlib import Path

from notebooklm_tools.services.indexing_utility import (
    build_plan,
    delete_profile,
    get_profile,
    load_store,
    set_profile,
    set_server,
)


def test_profile_and_server_persistence(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTEBOOKLM_MCP_CLI_PATH", str(tmp_path / "store"))

    server = set_server("cloud-a", endpoint="https://mcp.example.com", mode="cloud", description="team")
    assert server["mode"] == "cloud"

    profile = set_profile(
        "repo1",
        repo_root=str(tmp_path),
        include_patterns=["docs/*"],
        exclude_patterns=["docs/private/*"],
        notebook_id="nb-1",
        notebook_title="Repo Notebook",
        mcp_server_id="cloud-a",
    )

    assert profile["mcp_server_id"] == "cloud-a"
    loaded = get_profile("repo1")
    assert loaded is not None
    assert loaded["notebook_id"] == "nb-1"

    store = load_store()
    assert "local" in store["servers"]
    assert "cloud-a" in store["servers"]


def test_build_plan_include_exclude(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTEBOOKLM_MCP_CLI_PATH", str(tmp_path / "store"))

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("a", encoding="utf-8")
    (tmp_path / "docs" / "b.pdf").write_bytes(b"pdf")
    (tmp_path / "docs" / "private").mkdir()
    (tmp_path / "docs" / "private" / "secret.md").write_text("secret", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("note", encoding="utf-8")

    set_profile(
        "repo2",
        repo_root=str(tmp_path),
        include_patterns=["docs/*", "docs/**/*.pdf"],
        exclude_patterns=["docs/private/*"],
        mcp_server_id="local",
    )

    plan = build_plan("repo2", max_files=10)
    selected_names = {Path(f["path"]).name for f in plan["selected_files"]}

    assert "a.md" in selected_names
    assert "b.pdf" in selected_names
    assert "secret.md" not in selected_names
    assert "notes.txt" not in selected_names


def test_delete_profile(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTEBOOKLM_MCP_CLI_PATH", str(tmp_path / "store"))
    set_profile("repo3", repo_root=str(tmp_path))
    assert delete_profile("repo3") is True
    assert delete_profile("repo3") is False
