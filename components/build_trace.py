"""Write a readable audit trail from the saved outputs of one case."""

import argparse
import json
import re
from html import escape
from pathlib import Path

from components.load_sources import load_passages

ROOT = Path(__file__).resolve().parents[1]
PASSAGE_COLUMNS = {
    "ai_duty_passages": "Direct AI duty",
    "ai_duty_indirect_passages": "Indirect AI duty",
    "cyber_control_passages": "Cyber control",
}


def build_trace(case: str, model: dict, verified: dict, decision: dict, passages: dict, seconds: int) -> str:
    lines = [
        f"# {case} · {decision['action_id']}",
        "",
        f"**Decision:** `{decision['granted_level']}` · `{decision['status']}`",
        f"**Requested level:** `{decision['wanted_autonomy']}`",
        f"**Evidence file:** `{verified['evidence_file']}`",
        "",
        "## Level checks",
        "",
    ]
    requirements = {}
    links_by_control = {}
    reviews = {entry["control_id"]: entry for entry in decision["human_overrides"]}
    for level in decision["levels"]:
        label = level["level"]
        outcome = "PASS" if level["passed"] else "FAIL"
        lines.append(f"- `{label}` — **{outcome}**. {level['reason']}")
        lines.append(f"  {level['policy_reason']}")
        for rule in level["extra_rules"]:
            result = "PASS" if rule["passed"] else "FAIL"
            lines.append(f"  - `{rule['rule_id']}` — **{result}**. {rule['reason']}")
        for control in level["controls"]:
            control_id = control["control_id"]
            result = "PASS" if control["passed"] else "FAIL"
            requirements.setdefault(control_id, []).append((label, result, control["reason"]))
            links_by_control[control_id] = control["crosswalk"]
    if decision["conflicting_controls"]:
        lines.append("- Conflicting controls: " + ", ".join(decision["conflicting_controls"]))

    for finding in verified["findings"]:
        control_id = finding["control_id"]
        review = reviews.get(control_id)
        lines.extend([
            "",
            f"## {control_id}",
            "",
            f"- Verified finding: `{finding['finding']}` (model: `{finding.get('model_finding', finding['finding'])}`)",
            f"- Model reasoning: {finding['model_reasoning']}",
        ])
        if finding["verification_note"]:
            lines.append(f"- Verification note: {finding['verification_note']}")
        lines.append("- Verified quotes:")
        lines.extend(f"  - “{quote}”" for quote in finding["quotes"])
        if not finding["quotes"]:
            lines.append("  - None.")
        lines.append("- Rejected quotes:")
        lines.extend(f"  - `{entry['status']}`: “{entry['quote']}”" for entry in finding["rejected_quotes"])
        if not finding["rejected_quotes"]:
            lines.append("  - None.")
        if review:
            review_status = "applied" if review["applied"] else "model finding changed, review not applied"
            lines.append(
                f"- Human review ({review_status}): {review['reviewer']} ({review['date']}) "
                f"recorded model `{review['model_finding']}` → reviewer `{review['reviewer_finding']}`. "
                f"{review['reason']}"
            )
        else:
            lines.append("- Human review: none.")
        for level, result, reason in requirements.get(control_id, []):
            lines.append(f"- Requirement for `{level}` — **{result}**. {reason}")
        for link in links_by_control.get(control_id, []):
            lines.extend([
                f"- Approved crosswalk link: `{link['link_id']}`",
                f"  - Duty holder: {link['duty_holder']}",
                f"  - EU: {link['eu_status']}. US: {link['us_status']}.",
                f"  - Interpretation: {link['interpretation']}",
            ])
            for column, label in PASSAGE_COLUMNS.items():
                for identifier in filter(None, (value.strip() for value in link[column].split(";"))):
                    passage = passages[identifier]
                    if passage["status"] != "found" or not passage["text"].strip():
                        raise ValueError(f"No official text for {identifier}")
                    lines.append(
                        f"  - {label} — [{identifier} · {passage['reference']}]({passage['official_url']})"
                        f"\n\n    > {passage['text']}\n"
                    )

    lines.extend(["", "## Run details", "", "- Injection flags:"])
    for entry in verified["injection_flags"]:
        label = "verified" if entry["verified"] else "unverified"
        lines.append(f"  - {label}: “{entry['quote']}”")
    if not verified["injection_flags"]:
        lines.append("  - None.")
    tokens = model["token_counts"]
    lines.extend([
        f"- Model: `{model['model']}`",
        f"- Tokens: {tokens['input']} input, {tokens['output']} output, {tokens['total']} total",
        f"- Elapsed time through decision: {seconds} seconds",
    ])
    return "\n".join(lines) + "\n"


def as_html(markdown: str, case: str) -> str:
    """Render headings and source links, escaping all text from the inputs."""
    html_lines = []
    for line in markdown.splitlines():
        if line.startswith(("# ", "## ")):
            marks, title = line.split(" ", 1)
            size = len(marks)
            html_lines.append(f"<h{size}>{escape(title)}</h{size}>")
        else:
            source_link = re.fullmatch(
                r"  - (Direct AI duty|Indirect AI duty|Cyber control) — \[([^\[\]]+)\]\((https://[^\s()]+)\)",
                line,
            )
            if source_link:
                category, label, url = source_link.groups()
                safe = f'  - {escape(category)} — <a href="{escape(url)}">{escape(label)}</a>'
            else:
                safe = escape(line)
            html_lines.append(f'<div class="line">{safe}</div>')
    body = "\n".join(html_lines)
    return (
        '<!doctype html>\n<html lang="en"><meta charset="utf-8">'
        f"<title>{escape(case)} evidence trace</title>"
        "<style>body{max-width:75ch;margin:2rem auto;padding:0 1rem;font:1rem/1.55 system-ui}"
        ".line{white-space:pre-wrap;min-height:.5rem;overflow-wrap:anywhere}h2{margin-top:2rem}</style>"
        f"<main>\n{body}\n</main></html>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("case")
    parser.add_argument("seconds", type=int)
    args = parser.parse_args()
    run = ROOT / "runs" / args.run_id / args.case
    model, verified, decision = (
        json.loads((run / name).read_text(encoding="utf-8"))
        for name in ("01_model_check.json", "02_verified_findings.json", "03_decision.json")
    )
    passages = load_passages(ROOT / "sources/passages.jsonl")
    trace = build_trace(args.case, model, verified, decision, passages, args.seconds)
    report = ROOT / "reports" / args.run_id
    report.mkdir(parents=True, exist_ok=True)
    (report / f"{args.case}.md").write_text(trace, encoding="utf-8")
    (report / f"{args.case}.html").write_text(as_html(trace, args.case), encoding="utf-8")


if __name__ == "__main__":
    main()
