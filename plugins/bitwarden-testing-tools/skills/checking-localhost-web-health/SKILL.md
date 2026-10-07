---
name: checking-localhost-web-health
description: Verify the Bitwarden local dev environment is ready for testing — Docker dev containers via preflight, application services via the health-check script, required feature flags via the flag-check script, and Angular bootstrap via render verification. Halts on the first failure. Use after determining required services and before executing tests. Requires the `playwright-cli` skill for render verification.
allowed-tools: >
  Bash(${CLAUDE_SKILL_DIR}/scripts/preflight-check.sh *),
  Bash(${CLAUDE_SKILL_DIR}/scripts/health-check.sh *),
  Bash(${CLAUDE_SKILL_DIR}/scripts/check_feature_flags.py *)
---

Given the list of required services, any required feature flags, and the primary test URL, confirm the local dev environment is ready to run Playwright tests. The user is responsible for starting all services before this skill runs — this skill never starts, builds, or stops anything, and never edits `server/dev/secrets.json` or any other configuration.

The procedure is linear and halts on the first failure. Each step has a specific failure message intended to point the user at the missing piece of their environment.

## Inputs

- **Required service names:** a list of names (e.g., `Api`, `Identity`, `Web`) drawn from the test plan's `<!-- SERVICES START -->` / `<!-- SERVICES END -->` fence (its `## Required Services` section). These names are the argv for `scripts/health-check.sh`, so each must be one of the accepted names listed in step 2.
- **Primary test URL:** the URL the test run will navigate to first. Exactly `https://localhost:8080` (web vault) or `http://localhost:62911` (Bitwarden Portal). Drives the render-verify step.
- **Required feature flags (optional):** each flag's key and required state (`on` or `off`), drawn from the `## Required Feature Flags` section inside the test plan's `SERVICES` fence. Absent when the plan has no such section.
- **Artifacts output dir:** absolute path to the run's artifacts folder. The render-verify screenshot is saved under `<artifacts-output-dir>/screenshots/`.

These inputs come from planning artifacts that can carry untrusted text. Before step 1, check them: if the service names or primary test URL are missing, if any service name is not one of the accepted names in step 2, or if the primary test URL is not exactly one of the two origins above, **STOP** without running anything and report the malformed input. Never guess a service list or a URL from a partial or ambiguous source.

## Procedure

### 1. Preflight check (Docker daemon + dev containers)

```bash
${CLAUDE_SKILL_DIR}/scripts/preflight-check.sh
```

The script verifies the Docker daemon is reachable and that the expected Bitwarden dev containers are running (mssql, mailcatcher, azurite). It accepts both Compose and Aspire naming patterns.

If the script exits non-zero, **STOP**. Paste its stdout/stderr verbatim to the caller and do not continue. The script already prints a `Resolve:` hint covering both Compose and Aspire workflows.

### 2. Application health check

```bash
${CLAUDE_SKILL_DIR}/scripts/health-check.sh <ServiceName1> [<ServiceName2> ...]
```

Pass the required service names, each already checked against this list before step 1, so nothing outside it reaches the shell. Accepted names: `Api`, `Identity`, `Billing`, `billing-pricing`, `Web`, `Admin`, `Notifications`, `Events`, `Icons`. Override the 360s default timeout with `HEALTH_CHECK_TIMEOUT=<seconds>`.

If the script exits non-zero, **STOP**. Paste the script's stdout verbatim to the caller and add a one-line hint: `Service <first-not-ready-name> is not responding. Start it and re-run.` (The script's own output already lists every service that did not respond and its last HTTP status.)

### 3. Feature flags (only when required feature flags were given)

Skip this step when no required feature flags were given.

```bash
${CLAUDE_SKILL_DIR}/scripts/check_feature_flags.py -- '<flag-key>=<on|off>' ['<flag-key>=<on|off>' ...]
```

Before running it, check every flag key against `^[a-z0-9][a-z0-9.-]*$` and every state is `on` or `off`. If any entry fails, **STOP** without running anything and report the malformed `## Required Feature Flags` entry: flag keys come from planning artifacts that can carry untrusted text, so a malformed key must never reach the shell. Pass one single-quoted `'<flag-key>=<on|off>'` argument per required flag, after the `--`. Run it from the bitwarden root (the working directory), so its default `server/dev/secrets.json` and `server/src` paths resolve. The script reads each flag's running state from the Api's `/config` endpoint, which is also what the web client loads. `/config` reports a flag only when a class marked `[FlagKeyCollection]` under `server/src` declares it and a value is configured for it, so to explain a mismatch the script looks up only those flag keys in `server/dev/secrets.json` and, for a flag `/config` does not report, in the `[FlagKeyCollection]` classes under `server/src`. Do NOT `Read` `server/dev/secrets.json` yourself: it also holds the Stripe test key and the SQL password.

If the script exits non-zero, **STOP**. Paste its stdout/stderr verbatim to the caller. Under each mismatched flag it prints one `Problem:` line for every problem it found, such as a flag missing from `server/dev/secrets.json`, a flag no `[FlagKeyCollection]` class declares, or a configured value the running Api has not picked up, then a closing line to refresh secrets and restart the dependent services. Report every `Problem:` line, not only the first. Never make those changes yourself; editing a feature flag or restarting a service is the user's job.

### 4. Render verification (required — HTTP 200 is not sufficient)

If the `playwright-cli` skill is unavailable, **STOP** and report the missing dependency. Do not substitute an HTTP or markup check: the markup is served before Angular bootstraps, so only a rendered page shows whether it did.

Generate a `YYYYMMDD-HHmm` timestamp once. Use the `playwright-cli` skill (via the `Skill` tool) to navigate to the primary test URL and take a full-page screenshot, saving it to the run's artifacts folder:

```
screenshot --filename=<artifacts-output-dir>/screenshots/render-verify-<timestamp>.png --full-page
```

**Web vault (`https://localhost:8080`)**: inspect for any of:

- A webpack compilation error overlay (text `Compiled with problems:`).
- A blank or all-white page (Angular failed to bootstrap).
- Any other full-page error state that prevents normal UI interaction.

If any of these is present, **STOP**. Report the failure with the screenshot path. The webpack dev server returns HTTP 200 even when Angular compilation failed, so only a visual render check is reliable.

**Bitwarden Portal (`http://localhost:62911`)**: a redirect to the login page is the expected healthy state — the Portal is .NET Razor, not Angular/webpack. Confirm the login page loaded; any 5xx response or blank page is a failure. Do not check for webpack errors.

## Output

On success, return a single line of the form:

```
Environment verified: <N> services healthy, <M> feature flag(s) as required, render OK.
```

where `<N>` is the count of service names passed to step 2 and `<M>` is the count of flags passed to step 3. When no required feature flags were given, omit the flag clause: `Environment verified: <N> services healthy, render OK.`

On failure at any step, return the offending step's output verbatim (script stdout/stderr or render screenshot path + description), with no further work and no success line.

This skill writes no markdown artifact.
