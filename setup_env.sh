#!/usr/bin/env bash
# setup_env.sh — one-shot FactorTail environment bootstrap
#
# This script:
#   1. (Optionally) creates a Python virtualenv in `./.venv`.
#   2. Upgrades pip and installs FactorTail in editable mode with the
#      `dev`, `docs`, `plot`, and `realdata` extras.
#   3. Installs pre-commit hooks.
#   4. Runs `factortail-fetch-data` to download every external dataset
#      (Fama-French daily panels) into `./data/raw/`. The fetch step is
#      tolerant of network failures so an offline install still
#      succeeds.
#
# Usage:
#     ./setup_env.sh                 # default: create .venv and install
#     ./setup_env.sh --no-venv       # install in the active env, no venv
#     ./setup_env.sh --no-fetch      # skip the data download step
#     ./setup_env.sh --python python3.12   # pick an interpreter
#
set -euo pipefail

PYTHON="${PYTHON:-python3}"
CREATE_VENV=1
FETCH=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-venv)  CREATE_VENV=0; shift ;;
    --no-fetch) FETCH=0; shift ;;
    --python)   PYTHON="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,18p' "$0"
      exit 0
      ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

cd "$(dirname "$0")"

if [[ "$CREATE_VENV" -eq 1 ]]; then
  if [[ ! -d .venv ]]; then
    echo "[setup_env] creating virtualenv with $PYTHON"
    "$PYTHON" -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "[setup_env] interpreter: $(command -v python)"
echo "[setup_env] upgrading pip"
python -m pip install --upgrade pip >/dev/null

echo "[setup_env] installing factortail with dev,docs,plot,realdata extras"
python -m pip install -e ".[dev,docs,plot,realdata]"

echo "[setup_env] installing pre-commit hooks"
pre-commit install >/dev/null 2>&1 || echo "  (pre-commit install failed; run manually if needed)"

if [[ "$FETCH" -eq 1 ]]; then
  echo "[setup_env] fetching external data (this can be skipped with --no-fetch)"
  if ! factortail-fetch-data --cache-dir data/raw; then
    echo "  data fetch failed (likely no network) — synthetic surrogates will be used"
  fi
fi

echo
echo "[setup_env] done."
echo "  - run \`source .venv/bin/activate\` to use this environment"
echo "  - run \`pytest\` to verify the install"
echo "  - run \`factortail list-experiments\` to see the manifest"
