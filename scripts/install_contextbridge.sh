#!/usr/bin/env bash
set -euo pipefail

# ContextBridge Seamless Installer
# This script sets up ContextBridge, its virtual environment, and integrates it with your tools.

COLOR_BLUE="\033[0;34m"
COLOR_GREEN="\033[0;32m"
COLOR_RED="\033[0;31m"
COLOR_RESET="\033[0m"

function info() { echo -e "${COLOR_BLUE}[info]${COLOR_RESET} $1"; }
function success() { echo -e "${COLOR_GREEN}[success]${COLOR_RESET} $1"; }
function error() { echo -e "${COLOR_RED}[error]${COLOR_RESET} $1"; exit 1; }

# 1. Check Prerequisites
info "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 is required but not found. Please install Python 3.10 or higher."
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION < 3.10" | bc -l) -eq 1 ]]; then
    error "Python 3.10 or higher is required. Found version $PYTHON_VERSION"
fi

# 2. Determine Installation Directory
INSTALL_DIR="${INSTALL_DIR:-}"

if [[ -z "$INSTALL_DIR" ]]; then
    # If we are already in a git repo named getkodex or similar, or have the pyproject.toml, use current dir
    if [[ -f "pyproject.toml" ]] && grep -q "contextbridge-bootstrap" "pyproject.toml"; then
        INSTALL_DIR=$(pwd)
        info "Installing in current directory: $INSTALL_DIR"
    else
        INSTALL_DIR="$HOME/.contextbridge"
        info "Installing globally to: $INSTALL_DIR"
    fi
fi

# 3. Clone or Update Repository if needed
if [[ ! -d "$INSTALL_DIR/.git" ]]; then
    info "Cloning ContextBridge repository to $INSTALL_DIR..."
    git clone -b newflow https://github.com/aloknathyadav2010/getkodex.git "$INSTALL_DIR"
else
    if [[ "$(pwd)" != "$INSTALL_DIR" ]]; then
        info "Updating existing installation in $INSTALL_DIR..."
        cd "$INSTALL_DIR"
        git fetch origin newflow
        git checkout newflow
        git pull origin newflow
    fi
fi

cd "$INSTALL_DIR"

# 4. Create and Setup Virtual Environment
if [[ ! -d ".venv" ]]; then
    info "Creating virtual environment..."
    python3 -m venv .venv
fi

info "Installing dependencies..."
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e .

# 5. Run Configuration
info "Configuring MCP servers and syncing skills..."
# We use the absolute path to the installed script in the venv
./.venv/bin/contextbridge-install --project-root "$INSTALL_DIR" --skills-dir "$INSTALL_DIR/skills" "$@"

success "ContextBridge installation complete!"
info "Virtual environment is located at: $INSTALL_DIR/.venv"
info "You can now use ContextBridge in Claude Desktop, Cursor, and Claude Code."
