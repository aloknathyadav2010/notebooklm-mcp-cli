from pathlib import Path

from notebooklm_tools.services.indexing_utility import (
    build_plan,
    delete_profile,
    get_profile,
    list_profiles,
    set_profile,
    update_profile_notebook,
)


def test_profile_persistence_and_update_notebook(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTEBOOKLM_MCP_CLI_PATH", str(tmp_path / "store"))

    profile = set_profile(
        "repo1",
        repo_root=str(tmp_path),
        include_patterns=["docs/*"],
        exclude_patterns=["docs/private/*"],
        notebook_id=None,
        notebook_title="Repo Notebook",
    )

    assert profile["notebook_id"] is None
    loaded = get_profile("repo1")
    assert loaded is not None

    updated = update_profile_notebook("repo1", "nb-1", "Notebook One")
    assert updated["notebook_id"] == "nb-1"
    assert updated["notebook_title"] == "Notebook One"

    profiles = list_profiles()
    assert "repo1" in profiles


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
