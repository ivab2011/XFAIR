#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
case "${1:-}" in
    skill|pipeline) suite=$1 ;;
    *) printf 'Usage: %s skill|pipeline\n' "$0" >&2; exit 2 ;;
esac

export PROMPTFOO_DISABLE_TELEMETRY=1
export PROMPTFOO_DISABLE_UPDATE=1
export PROMPTFOO_PYTHON="$PWD/.venv/bin/python"
export PATH="$PWD/.venv/bin:$PATH"
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p reports/promptfoo

npx --yes promptfoo@0.125.1 eval --config "evals/promptfoo/${suite}_eval.yaml" \
    --no-cache --max-concurrency 1 \
    --output "reports/promptfoo/${suite}.html" --output "reports/promptfoo/${suite}.json"
