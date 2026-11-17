# XFAIR

MIT 1.125 term project. Project scope and workflow will be added here.

## Local setup

This workspace uses Python 3.15.0. The installed packages are
`openai==3.53.0` and `PyYAML==6.0.3`.

To recreate the environment from the project folder, run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install openai==3.53.0 PyYAML==6.0.3
```

The model check reads `OPENAI_API_KEY` from your environment. If you need to
set it up later, create a private file with `touch .env && chmod 600 .env`.
Open it in a local editor and add `export OPENAI_API_KEY='YOUR_KEY_HERE'`,
replacing the placeholder with your key. Save the file and run `source .env`
in the same terminal before running the check. Git ignores `.env`. Keep
the key out of chat, screenshots, terminal commands, and commits.

Run the model check from the project folder:

```sh
.venv/bin/python -m components.check_model
```

## Promptfoo evaluations

The evaluation runner uses **Promptfoo 0.125.1** through `npx`. It requires
Node.js 22.22.0 or newer, the Python environment above, and an exported
`OPENAI_API_KEY`. From the project folder, run:

```sh
./evals/promptfoo/run.sh skill
./evals/promptfoo/run.sh pipeline
```

The runner sets `PROMPTFOO_DISABLE_TELEMETRY=1`, disables the response cache
for fresh model calls, and writes HTML and JSON to `reports/promptfoo/`.
`npx` fetches the pinned version as needed.

The skill evaluation checks the model's raw evidence findings, quotes, and
injection flags. It uses the same prompt builder and model setting as XFAIR.
The pipeline evaluation also verifies quotes and applies the decision rules.
Both suites use `tests/cases.csv`. Case T7 checks whether a downgrade instruction
in the evidence can push a well-supported decision down.
