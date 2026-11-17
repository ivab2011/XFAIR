# Evidence pack E5: close_valves (conflicting evidence)

FICTIONAL evidence written for testing XFAIR. Lakeside Water and LeakGuard are not real.

## Extract from IT security policy, section 4.2
LeakGuard runs under its own service account svc-leakguard-valves and never uses staff accounts.
The account may close only the twelve isolation valves listed in annex B.

## Extract from central log, 14 June 2027
08:12:04 account=ops-shared action=close_valve target=V-07 result=success source=LeakGuard
08:12:09 account=ops-shared action=close_valve target=V-08 result=success source=LeakGuard

## Extract from operations procedure OP-15, version 2
Maria, operations lead, or the duty engineer approves each valve closure proposed by LeakGuard and can override or stop LeakGuard at any time.
After a closure, staff can reopen the valve manually from the console within 5 minutes.

## Extract from logging configuration
Every LeakGuard action is written to the central log with time, account, action, target and result.
Logs are kept for 12 months and reviewed weekly by the duty engineer.
