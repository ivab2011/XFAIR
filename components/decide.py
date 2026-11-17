"""Apply the charter and readiness rules to verified evidence findings."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CROSSWALK_FIELDS = (
    "link_id", "duty_holder", "eu_status", "us_status", "interpretation",
    "ai_duty_passages", "ai_duty_indirect_passages", "cyber_control_passages",
)
LIMITED_BLAST_RADII = {"none", "single_asset", "single_site"}
IRREVERSIBLE_CONDITION = "reversible == true or blast_radius in [none, single_asset, single_site]"


def approved_crosswalk(path: Path) -> dict:
    links = defaultdict(list)
    with path.open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            if row["approval"] == "approved":
                links[row["control_id"]].append({field: row[field] for field in CROSSWALK_FIELDS})
    return links


def evaluate_extra_rule(rule: dict, action: dict) -> dict:
    if rule["rule"] != "R-IRREVERSIBLE" or rule["condition"] != IRREVERSIBLE_CONDITION:
        raise ValueError(f"Unsupported extra rule or condition: {rule['rule']}")

    reversible = action["reversible"]
    blast_radius = action["blast_radius"]
    passed = reversible is True or blast_radius in LIMITED_BLAST_RADII
    return {
        "rule_id": rule["rule"],
        "passed": passed,
        "reason": (
            f"Charter: reversible={str(reversible).lower()}, blast_radius={blast_radius}. "
            + ("The action is reversible or limited in impact." if passed else rule["text"].strip())
        ),
    }


def apply_reviews(findings: dict, reviews: list, review_ids: set[str]) -> list:
    """Apply reviews for this case or run and keep an audit record."""
    matched_reviews = []
    reviewed_controls = set()
    for review in reviews:
        control_id = review["control_id"]
        if review["run_or_case"] not in review_ids or control_id not in findings:
            continue
        if control_id in reviewed_controls:
            raise ValueError(f"Multiple reviews match {control_id}")
        reviewed_controls.add(control_id)
        entry = findings[control_id]
        actual_model_finding = entry.get("model_finding", entry["finding"])
        applied = actual_model_finding == review["model_finding"]
        matched_reviews.append({
            **review,
            "actual_model_finding": actual_model_finding,
            "verified_finding": entry["finding"],
            "applied": applied,
        })
        if applied:
            reviewer_finding = review["reviewer_finding"]
            if reviewer_finding not in {"met", "missing", "conflicting"}:
                raise ValueError(f"Invalid reviewer finding for {control_id}")
            entry["finding"] = reviewer_finding
            entry["review_reason"] = review["reason"]
    return matched_reviews


def decide(
    verified: dict, rules: dict, charter: dict, links: dict, *,
    reviews: list = (), review_ids: set[str] = frozenset(),
) -> dict:
    action_id = verified["action_id"]
    actions = {action["id"]: action for action in charter["actions"]}
    if action_id not in actions:
        raise ValueError(f"Unknown action: {action_id}")
    action = actions[action_id]
    wanted = action["wanted_autonomy"]
    levels = charter["autonomy_levels"]
    policy = rules["decision"]
    default = policy["default_level"]
    findings = {entry["control_id"]: dict(entry) for entry in verified["findings"]}
    matched_reviews = apply_reviews(findings, reviews, review_ids)
    conflicts = sorted(control_id for control_id, entry in findings.items() if entry["finding"] == "conflicting")

    granted = default
    assessments = []
    for rank, level in enumerate(levels):
        requirements = rules["levels"].get(level, {}) if level == default else rules["levels"][level]
        controls = []
        for control_id in requirements.get("requires_met", []):
            entry = findings.get(control_id, {})
            finding = entry.get("finding", "missing")
            passed = finding == "met"
            reason = (
                entry.get("review_reason") or entry.get("verification_note") or entry.get("model_reasoning")
                or ("Verified finding is met." if passed else "No usable finding for this control.")
            )
            controls.append({
                "control_id": control_id,
                "finding": finding,
                "passed": passed,
                "reason": reason,
                "crosswalk": links.get(control_id, []),
            })

        extra_rules = [evaluate_extra_rule(rule, action) for rule in requirements.get("also_requires", [])]
        within_cap = not policy["cap_at_wanted_autonomy"] or rank <= levels.index(wanted)
        blockers = [item["control_id"] for item in controls if not item["passed"]]
        blockers.extend(item["rule_id"] for item in extra_rules if not item["passed"])
        if not within_cap:
            blockers.append("wanted_autonomy cap")
        if conflicts and level != default:
            blockers.append("conflicting evidence requires human review")

        assessments.append({
            "level": level,
            "passed": not blockers,
            "reason": "Blocked by " + ", ".join(blockers) + "." if blockers else "All requirements passed.",
            "policy_reason": requirements.get("reason", "Default level. A person takes the action.").strip(),
            "controls": controls,
            "extra_rules": extra_rules,
            "within_wanted_autonomy": within_cap,
        })
        if not blockers:
            granted = level

    status = "decided"
    if conflicts:
        status = policy["conflicting_evidence"]
        granted = default

    return {
        "action_id": action_id,
        "evidence_file": verified["evidence_file"],
        "wanted_autonomy": wanted,
        "granted_level": granted,
        "status": status,
        "conflicting_controls": conflicts,
        "human_overrides": matched_reviews,
        "levels": assessments,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("verified_findings", type=Path)
    parser.add_argument("--case-id")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    verified = json.loads(args.verified_findings.read_text(encoding="utf-8"))
    rules = yaml.safe_load((ROOT / "config/rules.yaml").read_text(encoding="utf-8"))
    charter = yaml.safe_load((ROOT / "config/charter.yaml").read_text(encoding="utf-8"))
    links = approved_crosswalk(ROOT / "crosswalk/crosswalk.csv")
    reviews = json.loads((ROOT / "overrides/human_overrides.json").read_text(encoding="utf-8"))
    review_ids = {identifier for identifier in (args.case_id, args.run_id) if identifier}
    result = decide(verified, rules, charter, links, reviews=reviews, review_ids=review_ids)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
