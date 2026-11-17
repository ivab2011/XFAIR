# Control themes (XFAIR midpoint scope)

DRAFT prepared with Claude for Iva Biscanic's review. Iva's expert sign-off: [x] approved on 2026-11-17 (crosswalk review)

XFAIR checks an AI agent against four control themes. Each theme pairs an AI duty
(what the AI rules ask) with the cyber controls that prove it (how security frameworks
make it checkable). Each theme has two concrete controls that the evidence check looks for.

## T1 Agent identity and access

The agent acts as its own identity, not as a person. It can do only what its charter allows.

- **C-ID-1 Own identity.** The agent has its own account or credential, separate from any staff
  login, so every action can be traced to the agent.
- **C-ID-2 Least privilege.** The agent's permissions are limited to the actions listed in its
  charter, and are reviewed.

Why it matters: an agent working under a shared staff login cannot be told apart from a person,
cannot be switched off on its own, and turns one stolen password into control of the plant
(OWASP ASI03, identity and privilege abuse).

## T2 Human oversight and intervention

A named person can step in, and the effect of an action can be undone or replaced by manual operation.

- **C-OV-1 Approve, override or stop.** A named person can approve, override or stop the
  agent's actions.
- **C-OV-2 Undo or manual fallback.** An action can be reversed, or staff can take over manually
  within a stated time.

## T3 Logging and record-keeping

Every action leaves a record that a person can check later.

- **C-LG-1 Automatic action log.** Every agent action is logged automatically with time, agent
  identity, action, target and result.
- **C-LG-2 Retention and review.** Logs are kept for at least six months and reviewed.

## T4 Incident detection and reporting

When the agent misbehaves or is misused, the utility notices, reports on time and hears from its vendor.

- **C-IR-1 Incident plan covering the agent.** The incident plan covers agent malfunction or
  misuse, including the NIS2 deadlines (early warning within 24 hours, notification within 72 hours,
  final report within one month).
- **C-IR-2 Vendor notification.** The contract requires the agent's vendor to notify the utility
  of incidents and vulnerabilities affecting the agent.

## Out of scope for the midpoint

Data governance, robustness testing, accountability and roles, transparency and training.
They return after the midpoint (and with the Singapore IMDA benchmark).
