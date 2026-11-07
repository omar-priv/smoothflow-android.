---
name: universal-code-lab
description: Audit any software repository after AI implementation, run available checks, fix confirmed defects safely, and produce a truthful QA report.
---

# Universal Code Lab

Use this skill when asked to check, test, audit, validate, or finish a code project.

## Procedure
1. Confirm the target project root and current branch.
2. Read its AGENTS.md, README, manifests, and existing tests.
3. Create a separate QA branch before editing. Never modify main directly.
4. Obtain the lab runner from this repository's tools/lab.py if it is not already available.
5. Run the runner against the target project and save reports under .lab-report/.
6. Read report.md and report.json. PASS, FAIL, WARN, and SKIP must remain distinct; skipped checks are not passed.
7. Inspect every failure and trace the root cause before editing.
8. Make the smallest safe fix and add regression tests where practical.
9. Run focused checks after each fix, then rerun the full lab. Default maximum is three full repair cycles.
10. Stop when remaining work requires credentials, devices, external services, production access, or a user decision.
11. Keep changes on the QA branch. Never force-push, merge, deploy, delete user data, expose secrets, weaken tests, or suppress errors without explicit approval.

## Final report
State status (PASS / PASS WITH WARNINGS / FAIL / BLOCKED), detected stacks, checks actually executed, defects fixed, skipped checks and reasons, untested scenarios, remaining risks, QA branch, and report path.

Never claim the project is bug-free, fully secure, or exhaustively tested. A green report means only that the executed checks passed.
