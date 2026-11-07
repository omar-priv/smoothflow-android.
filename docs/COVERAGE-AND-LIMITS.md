# Coverage and limitations

No generic scanner can test every possible input, branch, state combination, device, browser, race condition, API response, or third-party outage. Full behavioral confidence requires a test model and project-specific automated tests.

## Recommended additions
- Web: Playwright or Cypress for login, main journeys, forms, validation, empty/loading/error states, responsive layouts, and accessibility.
- Android/iOS: unit tests plus emulator/device instrumentation tests for permissions, lifecycle, offline behavior, and screen sizes.
- APIs: schema/contract tests, authorization tests, rate limits, and integration tests against controlled test services.
- Desktop: UI automation and platform-specific builds.
- Security: dedicated scanners such as Gitleaks, Semgrep, Trivy, pip-audit, npm audit, or osv-scanner where appropriate.

The runner checks available toolchains and existing project scripts. Missing tools and missing tests are reported as skipped or unverified, never silently passed.
