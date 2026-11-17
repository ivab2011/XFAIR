"""Check that the crosswalk's source references resolve to usable passages."""

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASSAGE_FIELDS = (
    "ai_duty_passages",
    "ai_duty_indirect_passages",
    "cyber_control_passages",
)
# Match passage IDs in prose without treating control IDs such as C-OV-1 as passages.
PASSAGE_ID = re.compile(r"\b(?:AIA|NIS2|CSF|RMF|OMN|CRA)-[A-Z0-9]+(?:[.-][A-Z0-9]+)*\b")


def load_passages(path: Path) -> dict:
    """Index the source records by their unique passage IDs."""
    passages = {}
    with path.open(encoding="utf-8") as source_file:
        for line_number, line in enumerate(source_file, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path.name}, line {line_number}: invalid JSON") from error
            identifier = record.get("passage_id") if isinstance(record, dict) else None
            if not isinstance(identifier, str) or not identifier.strip():
                raise ValueError(f"{path.name}, line {line_number}: missing passage_id")
            if identifier in passages:
                raise ValueError(f"{path.name}, line {line_number}: duplicate ID {identifier}")
            passages[identifier] = record
    return passages


def crosswalk_references(path: Path) -> tuple[int, dict[str, set[str]]]:
    """Collect IDs from source columns and references mentioned in prose."""
    references = defaultdict(set)
    row_count = 0
    with path.open(encoding="utf-8-sig", newline="") as crosswalk_file:
        reader = csv.DictReader(crosswalk_file)
        required_columns = {"link_id", *PASSAGE_FIELDS}
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(f"{path.name}: missing required crosswalk columns")
        for row_count, row in enumerate(reader, start=1):
            identifiers = {
                identifier.strip()
                for field in PASSAGE_FIELDS
                for identifier in (row[field] or "").split(";")
                if identifier.strip()
            }
            for field, value in row.items():
                if field not in PASSAGE_FIELDS and isinstance(value, str):
                    identifiers.update(PASSAGE_ID.findall(value))
            for identifier in identifiers:
                references[identifier].add(row["link_id"] or f"row {row_count}")
    return row_count, references


def main() -> int:
    try:
        passages = load_passages(ROOT / "sources" / "passages.jsonl")
        row_count, references = crosswalk_references(ROOT / "crosswalk" / "crosswalk.csv")
    except (OSError, ValueError, csv.Error) as error:
        print(f"Source check failed: {error}", file=sys.stderr)
        return 1

    problems = []
    for identifier, links in sorted(references.items()):
        record = passages.get(identifier)
        if record is None:
            reason = "missing from passages.jsonl"
        elif record.get("status") != "found":
            reason = f"status is {record.get('status')!r}"
        elif not isinstance(record.get("text"), str) or not record["text"].strip():
            reason = "text is empty or invalid"
        else:
            continue
        problems.append(f"- {identifier} ({', '.join(sorted(links))}): {reason}")

    print(f"Source records loaded: {len(passages)}")
    print(f"Crosswalk rows checked: {row_count}")
    print(f"Referenced passages verified: {len(references) - len(problems)}/{len(references)}")
    if problems:
        print("Missing or unusable passages:")
        print("\n".join(problems))
        return 1
    print("PASS: Every referenced passage is marked found and has non-empty text.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
