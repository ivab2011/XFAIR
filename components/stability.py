"""Compare the saved decisions, raw model findings, and costs of three runs."""

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}[+-]\d{4}")
ELAPSED = re.compile(r"^- Elapsed time through decision: (\d+) seconds$", re.MULTILINE)


def read_case(run_id: str, case: dict) -> dict:
    case_id = case["case_id"]
    folder = ROOT / "runs" / run_id / case_id
    model, verified, decision = (
        json.loads((folder / filename).read_text(encoding="utf-8"))
        for filename in ("01_model_check.json", "02_verified_findings.json", "03_decision.json")
    )
    expected_file = Path(case["evidence_file"]).name
    if any(
        result["action_id"] != case["action_id"] or result["evidence_file"] != expected_file
        for result in (model, verified, decision)
    ):
        raise ValueError(f"{run_id}/{case_id}: saved outputs do not match the test case")

    raw = json.loads(model["raw_answer"])
    raw_findings = {row["control_id"]: row["finding"] for row in raw["findings"]}
    if len(raw_findings) != len(raw["findings"]) or raw_findings.keys() != set(model["control_ids"]):
        raise ValueError(f"{run_id}/{case_id}: incomplete or duplicate raw findings")

    trace = (ROOT / "reports" / run_id / f"{case_id}.md").read_text(encoding="utf-8")
    footer = trace.rsplit("\n## Run details\n", 1)[-1]
    elapsed = ELAPSED.findall(footer)
    if len(elapsed) != 1:
        raise ValueError(f"{run_id}/{case_id}: missing or ambiguous elapsed time")
    return {
        "decision": f"{decision['granted_level']} / {decision['status']}",
        "findings": raw_findings,
        "rejected": sum(len(row["rejected_quotes"]) for row in verified["findings"]),
        "flags": bool(raw["injection_flags"]),
        "tokens": model["token_counts"]["total"],
        "seconds": int(elapsed[0]),
    }


def compare(run_ids: list[str]) -> str:
    if len(set(run_ids)) != 3 or not all(RUN_ID.fullmatch(run_id) for run_id in run_ids):
        raise ValueError("Supply three distinct, timestamped run IDs in comparison order.")
    with (ROOT / "tests/cases.csv").open(encoding="utf-8", newline="") as source:
        cases = list(csv.DictReader(source))

    lines = ["# Stability across three runs", ""]
    lines.extend(f"- Run {idx}: `{run_id}`" for idx, run_id in enumerate(run_ids, 1))
    lines += [
        "",
        "Run-by-run values are shown in the order above. Findings come from the raw model answer, before quote verification and review.",
        "",
        "| Case | Decision stable? | Decision (level / status) | Changed controls | Rejected quotes (1 / 2 / 3) |",
        "|---|---|---|---|---|",
    ]
    details = [
        "| Case | Control | Run 1 finding | Run 2 finding | Run 3 finding | Stable? |",
        "|---|---|---|---|---|---|",
    ]
    totals = [{"tokens": 0, "seconds": 0, "rejected": 0, "unknown_tokens": 0} for _ in run_ids]
    t6_flags = None
    for case in cases:
        case_id = case["case_id"]
        observations = [read_case(run_id, case) for run_id in run_ids]
        control_ids = observations[0]["findings"]
        if any(observation["findings"].keys() != control_ids.keys() for observation in observations):
            raise ValueError(f"{case_id}: runs checked different control IDs")

        decisions = [observation["decision"] for observation in observations]
        stable = len(set(decisions)) == 1
        decision_label = decisions[0] if stable else "; ".join(
            f"Run {idx}: {value}" for idx, value in enumerate(decisions, 1)
        )
        changed = []
        for control_id in sorted(control_ids):
            values = [observation["findings"][control_id] for observation in observations]
            unchanged = len(set(values)) == 1
            if not unchanged:
                changed.append(f"{control_id} ({' → '.join(values)})")
            detail_cells = [case_id, control_id, *values, "Yes" if unchanged else "No"]
            details.append("| " + " | ".join(detail_cells) + " |")

        rejected = " / ".join(str(observation["rejected"]) for observation in observations)
        lines.append(
            f"| {case_id} | {'Yes' if stable else 'No'} | {decision_label} | "
            f"{', '.join(changed) or '—'} | {rejected} |"
        )
        if case_id == "T6":
            t6_flags = ["Yes" if observation["flags"] else "No" for observation in observations]
        for total, observation in zip(totals, observations, strict=True):
            tokens = observation["tokens"]
            if tokens is None:
                total["unknown_tokens"] += 1
            else:
                total["tokens"] += tokens
            total["seconds"] += observation["seconds"]
            total["rejected"] += observation["rejected"]

    lines += ["", "## Raw findings by control", "", *details, "", "## T6 injection flags", ""]
    if t6_flags is None:
        raise ValueError("T6 is missing from the case list")
    lines.extend(f"- Run {idx}: {flag}" for idx, flag in enumerate(t6_flags, 1))
    lines += [
        "",
        "## Run totals",
        "",
        "Time is the sum of the six recorded case durations through the decision step, in whole seconds. It excludes report generation.",
        "",
        "| Run | Total tokens | Total time (s) | Rejected quotes |",
        "|---|---:|---:|---:|",
    ]
    for idx, total in enumerate(totals, 1):
        tokens = str(total["tokens"])
        if total["unknown_tokens"]:
            tokens += f" known ({total['unknown_tokens']} cases unavailable)"
        lines.append(f"| {idx} | {tokens} | {total['seconds']} | {total['rejected']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id", nargs=3, help="Three run IDs, in comparison order")
    args = parser.parse_args()
    try:
        report = compare(args.run_id)
        (ROOT / "reports/stability.md").write_text(report, encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Stability check failed: {error}\n")
    print(report, end="")


if __name__ == "__main__":
    main()
