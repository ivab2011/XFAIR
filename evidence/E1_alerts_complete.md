# Evidence pack E1: send_leak_alerts (complete)

FICTIONAL evidence written for testing XFAIR. Lakeside Water and LeakGuard are not real.

## Extract from IT access register, March 2027
LeakGuard runs under its own service account svc-leakguard. The account is not used by any staff member and has no interactive login.
The svc-leakguard account may read sensor data and send alerts to the operations channel. It has no permission to change pumps, valves or any plant setting. Permissions are reviewed every quarter.

## Extract from operations procedure OP-12
Maria, operations lead, is responsible for LeakGuard. She or the duty engineer can mute, override or switch off alerts at any time from the control-room console.
A false alert has no effect on the network; staff check and dismiss it, and alert sending can be paused immediately.

## Extract from logging configuration
Every LeakGuard action is written to the central log with time, account, action, target and result.
Logs are kept for 12 months and reviewed weekly by the duty engineer.

## Extract from incident response plan, version 3
The plan covers malfunction or misuse of LeakGuard. Significant incidents are reported to the national CSIRT with an early warning within 24 hours, a notification within 72 hours and a final report within one month.

## Extract from vendor contract, clause 9
The vendor shall notify Lakeside Water within 24 hours of any incident or vulnerability affecting LeakGuard.
