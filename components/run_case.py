"""Run one XFAIR case for Promptfoo and write its result to standard output."""

import argparse
import csv
import json
from pathlib import Path

from openai import APIConnectionError, APIStatusError

from components.check_evidence import check_evidence
from components.decide import decide_from_config
from components.verify_quotes import verify_quotes

ROOT = Path(__file__).resolve().parents[1]


def run_case(case_id: str, *, skill_only: bool = False) -> str:
    with (ROOT / "tests/cases.csv").open(encoding="utf-8", newline="") as file:
        cases = {row["case_id"]: row for row in csv.DictReader(file)}
    if case_id not in cases:
        raise ValueError(f"Unknown case: {case_id}")
    case = cases[case_id]
    evidence_path = ROOT / case["evidence_file"]
    model_check = check_evidence(case["action_id"], evidence_path)
    if skill_only:
        return model_check["raw_answer"]

    evidence = evidence_path.read_text(encoding="utf-8")
    verified = verify_quotes(model_check, evidence)
    decision = decide_from_config(verified, case_id=case_id)
    return json.dumps(decision, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-only", action="store_true")
    parser.add_argument("case_id")
    parser.add_argument("provider_options", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("provider_context", nargs="?", help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        print(run_case(args.case_id, skill_only=args.skill_only))
    except APIStatusError as error:
        parser.exit(1, f"OpenAI request failed (HTTP {error.status_code}).\n")
    except APIConnectionError:
        parser.exit(1, "Could not connect to OpenAI.\n")
    except ValueError as error:
        parser.exit(1, f"Case failed: {error}\n")


if __name__ == "__main__":
    main()
