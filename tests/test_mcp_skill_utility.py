from notebooklm_tools.mcp.tools import skill_utility


def test_skill_profiles_returns_success(monkeypatch):
    monkeypatch.setattr(skill_utility, "list_profiles", lambda: {"project-files": {"name": "project-files"}})

    result = skill_utility.skill_profiles()

    assert result["status"] == "success"
    assert result["count"] == 1
    assert "project-files" in result["profiles"]


def test_skill_bootstrap_creates_profile_and_links_notebook(monkeypatch):
    monkeypatch.setattr(skill_utility, "get_client", lambda: object())
    monkeypatch.setattr(skill_utility, "get_profile", lambda _: None)
    monkeypatch.setattr(
        skill_utility,
        "set_profile",
        lambda profile, repo_root: {
            "name": profile,
            "repo_root": repo_root,
            "notebook_id": None,
            "notebook_title": None,
        },
    )

    updates = []
    monkeypatch.setattr(
        skill_utility,
        "update_profile_notebook",
        lambda profile, notebook_id, notebook_title: updates.append((profile, notebook_id, notebook_title)),
    )
    monkeypatch.setattr(
        skill_utility,
        "notebook_index_local",
        lambda **_: {"status": "success", "notebook": {"id": "nb-1", "title": "NB 1"}},
    )

    result = skill_utility.skill_bootstrap(profile="project-files", repo=".")

    assert result["status"] == "success"
    assert result["workflow"] == "bootstrap"
    assert updates == [("project-files", "nb-1", "NB 1")]


def test_skill_ask_profile_missing():
    result = skill_utility.skill_ask(profile="missing", question="hello")
    assert result["status"] == "error"
    assert "Profile not found" in result["error"]


def test_skill_diagnose_cli_not_found(monkeypatch):
    monkeypatch.setattr(skill_utility.shutil, "which", lambda _: None)

    result = skill_utility.skill_diagnose_cli()

    assert result["status"] == "success"
    assert result["found"] is False
