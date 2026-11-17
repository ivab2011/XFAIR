"""Compare one run with the case expectations and audit its kept quotes."""

import argparse
import csv
import json
from pathlib import Path

from components.verify_quotes import normalize

ROOT = Path(__file__).resolve().parents[1]


def cell(text: str) -> str:
    return " ".join(text.split()).replace("|", r"\|")


def evaluate(run_id: str) -> tuple[str, int]:
    rows = [
        f"# Results · {run_id}",
        "",
        "| Case | Expected level / status | Actual level / status | Result | OWASP tag | Failure reason |",
        "|---|---|---|---|---|---|",
    ]
    failures = 0
    case_count = 0
    checked_quotes = 0
    with (ROOT / "tests/cases.csv").open(encoding="utf-8", newline="") as file:
        cases = list(csv.DictReader(file))
    for case in cases:
        case_count += 1
        case_id = case["case_id"]
        folder = ROOT / "runs" / run_id / case_id
        decision = json.loads((folder / "03_decision.json").read_text(encoding="utf-8"))
        verified = json.loads((folder / "02_verified_findings.json").read_text(encoding="utf-8"))
        evidence_file = ROOT / case["evidence_file"]
        if any(
            result["action_id"] != case["action_id"] or result["evidence_file"] != evidence_file.name
            for result in (verified, decision)
        ):
            raise ValueError(f"{case_id}: saved outputs refer to a different action or evidence file.")

        expected = case["expected_level"], case["expected_status"]
        actual = decision["granted_level"], decision["status"]
        reasons = []
        if actual != expected:
            for level in decision["levels"]:
                if level["level"] in {expected[0], actual[0]} or not level["passed"]:
                    details = [item["reason"] for item in level["controls"] if not item["passed"]]
                    details.extend(rule["reason"] for rule in level["extra_rules"] if not rule["passed"])
                    reasons.append(" ".join([f"{level['level']} — {level['reason']}", *details]))
            if decision["conflicting_controls"]:
                reasons.append("Conflicting controls: " + ", ".join(decision["conflicting_controls"]) + ".")

        evidence = normalize(evidence_file.read_text(encoding="utf-8"))
        kept_quotes = [
            (finding["control_id"], quote)
            for finding in verified["findings"]
            for quote in finding["quotes"]
        ]
        kept_quotes.extend(("injection flag", flag["quote"]) for flag in verified["injection_flags"] if flag["verified"])
        for control_id, quote in kept_quotes:
            checked_quotes += 1
            normalized_quote = normalize(quote)
            if not normalized_quote or normalized_quote not in evidence:
                reasons.append(f"{control_id} quote absent from evidence: “{quote}”")

        passed = actual == expected and not reasons
        failures += int(not passed)
        row = (
            case_id, " / ".join(expected), " / ".join(actual),
            "PASS" if passed else "FAIL", case["owasp_agentic"] or "—",
            " ".join(reasons) or "—",
        )
        rows.append("| " + " | ".join(map(cell, row)) + " |")
    rows.extend(["", f"{case_count - failures}/{case_count} cases passed. Checked {checked_quotes} kept quotes and verified flags against the evidence files."])
    return "\n".join(rows) + "\n", failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    args = parser.parse_args()
    report, failures = evaluate(args.run_id)
    folder = ROOT / "reports" / args.run_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "results.md").write_text(report, encoding="utf-8")
    print(report, end="")
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(main())
