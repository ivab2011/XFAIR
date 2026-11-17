#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python=.venv/bin/python
run_id=$(TZ=America/New_York date '+%Y-%m-%dT%H-%M-%S%z')
run_dir="runs/$run_id"

cases=$("$python" - <<'PY'
import csv

with open("tests/cases.csv", encoding="utf-8", newline="") as source:
    for row in csv.DictReader(source):
        print(row["case_id"], row["action_id"], row["evidence_file"], sep="\t")
PY
)
mkdir "$run_dir"
printf 'Run %s\n' "$run_id"
while IFS=$'\t' read -r case_id action_id evidence; do
    case_dir="$run_dir/$case_id"
    mkdir "$case_dir"
    started=$SECONDS
    printf '%s running (%s)\n' "$case_id" "$action_id"
    "$python" -m components.check_evidence "$action_id" "$evidence" > "$case_dir/01_model_check.json"
    "$python" -m components.verify_quotes "$case_dir/01_model_check.json" "$evidence" > "$case_dir/02_verified_findings.json"
    "$python" -m components.decide "$case_dir/02_verified_findings.json" \
        --case-id "$case_id" --run-id "$run_id" > "$case_dir/03_decision.json"
    "$python" -m components.build_trace "$run_id" "$case_id" "$((SECONDS - started))"
    "$python" - "$case_id" "$case_dir/03_decision.json" <<'PY'
import json
import sys

with open(sys.argv[2], encoding="utf-8") as source:
    decision = json.load(source)
print(f"{sys.argv[1]} done — {decision['granted_level']} ({decision['status']})")
PY
done <<< "$cases"
