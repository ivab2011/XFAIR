# XFAIR

Research prototype for MIT 1.125. Not legal advice. The utility, agent and people in the use case are fictional.

XFAIR is an MIT 1.125 term project that checks how much independence an AI agent should have for a particular action. It reads an evidence pack, checks eight controls across four themes, and recommends one of three levels: suggest an action for a person to take, act with a person's approval, or act alone and report afterward. The report shows the evidence, the decision rules, and the official sources behind each control so a reviewer can follow the decision.

## At a glance

**How much autonomy does the evidence support for this agent’s proposed action?**

- Seven test cases, including prompt injections that try to raise and lower autonomy.
- All six cases in the stability study reached the same decisions across three runs.
- Promptfoo v2 passed 20/21 in each suite. Every failure was fail-safe, with no increase in autonomy.
- 32 passages from six official texts.

[One-page summary (PDF)](docs/XFAIR_onepager.pdf) · [Midpoint submission](SUBMISSION.md) · [Architecture](ARCHITECTURE.md) · [Midpoint video placeholder](SUBMISSION.md#midpoint-materials)

## Maria’s use case

Maria leads operations at Lakeside Water, a fictional drinking-water utility in Croatia. Its fictional agent, LeakGuard, watches for leaks. Maria wants to know when it can send leak alerts, adjust pump schedules, or close valves. A false alert can be dismissed. A mistaken valve closure can interrupt water service for many customers, even if the valve is later reopened. XFAIR checks what the evidence supports for each action.

## Install and run

Run these commands from the XFAIR folder. The recorded setup used Python 3.15.0. A virtual environment keeps XFAIR’s packages in the project’s `.venv` folder.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install openai==3.53.0 PyYAML==6.0.3
```

If `OPENAI_API_KEY` is already set in your terminal, use that terminal. Otherwise create a private file with `touch .env && chmod 600 .env`. In a local editor add `export OPENAI_API_KEY='YOUR_KEY_HERE'`, replacing the placeholder with your key. Save it and run `source .env`. Git ignores the file. Keep the key private.

Run a short model check, verify the local source references, then run the cases:

```sh
.venv/bin/python -m components.check_model
.venv/bin/python -m components.load_sources
./run.sh
```

`run.sh` prints a timestamp after the word `Run`. It saves the three steps for each case under `runs/` and writes the readable traces under `reports/`. To compare the decisions with the expected results, run the following and paste that timestamp when asked:

```sh
printf 'Paste the run ID and press Enter: '
read -r run_id
.venv/bin/python -m components.evaluate "$run_id"
```

The evaluator writes `reports/<run-id>/results.md`. To compare three runs from the same case list, enter their timestamps in order:

```sh
printf 'Paste three run IDs separated by spaces and press Enter: '
read -r first_run second_run third_run
.venv/bin/python -m components.stability "$first_run" "$second_run" "$third_run"
```

The stability command writes `reports/stability.md`. The [midpoint stability report](reports/stability.md) used the six-case list saved at commit `21f101a`. The current list also includes T7. Use three fresh runs for a seven-case comparison, or reproduce the six-case report in a temporary copy:

```sh
snapshot="$(mktemp -d)"
project_python="$PWD/.venv/bin/python"
git archive 21f101a | tar -x -C "$snapshot"
(
  cd "$snapshot" || exit 1
  "$project_python" -m components.stability \
    2026-11-17T17-59-25-0500 2026-11-17T18-08-22-0500 2026-11-17T18-08-43-0500
)
```

### Promptfoo

Promptfoo is a separate evaluation tool. The runner uses `npx` with pinned Promptfoo **0.125.1** and needs Node.js 22.22.0 or newer. It sets `PROMPTFOO_DISABLE_TELEMETRY=1` and makes fresh model calls. The following repeats each case three times and saves HTML and JSON under the new suffix `local`. Choose a different suffix for later runs if you want to keep these reports.

```sh
./evals/promptfoo/run.sh skill 3 local
./evals/promptfoo/run.sh pipeline 3 local
```

The skill suite checks the evidence checker’s raw findings, quotes, and injection flags. The pipeline suite checks the final decision after quote verification and application of the rules. Promptfoo can write reports even when a test fails.

## Design choices

- The model finds and quotes evidence, labels each control, and flags text that tries to instruct the reviewer. Plain Python decides the autonomy level.
- The verifier checks each quote word for word against the evidence, allowing whitespace differences only. Unsupported findings lose credit when too few quotes match.
- A human review can override a finding. The decision records the model and reviewer findings, who reviewed it, and why.
- `components/call_model.py` is the single place that contacts OpenAI. The model name comes from `config/settings.yaml`.
- The legal crosswalk uses approved rows. The trace keeps the official text, the project’s interpretation, and the case evidence visible.
- [Skill revisions](docs/skill_revisions.md) record what the model did, the review decision, and the resulting wording changes.

## Folder structure

Files generated for multiple cases or runs are listed by their filename pattern.

| File or pattern | What it does |
|---|---|
| `.gitignore` | Keeps local credentials, packages, and caches out of Git. |
| `README.md` | Introduces XFAIR and gives setup and run commands. |
| `ARCHITECTURE.md` | Shows how the steps fit together and follows one control through a decision. |
| `SUBMISSION.md` | Records the midpoint results and final plan. |
| `PROGRESS_handoff.md` | Gives the next work session a starting point. |
| `run.sh` | Runs every case and saves its outputs. |
| `components/README.md` | Introduces the Python components folder. |
| `components/build_trace.py` | Builds the readable Markdown and HTML traces. |
| `components/call_model.py` | Sends all model requests and records token counts. |
| `components/check_evidence.py` | Builds the evidence prompt and saves the raw model answer. |
| `components/check_model.py` | Checks the model connection with one short question. |
| `components/decide.py` | Applies approved reviews, charter limits, and decision rules. |
| `components/evaluate.py` | Compares a run with the expected results and rechecks kept quotes. |
| `components/load_sources.py` | Checks that the crosswalk’s passage IDs have saved text. |
| `components/run_case.py` | Runs one case for Promptfoo using the same Python steps. |
| `components/stability.py` | Compares decisions and raw findings across three runs. |
| `components/verify_quotes.py` | Checks quotes and injection flags against the evidence. |
| `config/README.md` | Introduces the project settings folder. |
| `config/charter.yaml` | Defines Maria’s scenario, the three actions, and the requested autonomy. |
| `config/controls.yaml` | Lists the eight controls for the evidence checker. |
| `config/labels.md` | Explains the legal-status labels used in the crosswalk. |
| `config/rules.yaml` | Defines which controls and restrictions apply to each level. |
| `config/settings.yaml` | Sets the OpenAI model name. |
| `config/themes.md` | Describes the four themes and eight controls in plain language. |
| `crosswalk/README.md` | Introduces the crosswalk folder. |
| `crosswalk/crosswalk.csv` | Maps controls to passages, interpretations, duty holders, and review status. |
| `docs/skill_revisions.md` | Records the review and reason for each skill revision. |
| `evals/README.md` | Introduces the evaluation folder. |
| `evals/promptfoo/cases.py` | Turns the case list into tests for both Promptfoo suites. |
| `evals/promptfoo/pipeline_eval.yaml` | Configures the full decision checks. |
| `evals/promptfoo/run.sh` | Runs the pinned Promptfoo version and saves its reports. |
| `evals/promptfoo/skill_assertions.js` | Checks control IDs, quotes, findings, and injection flags. |
| `evals/promptfoo/skill_eval.yaml` | Configures the evidence-check suite. |
| `evidence/README.md` | Introduces the fictional evidence folder. |
| `evidence/E1_alerts_complete.md` | Complete evidence for sending alerts. |
| `evidence/E2_pumps_partial.md` | Partial evidence for changing pump schedules. |
| `evidence/E3_valves_missing.md` | Missing controls for valve closure. |
| `evidence/E4_valves_complete.md` | Complete control evidence for valve closure. |
| `evidence/E5_valves_conflicting.md` | Conflicting account evidence for valve closure. |
| `evidence/E6_valves_injection.md` | A test of an instruction to raise autonomy. |
| `evidence/E7_alerts_injection_downgrade.md` | A test of an instruction to lower autonomy. |
| `overrides/README.md` | Introduces the human review folder. |
| `overrides/human_overrides.json` | Stores human reviews, including Iva’s T3 finding. |
| `prompts/README.md` | Marks the folder for reusable prompts. |
| `skills/evidence-check/README.md` | Introduces the evidence-check skill folder. |
| `skills/evidence-check/SKILL.md` | Gives the model its evidence-check instructions. |
| `sources/README.md` | Introduces the official source folder. |
| `sources/passage_list.csv` | Lists the requested provisions and their official URLs. |
| `sources/passages.jsonl` | Stores one record per extracted provision. |
| `sources/raw/ai-act-consolidated.html` | Saved consolidated EU AI Act. |
| `sources/raw/cyber-resilience-act.html` | Saved EU Cyber Resilience Act. |
| `sources/raw/digital-omnibus.html` | Saved Digital Omnibus on AI. |
| `sources/raw/nis2.html` | Saved NIS2 Directive. |
| `sources/raw/nist-ai-rmf-1.0.pdf` | Saved NIST AI Risk Management Framework. |
| `sources/raw/nist-csf-2.0.pdf` | Saved NIST Cybersecurity Framework. |
| `tests/README.md` | Introduces the tests folder. |
| `tests/cases.csv` | Stores each case, its expected level and status, and any OWASP tag. |
| `runs/README.md` | Introduces the saved run outputs. |
| `runs/<run-id>/[<case>/]01_model_check.json` | Raw model output and usage for a case. |
| `runs/<run-id>/[<case>/]02_verified_findings.json` | Findings after quotes and flags are checked. |
| `runs/<run-id>/[<case>/]03_decision.json` | Final level, status, and reasons. |
| `reports/README.md` | Introduces the reports folder. |
| `reports/<run-id>/<case>.md` | A case trace in Markdown. |
| `reports/<run-id>/<case>.html` | The same case trace formatted for a browser. |
| `reports/<run-id>/results.md` | The case results and independent quote check for a run. |
| `reports/stability.md` | The comparison across the three six-case runs. |
| `reports/promptfoo/skill_v1.html` | First skill evaluation, browser report. |
| `reports/promptfoo/skill_v1.json` | First skill evaluation, structured results. |
| `reports/promptfoo/pipeline_v1.html` | First pipeline evaluation, browser report. |
| `reports/promptfoo/pipeline_v1.json` | First pipeline evaluation, structured results. |
| `reports/promptfoo/skill_v2.html` | Repeated skill evaluation, browser report. |
| `reports/promptfoo/skill_v2.json` | Repeated skill evaluation, structured results. |
| `reports/promptfoo/pipeline_v2.html` | Repeated pipeline evaluation, browser report. |
| `reports/promptfoo/pipeline_v2.json` | Repeated pipeline evaluation, structured results. |

## Official sources

The repository contains 32 passages from six documents. These links come from [the passage list](sources/passage_list.csv).

- [EU AI Act, consolidated text as amended by Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng)
- [NIS2 Directive (EU) 2022/2555](https://eur-lex.europa.eu/eli/dir/2022/2555/oj)
- [EU Cyber Resilience Act, Regulation (EU) 2024/2847](https://eur-lex.europa.eu/eli/reg/2024/2847/oj)
- [Digital Omnibus on AI, Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj)
- [NIST Cybersecurity Framework 2.0](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf)
- [NIST AI Risk Management Framework 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)

## Limitations

- The project uses synthetic evidence only.
- One reviewer has assessed the crosswalk so far. A second independent review is planned.
- The crosswalk reflects the project’s interpretation of the official texts.
- The model’s findings can vary between runs. [Midpoint submission](SUBMISSION.md#technical-uncertainties-investigated)

## AI assistance

XFAIR’s code was written with Codex. The evidence checker uses `gpt-5.4-mini` at runtime. Claude helped prepare the content drafts for the themes, charter, rules, crosswalk, evidence, and tests. Iva Biscanic reviewed and approved the midpoint content. The approved crosswalk rows and the skill revision log record specific reviews.
