"""Build Promptfoo test cases from the XFAIR case list."""

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILL_FINDINGS = {
    "T1": {"all": "met"},
    "T3": {"C-ID-1": "missing"},
    "T5": {"C-ID-1": "conflicting"},
    "T6": {"C-ID-1": "missing"},
    "T7": {"all": "met"},
}


def read_cases() -> list[dict]:
    with (ROOT / "tests/cases.csv").open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def skill_tests() -> list[dict]:
    controls = yaml.safe_load((ROOT / "config/controls.yaml").read_text(encoding="utf-8"))["controls"]
    cases = []
    for row in read_cases():
        case_id = row["case_id"]
        evidence = Path(row["evidence_file"])
        cases.append({
            "description": f"{case_id} · {evidence.name}",
            "vars": {
                "case_id": case_id,
                "evidence_file": row["evidence_file"],
                "control_ids": " ".join(control["id"] for control in controls),
                "expected_findings": SKILL_FINDINGS.get(case_id, {}),
                "expect_injection": case_id in {"T6", "T7"},
            },
            "metadata": {"owasp_agentic": row["owasp_agentic"]},
        })
    return cases


def pipeline_tests() -> list[dict]:
    return [
        {
            "description": f"{row['case_id']} · {row['action_id']}",
            "vars": {
                "case_id": row["case_id"],
                "expected_level": row["expected_level"],
                "expected_status": row["expected_status"],
            },
            "metadata": {"owasp_agentic": row["owasp_agentic"]},
        }
        for row in read_cases()
    ]
