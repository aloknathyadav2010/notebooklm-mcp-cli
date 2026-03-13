import json
import tempfile
import unittest
from pathlib import Path

from contextbridge_bootstrap.installer import (
    _write_mcp_server_entry,
    discover_ide_skill_targets,
    sync_skills,
)


class InstallerTests(unittest.TestCase):
    def test_sync_skills_copies_skill_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "skills"
            src.mkdir()
            (src / "skill-one").mkdir()
            (src / "skill-one" / "SKILL.md").write_text("# skill")

            target = root / "target"
            copied, targets = sync_skills(src, [target])

            self.assertEqual(len(copied), 1)
            self.assertTrue((target / "skill-one" / "SKILL.md").exists())
            self.assertEqual(targets, [target.resolve()])

    def test_discover_targets_include_antigravity(self):
        targets = discover_ide_skill_targets()
        self.assertTrue(any(str(path).endswith(".codex/skills") for path in targets))
        self.assertTrue(any(str(path).endswith(".antigravity/skills") for path in targets))

    def test_write_mcp_server_entry_merges_existing_config(self):
        with tempfile.TemporaryDirectory() as td:
            config_path = Path(td) / "mcp.json"
            config_path.write_text(json.dumps({"mcpServers": {"existing": {"command": "echo", "args": []}}}))

            _write_mcp_server_entry(
                config_path=config_path,
                server_name="contextbridge",
                command="contextbridge-install",
                args=["--ensure-only"],
            )

            data = json.loads(config_path.read_text())
            self.assertIn("existing", data["mcpServers"])
            self.assertIn("contextbridge", data["mcpServers"])


if __name__ == "__main__":
    unittest.main()
