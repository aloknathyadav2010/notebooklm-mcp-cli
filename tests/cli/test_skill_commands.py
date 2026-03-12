from pathlib import Path

from typer.testing import CliRunner

from notebooklm_tools.cli.commands import skill as skill_cmd


runner = CliRunner()


def test_add_auto_detects_antigravity_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".agent").mkdir()

    result = runner.invoke(skill_cmd.app, ["add"])

    assert result.exit_code == 0
    skill_root = tmp_path / ".agent/skills/nlm-skill"
    assert (skill_root / "SKILL.md").exists()
    assert (skill_root / "references/command_reference.md").exists()


def test_add_defaults_to_antigravity_when_no_markers(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(skill_cmd.app, ["add"])

    assert result.exit_code == 0
    assert "Defaulting to" in result.stdout
    assert (tmp_path / ".agent/skills/nlm-skill/SKILL.md").exists()


def test_add_rejects_unknown_framework(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(skill_cmd.app, ["add", "unknown-framework"])

    assert result.exit_code == 1
    assert "Unknown framework" in result.stdout


def test_add_existing_skill_requires_force(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / ".agent/skills/nlm-skill"
    target.mkdir(parents=True)
    skill_file = target / "SKILL.md"
    skill_file.write_text("original")

    result = runner.invoke(skill_cmd.app, ["add", "antigravity"]) 

    assert result.exit_code == 0
    assert "already present" in result.stdout
    assert skill_file.read_text() == "original"


def test_add_force_overwrites_existing_skill(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / ".agent/skills/nlm-skill"
    target.mkdir(parents=True)
    skill_file = target / "SKILL.md"
    skill_file.write_text("original")

    result = runner.invoke(skill_cmd.app, ["add", "antigravity", "--force"])

    assert result.exit_code == 0
    assert "Added NLM skill" in result.stdout
    assert skill_file.read_text() != "original"


def test_inject_alias_maps_to_add(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".agent").mkdir()

    result = runner.invoke(skill_cmd.app, ["inject"])

    assert result.exit_code == 0
    assert (tmp_path / ".agent/skills/nlm-skill/SKILL.md").exists()


def test_diagnose_reports_missing_nlm(monkeypatch):
    monkeypatch.setattr(skill_cmd.shutil, "which", lambda _: None)

    result = runner.invoke(skill_cmd.app, ["diagnose"])

    assert result.exit_code == 0
    assert "not found in PATH" in result.stdout
    assert "uv tool install --force notebooklm-mcp-cli" in result.stdout


def test_diagnose_reports_nlm_found(monkeypatch):
    monkeypatch.setattr(skill_cmd.shutil, "which", lambda _: "/usr/local/bin/nlm")

    result = runner.invoke(skill_cmd.app, ["diagnose"])

    assert result.exit_code == 0
    assert "nlm found in PATH" in result.stdout
    assert "/usr/local/bin/nlm" in result.stdout


def test_legacy_commands_removed():
    command_names = {c.name for c in skill_cmd.app.registered_commands}
    assert "add" in command_names
    assert "diagnose" in command_names
    assert "link" not in command_names
    assert "integrity" not in command_names
