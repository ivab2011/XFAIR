"""Keep all language model calls in this module."""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from openai import OpenAI

SETTINGS_PATH = Path(__file__).resolve().parents[1] / "config" / "settings.yaml"


@dataclass(frozen=True)
class ModelAnswer:
    text: str
    total_tokens: int | None


def call_model(instructions: str, text: str) -> ModelAnswer:
    """Send instructions and text to the configured model."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. See README.md for setup.")

    with SETTINGS_PATH.open(encoding="utf-8") as settings_file:
        model = yaml.safe_load(settings_file)["model"]

    with OpenAI(
        api_key=api_key,
        base_url="https://api.openai.com/v1",
        timeout=30.0,
        max_retries=0,
    ) as client:
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=text,
        )

    return ModelAnswer(
        text=response.output_text,
        total_tokens=response.usage.total_tokens if response.usage else None,
    )
