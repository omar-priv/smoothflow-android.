# Using the lab with coding agents

## ChatGPT, OpenCode, Claude Code, Cursor, Copilot, and other agents

1. Open the target project in the agent.
2. Give it the instructions in AGENT_PROMPT.md (or point it to this repository).
3. Ask it to create a QA branch and run the lab against the target project.
4. The agent should inspect the generated report, repair confirmed defects, and rerun checks.
5. Review the final report and branch before merging.

AGENTS.md is the portable baseline. CLAUDE.md and .github/copilot-instructions.md point those tools back to the same rules. Tool-specific skill formats vary, so use the Markdown skill definitions as reusable procedures rather than assuming every agent auto-loads them.

## Reusable GitHub Actions

Copy examples/target-repo-workflow.yml into the target repository at .github/workflows/code-lab.yml. This enables checks on pushes and pull requests. The report is uploaded as a workflow artifact.

## Local execution

The runner is read-only with respect to source files; test/build tools may create their normal generated outputs. Run it from the project root with Python 3.9+.

## Combine GitHub checks with an AI repair agent

For a mostly automatic workflow, copy `examples/target-repo-workflow.yml` into the target repository as `.github/workflows/code-lab.yml`, then configure its Actions secret and variables as described in [AI auto-repair setup](AI-AUTO-REPAIR.md).

On a push, GitHub runs the audit. If checks fail and `auto_repair` is enabled, a separate AI repair process calls the configured OpenAI-compatible endpoint, applies only an allowed patch, reruns the lab, and opens a draft PR. Pull requests are audited but deliberately do not trigger the AI repair pass. No PR is merged automatically.

Important distinction: this is a separate AI process running in GitHub Actions. It does not attach itself to, or continue controlling, the live OpenCode/Claude/Cursor/ChatGPT coding-agent session that originally built the project. The local agent can still use `AGENT_PROMPT.md`; the GitHub-side agent uses the API key and model configured in the target repository.

