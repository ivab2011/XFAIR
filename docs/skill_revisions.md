# Evidence-check skill revisions

## 2026-11-17 — Run 2026-11-17T17-45-01-0500

The model marked C-OV-1 `met` after quoting “Maria, operations lead, can stop LeakGuard from the control-room console.” The sentence appeared in draft operations procedure OP-15.

**Old rule.** “missing: no quote shows it, or quotes show it is not in place, or the evidence says it is planned, a draft, or not yet decided.”

**Review by Iva Biscanic.** Keep C-OV-1 `met`. The sentence states that Maria can already stop LeakGuard. The draft status affects the manual takeover procedure assessed under C-OV-2, where the evidence says there is no written procedure yet.

**New rule.** “missing: no quote shows it, or quotes show it is not in place, or the evidence describes it only as planned or not yet decided. A statement of an existing capability counts as evidence even if it appears in a draft document; a draft that only describes intended future practice does not.”

**Why.** The evidence check now distinguishes what the document says exists today from what it says is planned. A draft can contain both kinds of statement.

## Revision 2 · 2026-11-17 · Promptfoo T2 review

**Quote fidelity.** The skill evaluation rejected the C-IR-2 quote “the vendor contract is still being negotiated and has no clause on notifying us of incidents.” The evidence starts that sentence with “The”, and the model changed the first letter. Rule 1 now says “Copy capitalisation and punctuation exactly. Start each quote at the beginning of a sentence or line in the evidence; do not change its first letter.”

**Agent identity in logs.** In the separate pipeline evaluation, the model marked C-LG-1 `missing` because it did not count the account field as evidence of agent identity. The evidence says LeakGuard has its own service account and that the log records the account. Iva Biscanic decided that the agent's own account counts as its identity. The control now reads “Every agent action is logged automatically with time, the agent's identity (its own account counts as its identity), action, target and result.”

**Archived reports.** The original reports are kept as `skill_v1.html`, `skill_v1.json`, `pipeline_v1.html`, and `pipeline_v1.json` in `reports/promptfoo/`.
