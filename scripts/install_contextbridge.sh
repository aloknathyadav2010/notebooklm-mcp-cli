#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
SKILLS_DIR="${SKILLS_DIR:-${PROJECT_ROOT}/skills}"

if [[ ! -d "${SKILLS_DIR}" ]]; then
  echo "skills directory not found at ${SKILLS_DIR}."
  echo "Create skills/ (or set SKILLS_DIR) before running installer."
  exit 1
fi

python -m pip install -e "${PROJECT_ROOT}"
contextbridge-install \
  --project-root "${PROJECT_ROOT}" \
  --skills-dir "${SKILLS_DIR}" \
  "$@"
