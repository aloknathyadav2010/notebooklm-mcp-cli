from __future__ import annotations

import argparse
from pathlib import Path

from .installer import run_installer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install notebooklm-mcp-cli dependency and sync skills into IDE directories."
    )
    parser.add_argument("--project-root", default=".", help="Root directory of your ContextBridge project")
    parser.add_argument("--skills-dir", default="skills", help="Directory containing skill folders")
    parser.add_argument(
        "--ide-target",
        action="append",
        default=[],
        help="Additional IDE skill target directory. Repeatable.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing skills in targets")
    parser.add_argument(
        "--skip-dependency-install",
        action="store_true",
        help="Skip pip install for notebooklm-mcp-cli dependency",
    )
    parser.add_argument("--skip-cursor-config", action="store_true", help="Do not write Cursor MCP config")
    parser.add_argument("--skip-claude-config", action="store_true", help="Do not write Claude Desktop MCP config")
    parser.add_argument("--skip-antigravity-config", action="store_true", help="Do not write Antigravity MCP config")
    parser.add_argument(
        "--ensure-only",
        action="store_true",
        help="Only ensure config references are valid, skip dependency install and skill sync",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.ensure_only:
        print("Configuration ensure-only mode: no dependency or skill sync executed.")
        return

    report = run_installer(
        project_root=Path(args.project_root),
        skills_dir=Path(args.skills_dir),
        ide_targets=args.ide_target,
        overwrite=args.overwrite,
        skip_dependency_install=args.skip_dependency_install,
        ensure_cursor=not args.skip_cursor_config,
        ensure_claude=not args.skip_claude_config,
        ensure_antigravity=not args.skip_antigravity_config,
    )

    print("ContextBridge bootstrap complete")
    print(f"- Dependency installed: {report.dependency_installed}")
    print(f"- Skills copied: {len(report.copied_skills)}")
    for copied in report.copied_skills:
        print(f"  - {copied}")
    print("- Updated IDE targets:")
    for target in report.ide_targets_updated:
        print(f"  - {target}")
    print("- Updated MCP configs:")
    for config_path in report.mcp_configs_updated:
        print(f"  - {config_path}")


if __name__ == "__main__":
    main()
