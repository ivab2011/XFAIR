"""Ask the model to check one evidence pack against the configured controls."""

import argparse
import json
from pathlib import Path

import yaml
from openai import APIConnectionError, APIStatusError

from components.call_model import call_model

ROOT = Path(__file__).resolve().parents[1]


def check_evidence(action_id: str, evidence_path: Path) -> dict:
    instructions = (ROOT / "skills/evidence-check/SKILL.md").read_text(encoding="utf-8")
    controls = yaml.safe_load((ROOT / "config/controls.yaml").read_text(encoding="utf-8"))["controls"]
    request = {
        "action_id": action_id,
        "evidence_file": evidence_path.name,
        "controls": controls,
        "evidence": evidence_path.read_text(encoding="utf-8"),
    }
    model_input = "Return the evidence check as a JSON object only.\n\n" + json.dumps(request, ensure_ascii=False)
    answer = call_model(instructions, model_input, json_only=True)
    return {
        "action_id": action_id,
        "evidence_file": evidence_path.name,
        "control_ids": [control["id"] for control in controls],
        "model": answer.model,
        "token_counts": {
            "input": answer.input_tokens,
            "output": answer.output_tokens,
            "total": answer.total_tokens,
        },
        "raw_answer": answer.text,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action_id")
    parser.add_argument("evidence_file", type=Path)
    args = parser.parse_args()
    try:
        result = check_evidence(args.action_id, args.evidence_file)
    except APIStatusError as error:
        parser.exit(1, f"OpenAI request failed (HTTP {error.status_code}).\n")
    except APIConnectionError:
        parser.exit(1, "Could not connect to OpenAI.\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
