# Universal Code Lab

A reusable QA lab for AI-built software. Point an AI coding agent at any project, run the lab, inspect the report, repair justified defects, and rerun checks.

## What it checks
- Detects Python, JavaScript/TypeScript, Go, Rust, Java, .NET, PHP, Ruby, shell, and Docker projects.
- Runs syntax/manifest checks and available native linters, tests, and builds.
- Records commands, exit codes, durations, and bounded output.
- Produces Markdown and JSON reports.
- Provides a reusable GitHub Actions workflow for other repositories.
- Can optionally send failed checks to an OpenAI-compatible AI endpoint, apply guarded fixes, rerun the lab, and open a draft pull request.
- Includes AI-agent instructions and skills for audit, triage, repair, and final reporting.

## Local use
Requires Python 3.9+; the runner itself uses only the Python standard library.

    python tools/lab.py --root . --output .lab-report

Windows:

    py -3 tools/lab.py --root . --output .lab-report

## Use from another GitHub repository
Copy examples/target-repo-workflow.yml to the target repository at .github/workflows/code-lab.yml. The sample enables optional AI repair on pushes and manual runs. Add the AI_API_KEY Actions secret and AI_BASE_URL / AI_MODEL repository variables before using it. Pull requests are audited but are not sent to the AI repair job. See [the setup guide](docs/AI-AUTO-REPAIR.md).

## AI agent
Use AGENT_PROMPT.md. Create a QA branch, run the lab against the target project, inspect every failure, make minimal justified fixes, run focused tests, rerun the full lab, and report skipped/unverified areas. Never merge automatically.

## AI-assisted automatic repair
The reusable workflow supports an optional bounded AI repair pass. When enabled, failed checks are sent with selected source files to an OpenAI-compatible Chat Completions endpoint. The repair runner validates the returned patch, refuses protected paths and unsafe patch types, reruns the lab, and opens a draft PR if source files changed. It never merges or deploys automatically. See [docs/AI-AUTO-REPAIR.md](docs/AI-AUTO-REPAIR.md) for setup and security limits.

## Important limitation
No tool can guarantee that every possible execution path or combination is bug-free. The lab runs available checks and reports what it could not verify. Meaningful UI and edge-case coverage requires project-specific tests such as Playwright, Cypress, Appium, or API contract tests. A skipped check is not a pass.

## Structure
- tools/lab.py: cross-language runner and report generator.
- .github/workflows/universal-lab.yml: reusable workflow.
- AGENTS.md: permanent agent rules.
- AGENT_PROMPT.md: copy/paste instruction.
- skills/: reusable agent skills.
- docs/: architecture and coverage limitations.
- examples/: workflow template.

MIT License.
