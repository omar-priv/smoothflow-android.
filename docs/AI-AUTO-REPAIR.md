# Optional AI auto-repair

Universal Code Lab can run an AI repair pass after its normal checks fail. The AI does not run on every project change: it runs only when the caller enables `auto_repair: true`, a check failed, and the triggering event is not a pull request.

## Setup in the project being checked

1. Copy `examples/target-repo-workflow.yml` from this repository to the target project as `.github/workflows/code-lab.yml`.
2. In the target GitHub repository, open **Settings → Secrets and variables → Actions**.
3. Add a repository secret named `AI_API_KEY` with the API key for an OpenAI-compatible Chat Completions provider.
4. Add a repository variable named `AI_BASE_URL`. For an OpenAI-compatible endpoint, use its API base URL (not the `/chat/completions` suffix).
5. Add a repository variable named `AI_MODEL` containing a model identifier supported by that provider.
6. Push a commit to the project branch, or manually run the target project's **Universal Code Lab** workflow.

The supplied example enables auto-repair on push and manual runs. Pull requests are still audited, but AI repair is intentionally skipped for pull-request events to reduce exposure to untrusted contributions and secrets.

## What happens

1. The reusable workflow checks out the target project and runs `tools/lab.py`.
2. It uploads `universal-code-lab-report` with the original Markdown and JSON report.
3. When the lab fails and auto-repair is enabled, the repair job downloads that report and sends the relevant failures and selected source files to the configured model.
4. The model must return a unified Git diff. The runner checks the paths, validates the patch with `git apply --check`, applies it, and reruns the lab.
5. The runner makes at most two repair attempts in the supplied workflow.
6. If files changed, GitHub Actions pushes a separate branch and opens a **draft pull request**. It never merges or deploys the changes automatically.
7. The `universal-code-lab-ai-repair` artifact contains the repair summary, attempted patches, and recheck reports.

## Safety boundaries

- The API key is passed to the repair process as an environment variable; it is not included in the prompt and is removed from the environment before any project tests are rerun.
- GitHub checkout credentials are not persisted while project code is inspected or tested. Write access is configured only in the final step that pushes the proposed branch and opens the PR.
- Secret-like values and common token formats in report excerpts and source files are redacted before sending.
- Automatic patches cannot modify GitHub workflow files, this lab's own runner, secret/credential paths, environment files, dependency lockfiles, or existing tests.
- Deletions, renames, binary changes, symlinks, path traversal, and patches outside the project root are rejected.
- The repair loop is bounded (maximum three cycles in the script; two in the supplied workflow).
- An unresolved failure remains a failure. The pull request is draft and must be reviewed and merged by a person.

These safeguards reduce risk but do not make AI-generated code inherently safe. Review every proposed change, inspect the final report, and run project-specific UI, API, device, and deployment checks that the generic lab cannot provide.

## Reusable workflow inputs

| Input | Default | Purpose |
|---|---|---|
| `timeout` | `300` | Per-check timeout in seconds |
| `auto_repair` | `false` | Enable the AI repair job |
| `ai_base_url` | `https://api.openai.com/v1` | OpenAI-compatible API base URL |
| `ai_model` | `gpt-4.1-mini` | Provider-specific model identifier |

The calling workflow must grant `contents: write` and `pull-requests: write` for draft PR creation. If the secret is missing, the audit still runs and AI repair is skipped.
