"""Check the model connection with one short question."""

import sys
from time import perf_counter

from openai import APIConnectionError, APIStatusError

from components.call_model import call_model


def main() -> int:
    start = perf_counter()
    try:
        answer = call_model("Answer with just the number.", "What is 2 + 2?")
    except APIStatusError as error:
        print(f"Model check failed (HTTP {error.status_code}).", file=sys.stderr)
        return 1
    except APIConnectionError:
        print("Model check failed: could not connect to OpenAI.", file=sys.stderr)
        return 1
    except RuntimeError as error:
        print(f"Model check failed: {error}", file=sys.stderr)
        return 1

    elapsed = perf_counter() - start
    if not answer.text.strip():
        print("Model check failed: OpenAI returned no answer text.", file=sys.stderr)
        return 1

    token_count = answer.total_tokens if answer.total_tokens is not None else "unavailable"
    print(f"Answer: {answer.text}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Total tokens: {token_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
