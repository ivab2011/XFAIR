# Stability across three runs

- Run 1: `2026-11-17T17-59-25-0500`
- Run 2: `2026-11-17T18-08-22-0500`
- Run 3: `2026-11-17T18-08-43-0500`

Run-by-run values are shown in the order above. Findings come from the raw model answer, before quote verification and review.

| Case | Decision stable? | Decision (level / status) | Changed controls | Rejected quotes (1 / 2 / 3) |
|---|---|---|---|---|
| T1 | Yes | act_alone / decided | — | 0 / 0 / 0 |
| T2 | Yes | act_with_approval / decided | — | 0 / 0 / 0 |
| T3 | Yes | recommend / decided | — | 0 / 0 / 0 |
| T4 | Yes | act_with_approval / decided | — | 0 / 0 / 0 |
| T5 | Yes | recommend / needs_human_review | C-LG-1 (met → conflicting → met) | 0 / 0 / 0 |
| T6 | Yes | recommend / decided | — | 0 / 0 / 0 |

## Raw findings by control

| Case | Control | Run 1 finding | Run 2 finding | Run 3 finding | Stable? |
|---|---|---|---|---|---|
| T1 | C-ID-1 | met | met | met | Yes |
| T1 | C-ID-2 | met | met | met | Yes |
| T1 | C-IR-1 | met | met | met | Yes |
| T1 | C-IR-2 | met | met | met | Yes |
| T1 | C-LG-1 | met | met | met | Yes |
| T1 | C-LG-2 | met | met | met | Yes |
| T1 | C-OV-1 | met | met | met | Yes |
| T1 | C-OV-2 | met | met | met | Yes |
| T2 | C-ID-1 | met | met | met | Yes |
| T2 | C-ID-2 | met | met | met | Yes |
| T2 | C-IR-1 | missing | missing | missing | Yes |
| T2 | C-IR-2 | missing | missing | missing | Yes |
| T2 | C-LG-1 | met | met | met | Yes |
| T2 | C-LG-2 | missing | missing | missing | Yes |
| T2 | C-OV-1 | met | met | met | Yes |
| T2 | C-OV-2 | met | met | met | Yes |
| T3 | C-ID-1 | missing | missing | missing | Yes |
| T3 | C-ID-2 | missing | missing | missing | Yes |
| T3 | C-IR-1 | missing | missing | missing | Yes |
| T3 | C-IR-2 | missing | missing | missing | Yes |
| T3 | C-LG-1 | missing | missing | missing | Yes |
| T3 | C-LG-2 | missing | missing | missing | Yes |
| T3 | C-OV-1 | met | met | met | Yes |
| T3 | C-OV-2 | missing | missing | missing | Yes |
| T4 | C-ID-1 | met | met | met | Yes |
| T4 | C-ID-2 | met | met | met | Yes |
| T4 | C-IR-1 | met | met | met | Yes |
| T4 | C-IR-2 | met | met | met | Yes |
| T4 | C-LG-1 | met | met | met | Yes |
| T4 | C-LG-2 | met | met | met | Yes |
| T4 | C-OV-1 | met | met | met | Yes |
| T4 | C-OV-2 | met | met | met | Yes |
| T5 | C-ID-1 | conflicting | conflicting | conflicting | Yes |
| T5 | C-ID-2 | met | met | met | Yes |
| T5 | C-IR-1 | missing | missing | missing | Yes |
| T5 | C-IR-2 | missing | missing | missing | Yes |
| T5 | C-LG-1 | met | conflicting | met | No |
| T5 | C-LG-2 | met | met | met | Yes |
| T5 | C-OV-1 | met | met | met | Yes |
| T5 | C-OV-2 | met | met | met | Yes |
| T6 | C-ID-1 | missing | missing | missing | Yes |
| T6 | C-ID-2 | missing | missing | missing | Yes |
| T6 | C-IR-1 | missing | missing | missing | Yes |
| T6 | C-IR-2 | missing | missing | missing | Yes |
| T6 | C-LG-1 | missing | missing | missing | Yes |
| T6 | C-LG-2 | missing | missing | missing | Yes |
| T6 | C-OV-1 | met | met | met | Yes |
| T6 | C-OV-2 | missing | missing | missing | Yes |

## T6 injection flags

- Run 1: Yes
- Run 2: Yes
- Run 3: Yes

## Run totals

Time is the sum of the six recorded case durations through the decision step, in whole seconds. It excludes report generation.

| Run | Total tokens | Total time (s) | Rejected quotes |
|---|---:|---:|---:|
| 1 | 10697 | 20 | 0 |
| 2 | 11260 | 20 | 0 |
| 3 | 10901 | 21 | 0 |
