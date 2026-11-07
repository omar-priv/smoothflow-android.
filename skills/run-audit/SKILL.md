---
name: run-universal-code-audit
description: Run Universal Code Lab against any software repository and produce an honest QA report.
---
# Run Universal Code Audit

Use when asked to check, audit, test, validate, or quality-review a completed project.

1. Identify the project root and current branch.
2. Read project instructions and manifests.
3. Run tools/lab.py against the project and save output to .lab-report/.
4. Read report.md and report.json.
5. Treat FAIL as a finding, WARN as a warning, and SKIP as unverified—not passed.
6. Inspect relevant files around reported failures; avoid dumping the entire repository into context.
7. Return prioritized findings and coverage gaps.

Never claim bug-free or exhaustive testing.
