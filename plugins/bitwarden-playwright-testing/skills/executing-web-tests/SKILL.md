---
name: executing-web-tests
description: Execute Bitwarden web test cases step-by-step using the playwright-cli skill directly. Use after test cases are defined and services are running. Governs tool policy, screenshot naming, toast capture, Setup Steps execution, and the billing blocker policy.
---

Given the test cases, artifacts output dir, and the absolute path to `scripts/playwright.config.json`, execute the tests by calling `Skill(playwright-cli)` for each browser action.

## Before you start

### Resolve these values from your inputs

| Value                | Source                                                                      |
| -------------------- | --------------------------------------------------------------------------- |
| Screenshot directory | `<artifacts-output-dir>/screenshots/`                                       |
| Config path          | The absolute path to `scripts/playwright.config.json` you received as input |
| Timestamp            | Generate once now as `YYYYMMDD-HHmm` and reuse across all screenshots       |

### Read the tool policy

Read `${CLAUDE_PLUGIN_ROOT}/references/tool-policy.md` — it governs which tools you may use throughout the run. Follow it without exception.

### Billing blocker policy

If any billing-related 400 error is encountered during setup or test-case execution, stop immediately, do not continue testing, and report the entire run as FAIL with the exact error before any partial completion is reported.

### Resume context (conditional)

Only when a `Resume:` block is present in your inputs: extract and hold:

- **Paused at** — the location string identifying the `[HUMAN]` step, e.g. `"Test Case 3, Setup Step 5: Attach a Stripe test clock"`
- **User's answer** — to apply to subsequent steps that reference the `[HUMAN]` step's result

For the resuming test case (the first test case in your input), before executing any of its steps:

1. Open the browser fresh: `playwright-cli open --config=<config-path>` (always first)
2. Re-establish browser session using credentials from that test case's SETUP steps in the test plan
3. Start from the step immediately after the `[HUMAN]` step identified by "Paused at", applying the user's answer to any steps that reference it

All subsequent test cases run fully and normally from their first step.

If the `[HUMAN]` step was the last step of the resuming test case (no test steps follow it within that case), record the test case result using the user's answer as the outcome of that step, then proceed to subsequent test cases or return the complete JSON object if none remain.

This protocol repeats for each `[HUMAN]` step encountered in a run. A second pause in a resumed run uses the same paused JSON object format.

A `Resume:` block in your inputs looks like:

```
Resume: Paused at <location string>. User's answer: <answer>.
```

## Step 1 — Initialize the browser session

Before any navigation, open the browser with the custom config to disable SSL certificate errors (`ignoreHTTPSErrors` in playwright.config.json is intentional: Bitwarden dev certs are self-signed and all navigation targets are localhost). This must be the first `playwright-cli` call — all subsequent interactions inherit this session:

```
Skill(playwright-cli): open --config=<config-path>
```

## Step 2 — Run setup and authentication

Any login, magic-link flow, or account/org creation required before the first test case is **setup**, not part of a test case.

**Resolve the admin-portal token at run time.** When a setup or test step contains the literal `<bitwarden-portal-admin-email>`, resolve it now (not earlier) by reading `server/dev/secrets.json` in the server repo and taking the first entry under the `admins` key. If the file is absent or `admins` is empty, mark the affected test case FAIL with that reason.

- Use `setup-{description}-{timestamp}.png` screenshot names during setup (e.g., `setup-login-complete-20260409-2057.png`)
- Apply the same "screenshot every visual state change" rule as during test cases (see Step 3)
- Record everything done: account email/password, org created, billing performed, email verifications followed, and any step that failed

**If setup or authentication cannot complete before the first test case runs** (for example login or account/org creation fails), the run cannot proceed and no test case has started. Return exactly this JSON object and stop, replacing `<reason>` with a one-line description of the failure: `{ "run_status": "aborted", "abort_reason": "setup failure before test cases (<reason>)" }`. Do not emit any cases.

## Step 3 — Execute test cases

Work through every test case in order. For each test case:

### 3a — Run Setup Steps first (if any)

Some test cases contain lines labeled `SETUP:`. Execute all of them before any Test Steps.

- Use `setup-tc-N-step-M-{timestamp}.png` screenshot names (N = test case number, M = setup step number)
- If any SETUP step fails — including any HTTP 4xx or 5xx response — stop this test case (not the whole run):
  1. Do NOT retry or modify parameters
  2. Mark the test case FAILED with the setup failure as the reason
  3. Do NOT run this test case's Test Steps; continue to the next test case
  4. Put the exact request and response body in `Notes:`

### 3b — Run Test Steps

After all SETUP steps complete, execute the Test Steps.

- Use `test-case-N-step-M-{timestamp}.png` screenshot names
- Assert each step's expected outcome and record PASS or FAIL

### Test case object format

Build each test case as a JSON object matching `${CLAUDE_PLUGIN_ROOT}/skills/compiling-test-report/references/examples/complete-run.json`:

```json
{
  "number": 1,
  "name": "<name>",
  "status": "PASS | PASS (adaptive) | FAIL | ERROR",
  "url": "<page under test, from the first navigation>",
  "setup_steps": [<step>, "..."],
  "test_steps": [<step>, "..."],
  "notes": "<notes, if any>",
  "adaptive": { "specified": "<what the plan asserted>", "found": "<what actually rendered>" }
}
```

Each step object:

```json
{
  "text": "<description>",
  "outcome": "PASS | FAIL | COMPLETED (User: <answer>)",
  "observed": "<what you observed on an assertion>",
  "screenshot": "<bare filename>",
  "human": true
}
```

- Omit `setup_steps` (or use `[]`) when the case has no setup steps.
- Omit `notes` when there is nothing to note.
- Include `observed` only on assertion steps, holding what you actually saw.
- Include `screenshot` only for a step that produced a visual change; use the exact filename from the screenshot directory listing.
- Set `"human": true` and `"outcome": "COMPLETED (User: <answer>)"` for a `[HUMAN]` step.
- Include `adaptive` only when `status` is `"PASS (adaptive)"`, filled from the adaptive evaluation.
- Do not emit run totals. The team lead's merge script derives them from the per-case `status` values.

### Adaptive assertion evaluation

After any assertion step fails, before recording the result, apply the evaluation in `${CLAUDE_SKILL_DIR}/references/adaptive-assertion-evaluation.md` — using only what you already observed during normal execution (no additional browser calls). It can resolve a failed assertion to `PASS (adaptive)`, but never when the feature behavior itself is wrong, the expected content is genuinely absent, the test couldn't run due to environment state, or the failed assertion was a URL/navigation check.

When a case resolves to `PASS (adaptive)`, set the case's `status` to `"PASS (adaptive)"` and fill its `adaptive` object with `specified` (what the plan asserted) and `found` (what actually rendered).

### Screenshot policy

Call `Skill(playwright-cli)` to take a full-page screenshot **after every visual state change** — no exceptions:

- After navigating to a new page or URL
- After a modal, dialog, or overlay opens or closes
- After a checkbox, toggle, accordion, or other element reveals or hides content
- After a form is submitted and a result or error appears
- After a toast or notification appears — capture immediately before it auto-dismisses (toasts last 2-5 seconds). Watch for up to 3 seconds after any state-changing action; if no toast appears, continue

Always save screenshots in the artifact output directory and pass `--full-page`: `screenshot --filename=<artifacts-output-dir>/screenshots/<name>.png --full-page`

Do NOT screenshot after: `run-code`, `eval`, `console`, `cookie-get`, or any pure-inspection action; or a step where nothing visible changed.

When in doubt, take the screenshot.

### Asserting transient toasts

Toasts can auto-dismiss in well under a second. Capture the text reliably from the live DOM per `${CLAUDE_SKILL_DIR}/references/asserting-transient-toasts.md`, which covers both the normal case and the Admin Portal's server-rendered post-back case.

### Continuity rule

External trigger results (external_trigger.py responses), email reads, and URL extractions are intermediate working steps, not stopping points. After each, proceed immediately to the next test step.

For email-driven flows (verification, magic-link login, trial activation, OTP), call the mailcatcher reader script directly via Bash (canonical path in references/tool-policy.md):

```
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py --recipient <email> --pattern <subject-keyword>
```

stdout is the URL — use it as input to the next browser step. The script already retries once on `NO_MATCH`; a non-zero exit after the retry is a hard failure — mark the test case FAIL immediately with the `NO_MATCH` diagnostic in Notes. Do not attempt to read Mailcatcher via any other means (curl, direct API calls, or sub-agent). Do not invoke `Skill(reading-mailcatcher-api)` (it is documentation for the underlying API; the co-located script is the only sanctioned transport).

### Human step halt

When executing any step (Setup or Test) whose text begins with `[HUMAN]`, halt immediately. Do not retry, infer, or skip.

Return a single JSON object with the cases completed so far and the pause signal, matching `${CLAUDE_PLUGIN_ROOT}/skills/compiling-test-report/references/examples/paused-segment.json`:

```json
{
  "run_status": "paused",
  "cases": [<completed test case object>, "..."],
  "need_user_input": "<step text after the [HUMAN] marker, verbatim, with location context, e.g. \"Test Case 1, Setup Step 8: Attach a Stripe test clock to the subscription.\">"
}
```

Rules:

- `cases` holds only the test cases completed before the pause (use `[]` if none).
- `need_user_input` is required and is the resume question.
- Do not set `run_status` to `"complete"` on a pause.

## Step 4 - Produce the required output

Do not return until every test case object is complete. Before assembling the output, run `ls <screenshot-dir>/*<timestamp>*` to get the ground-truth screenshot filenames, and use them verbatim in each step's `screenshot` field.

Return a single JSON object and nothing else, matching `${CLAUDE_PLUGIN_ROOT}/skills/compiling-test-report/references/examples/complete-run.json`:

```json
{
  "run_status": "complete",
  "cases": [<test case object>, "..."]
}
```

If setup or authentication failed before any test case ran (see Step 2), return the aborted object instead, with no cases:

```json
{
  "run_status": "aborted",
  "abort_reason": "setup failure before test cases (<reason>)"
}
```
