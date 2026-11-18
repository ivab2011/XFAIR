# Progress handoff

## Midpoint status

XFAIR runs Maria’s fictional water-utility cases from evidence through a decision trace. The repository has an approved eight-row crosswalk, 32 official passages, seven evidence cases, and two recorded skill revisions. The original six-case evaluation passed 6/6. The three-run stability check used those same six cases and found one raw finding change, with the same final level and status for every case. Promptfoo v2 includes T7 and passed 20/21 in each suite. [Midpoint submission](SUBMISSION.md) · [Setup and commands](README.md)

## Start the next session here

1. Read the T4 trace to see how a finding moves from an official provision through a control to the decision. It grants `act_with_approval` because valve closure fails the irreversible-action rule. [T4 trace](reports/2026-11-17T17-59-25-0500/T4.md)
2. Review the two remaining Promptfoo v2 failures before changing the skill. One T2 pipeline run still treated the logged account as insufficient proof of agent identity. One T5 skill run treated the fiction disclaimer as an injection. Keep the v1 and v2 reports for comparison and use a new suffix for another evaluation. [Skill v2](reports/promptfoo/skill_v2.html) · [Pipeline v2](reports/promptfoo/pipeline_v2.html) · [Revision log](docs/skill_revisions.md)
3. Build the three-check workflow and a human review path for disagreements. The current stability script compares saved runs after the fact, and the existing override file records individual human reviews. [Stability report](reports/stability.md) · [Human reviews](overrides/human_overrides.json)
4. Arrange the second independent review, add evidence cases, and build the incident clocks view and run-output web interface. Keep the Article 12 question about agent version and triggering input open for review. [Final plan](SUBMISSION.md#plan-for-the-final)

Add the midpoint video link once it is available.
