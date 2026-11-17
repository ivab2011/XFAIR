"""Check model quotes and injection flags against the original evidence."""

import argparse
import json
from pathlib import Path

FINDINGS = {"met", "missing", "conflicting"}


def normalize(text: str) -> str:
    return " ".join(text.split())


def verify_quotes(model_check: dict, evidence: str) -> dict:
    answer = json.loads(model_check["raw_answer"])
    normalized_evidence = normalize(evidence)
    verified_findings = []
    seen_controls = set()

    for finding in answer["findings"]:
        control_id = finding["control_id"]
        original = finding["finding"]
        if control_id in seen_controls or original not in FINDINGS:
            raise ValueError(f"Duplicate control or invalid finding for {control_id}")
        seen_controls.add(control_id)

        quotes = []
        rejected_quotes = []
        source_quotes = finding["quotes"]
        if not isinstance(source_quotes, list) or not all(isinstance(q, str) for q in source_quotes):
            raise ValueError(f"Expected a list of quote strings for {control_id}")

        distinct_quotes = set()
        for quote in source_quotes:
            normalized_quote = normalize(quote)
            if normalized_quote and normalized_quote in normalized_evidence:
                quotes.append(quote)
                distinct_quotes.add(normalized_quote)
            else:
                rejected_quotes.append({"status": "rejected_quote", "quote": quote})

        result = original
        verification_note = None
        required_quotes = {"met": 1, "conflicting": 2}.get(original, 0)
        if len(distinct_quotes) < required_quotes:
            result = "missing"
            verification_note = f"{original} requires at least {required_quotes} distinct verified quote(s)."
        verified_findings.append({
            "control_id": control_id,
            "model_finding": original,
            "finding": result,
            "quotes": quotes,
            "rejected_quotes": rejected_quotes,
            "model_reasoning": finding["reasoning"],
            "verification_note": verification_note,
        })

    if seen_controls != set(model_check["control_ids"]):
        raise ValueError("The model must return exactly one finding per configured control.")

    flags = answer["injection_flags"]
    if not isinstance(flags, list) or not all(isinstance(flag, str) for flag in flags):
        raise ValueError("Expected a list of injection flag strings.")
    injection_flags = []
    for flag in flags:
        normalized_flag = normalize(flag)
        injection_flags.append({
            "quote": flag,
            "verified": bool(normalized_flag and normalized_flag in normalized_evidence),
        })

    return {
        "action_id": model_check["action_id"],
        "evidence_file": model_check["evidence_file"],
        "findings": verified_findings,
        "injection_flags": injection_flags,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model_check", type=Path)
    parser.add_argument("evidence_file", type=Path)
    args = parser.parse_args()
    model_check = json.loads(args.model_check.read_text(encoding="utf-8"))
    if model_check["evidence_file"] != args.evidence_file.name:
        parser.error("Use the same evidence file that was sent to the model.")
    result = verify_quotes(model_check, args.evidence_file.read_text(encoding="utf-8"))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
