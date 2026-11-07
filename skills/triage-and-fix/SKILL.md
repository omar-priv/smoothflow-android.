---
name: triage-and-fix
description: Diagnose QA findings, make minimal safe fixes, and verify regressions.
---
# Triage and Fix

1. Work on a dedicated QA branch.
2. Classify findings: confirmed defect, environment/tooling issue, flaky test, or unverified risk.
3. Reproduce with the narrowest relevant command.
4. Trace root cause before changing code.
5. Make the smallest safe fix and preserve intended behavior.
6. Add a regression test where practical.
7. Run focused checks, then the full lab.
8. Repeat up to three full repair cycles by default.
9. Never delete/weaken tests or suppress errors to get a green result.
10. Stop when blocked by secrets, devices, external services, production access, or user decisions.
