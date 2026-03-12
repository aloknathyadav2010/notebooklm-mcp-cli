#!/usr/bin/env bash
set -euo pipefail

REPO_SPEC="git+https://github.com/aloknathyadav2010/notebooklm-mcp-cli.git@newflow"
ACTION="${1:-install}"

have_cmd() { command -v "$1" >/dev/null 2>&1; }

if ! have_cmd uv; then
  echo "uv is required for seamless install/update/uninstall."
  echo "Install uv: https://docs.astral.sh/uv/getting-started/installation/"
  echo "Then rerun this script."
  exit 1
fi

case "$ACTION" in
  install|update)
    echo "Installing notebooklm-mcp-cli from this repository..."
    uv tool install --force "$REPO_SPEC"
    ;;
  uninstall|remove)
    echo "Uninstalling notebooklm-mcp-cli..."
    uv tool uninstall notebooklm-mcp-cli
    echo "✓ Uninstalled."
    exit 0
    ;;
  *)
    echo "Usage: ./install.sh [install|update|uninstall]"
    exit 1
    ;;
esac

echo
if have_cmd nlm; then
  echo "✓ nlm found: $(command -v nlm)"
else
  echo "! nlm not in PATH yet. You may need to restart your shell."
fi

if have_cmd notebooklm-mcp; then
  echo "✓ notebooklm-mcp found: $(command -v notebooklm-mcp)"
else
  echo "! notebooklm-mcp not in PATH yet. You may need to restart your shell."
fi

echo
echo "Next steps:"
echo "  nlm --version"
echo "  notebooklm-mcp --help"
echo "  nlm login"
