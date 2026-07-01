---
name: executing-web-tests
description: Execute Bitwarden web test cases step-by-step using the playwright-cli skill directly. Use after test cases are defined and services are running. Governs tool policy, screenshot naming, toast capture, Setup Steps execution, and the billing blocker policy.
---

Given the test cases, artifacts output dir, and the absolute path to `scripts/playwright.config.json`, execute the tests yourself by calling `Skill(playwright-cli)` for each individual browser action.

## Before you start

### Resolve these values from your inputs

| Value                | Source                                                                        |
| -------------------- | ----------------------------------------------------------------------------- |
| Screenshot directory | `<artifacts-output-dir>/screenshots/` |
| Config path          | The absolute path to `scripts/playwright.config.json` you received as input   |
| Timestamp            | Generate once now as `YYYYMMDD-HHmm` and reuse across all screenshots         |

### Read the tool policy

Read `${CLAUDE_PLUGIN_ROOT}/references/tool-policy.md`. This governs which tools you may use throughout the run. Follow it without exception.

### Billing blocker policy

If any billing-related 400 error is encountered during setup or test-case execution, stop immediately, do not continue testing, and report the entire run as FAIL with the exact error before any partial completion is reported.

### Resume context (conditional)

Only when a `Resume:` block is present in your inputs: extract and hold:
- **Paused at** — the location string identifying the `[HUMAN]` step, e.g. `"Test Case 3, Setup Step 5: Attach a Stripe test clock"`
- **User's answer** — to apply to subsequent steps that reference the `[HUMAN]` step's result

For the resuming test case (your caller always passes remaining test cases starting with the paused one, so this is the first test case in your input), before executing any of its steps:
1. Open the browser fresh: `playwright-cli open --config=<config-path>` (always first, same as any run)
2. Re-establish browser session using credentials from that test case's SETUP steps in the test plan
3. Start from the step immediately after the `[HUMAN]` step identified by "Paused at", applying the user's answer to any steps that reference it

All subsequent test cases run fully and normally from their first step.

If the `[HUMAN]` step was the last step of the resuming test case (no test steps follow it within that case), record the test case result using the user's answer as the outcome of that step, then proceed to subsequent test cases or produce `=== TEST RUN COMPLETE ===` if none remain.

This protocol repeats for each `[HUMAN]` step encountered in a run — a second pause in a resumed run uses the same partial-emit and signal format.

A `Resume:` block in your inputs looks like:
```
Resume: Paused at <location string>. User's answer: <answer>.
```

## Step 1 — Initialize the browser session

Before any navigation, open the browser with the custom config to disable SSL certificate errors. This must be the first `playwright-cli` call — all subsequent interactions inherit this session:

```
Skill(playwright-cli): open --config=<config-path>
```

## Step 2 — Run setup and authentication

Any login, magic-link flow, or account/org creation required before the first test case is **setup**, not part of a test case.

- Use `setup-{description}-{timestamp}.png` screenshot names during setup (e.g., `setup-login-complete-20260409-2057.png`)
- Apply the same "screenshot every visual state change" rule as during test cases (see Step 3)
- Record everything done: account email/password, org created, billing performed, email verifications followed, and any step that failed

## Step 3 — Execute test cases

Work through every test case in order. For each test case:

### 3a — Run Setup Steps first (if any)

Some test cases contain lines labeled `SETUP:`. Execute all of them before any Test Steps.

- Use `setup-tc-N-step-M-{timestamp}.png` screenshot names (N = test case number, M = setup step number)
- If any SETUP step fails — including any HTTP 4xx or 5xx response — stop immediately:
  1. Do NOT retry or modify parameters
  2. Mark the test case FAILED with the setup failure as the reason
  3. Do NOT proceed to Test Steps or subsequent test cases
  4. Put the exact request and response body in `Notes:`

### 3b — Run Test Steps

After all SETUP steps complete, execute the Test Steps.

- Use `test-case-N-step-M-{timestamp}.png` screenshot names
- Assert each step's expected outcome and record PASS or FAIL

### Test case block format

Every test case block — in the run-complete output (Step 4) and in the partial output emitted at a `[HUMAN]` halt — uses this exact shape:

```
--- TEST CASE N: <name> ---
Status: <PASS | PASS (adaptive) | FAIL | ERROR>
Setup Steps:
Setup Step 1: <description> — <PASS | FAIL>
  Screenshot: setup-tc-N-step-1-<timestamp>.png
[HUMAN] Setup Step M: <description> — COMPLETED (User: <answer>)
Test Steps:
Step 1: <description> — <PASS | FAIL>
  Screenshot: test-case-N-step-1-<timestamp>.png
Step 2: Assert <selector/condition> — <PASS | FAIL> (<what was actually observed>)
Notes: <notes, if any>
--- END TEST CASE N ---
```

- `Status:` is the first line of the block.
- Omit the entire `Setup Steps:` section when the test case has no setup steps.
- A `  Screenshot: <filename>` line (two-space indent) goes on the line immediately after the step it documents — one line per screenshot, only when that step produced a visual change. Do not collect screenshots into a trailing list.
- For an assertion step, append what you actually observed in parentheses after the outcome — e.g. `Step 4: Assert ".badge.bg-secondary" visible — PASS (badge text: "Inactive")`.
- `[HUMAN]` prefixes a human-completed step; its outcome is `COMPLETED (User: <answer>)`.
- Omit `Notes:` when there is nothing to note.

### Adaptive assertion evaluation

After any assertion step fails, apply this evaluation before recording the result — using only what you already observed during normal execution:

1. Review page content, visible text, error messages, and element content already in your context and screenshots. Do NOT issue additional browser calls.
2. Ask: "Is the semantic condition this assertion was checking demonstrably present in what I already observed?" The semantic condition is the underlying behavior or content the test intends to verify, independent of the specific CSS selector or element path the plan specified.
3. Apply the rule to each failed assertion individually:
   - If **all** failed assertions resolve adaptively → record the test case as `PASS (adaptive)`
   - If **any** failed assertion represents a genuine failure → record `FAIL`; document the adaptive assessments for the resolved assertions in Notes
4. When recording `PASS (adaptive)`, write in Notes:
   - What the plan's assertion specified
   - What was actually found
   - Why the semantic condition is considered met
5. Do NOT apply adaptive evaluation when:
   - The feature behavior itself is wrong (e.g., the server accepted input it should have rejected)
   - The expected content or behavior is genuinely absent from the page
   - The test could not run due to environment state (dirty database, missing seed data, skipped `[HUMAN]` step)
   - The failed assertion was a URL/navigation check (wrong URL always means wrong behavior)

### Screenshot policy

Call `Skill(playwright-cli)` to take a full-page screenshot **after every visual state change** — no exceptions:

- After navigating to a new page or URL
- After a modal, dialog, or overlay opens or closes
- After a checkbox, toggle, accordion, or other element reveals or hides content
- After a form is submitted and a result or error appears
- After a toast or notification appears — capture immediately before it auto-dismisses (toasts last 2-5 seconds). Watch for up to 3 seconds after any state-changing action; if no toast appears, continue

Always save screenshots in the artifact output directory and pass `--full-page`: `screenshot --filename=<artifacts-output-dir>/screenshots/<name>.png --full-page`

Do NOT screenshot after: `run-code`, `eval`, `console`, `cookie-get`, or any pure-inspection action; or a step where nothing visible changed.

When in doubt, take the screenshot. A redundant screenshot costs nothing; a missing one cannot be recovered.

### Asserting transient toasts

Toasts can auto-dismiss in well under a second. To capture toast text reliably, read it from the live DOM: use `playwright-cli eval` to read the toast region's text right after the action, or `playwright-cli run-code` to wait for the toast region and return its text (arm the wait together with the triggering action so a short-lived toast is caught as it renders).

When the action causes a full page reload (the server-rendered Admin Portal — ASP.NET MVC), the new page fires the toast from an inline `document.ready` script, so the action's promise resolves before the toast renders and arming a wait alongside the action cannot catch it. For this post-back case, read the toast from the new page instead: assert its text from the inline `toastr.*("...")` call in the page source, or read the toast node on the new page's load.

### Continuity rule

External trigger results (curl responses), email reads, and URL extractions are intermediate working steps — not stopping points. After each, proceed immediately to the next test step.

For email-driven flows (verification, magic-link login, trial activation, OTP), call the mailcatcher reader script directly via Bash:

```
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read-mailcatcher.sh --recipient <email> --pattern <subject-keyword>
```

stdout is the URL — use it as input to the next browser step. The script already retries once on `NO_MATCH`; a non-zero exit after the retry is a hard failure — mark the test case FAIL immediately with the `NO_MATCH` diagnostic in Notes. Do not attempt to read Mailcatcher via any other means (curl, direct API calls, or sub-agent). Do not invoke `Skill(reading-mailcatcher-api)` (it is documentation for the underlying API; the co-located script is the only sanctioned transport).

### Human step halt

When executing any step (Setup or Test) whose text begins with `[HUMAN]`, halt immediately. Do not retry, infer, or skip.

Before returning, emit all completed test-case blocks using the Test case block format defined in Step 3, close the block with the pause marker, then append the signal as the very last line:

```
=== TEST RUN RESULTS ===

SUMMARY: <N completed in this segment> test cases | N passed | N passed (adaptive) | N failed

--- TEST CASE N: <name> ---
[emit completed test case block using the Test case block format defined in Step 3]
--- END TEST CASE N ---

[one block per completed test case, in order]

=== PARTIAL RUN — PAUSED ===

Need user input: <step text after the [HUMAN] marker, verbatim, with location context — e.g. "Test Case 1, Setup Step 8: Attach a Stripe test clock to the subscription.">
```

Rules:
- `SUMMARY:` reflects only test cases completed in this segment.
- If zero test cases have completed yet, write `SUMMARY: 0 test cases | 0 passed | 0 passed (adaptive) | 0 failed` and omit the test case blocks.
- `=== PARTIAL RUN — PAUSED ===` is the segment delimiter and replaces `=== TEST RUN COMPLETE ===` on a pause.
- `Need user input:` is always the very last line of the response.
- Do not produce `=== TEST RUN COMPLETE ===` on a pause.

You are not done with a test case until both SETUP steps and Test Steps are complete with PASS or FAIL recorded. You are not done with the run until all test cases are complete and the `=== TEST RUN COMPLETE ===` marker is produced.

## Step 4 — Produce the required output

Do not return until every test case has a complete block. The `=== TEST RUN COMPLETE ===` line may only appear after all blocks.

Before writing the output block, run:

```bash
ls <screenshot-dir> | grep '<timestamp>'
```

This gives you the ground-truth list of screenshots this run actually wrote. For each test case N, files whose names contain `test-case-N-` are that case's test-step screenshots and `setup-tc-N-` are its setup-step screenshots. Use these exact filenames in the indented `Screenshot:` lines — place each on the line immediately after the step it documents — and do not reconstruct names from memory.

```
=== TEST RUN RESULTS ===

SUMMARY: N test cases | N passed | N passed (adaptive) | N failed

--- TEST CASE N: <name> ---
[emit test case block using the Test case block format defined in Step 3]
--- END TEST CASE N ---

[one block per test case, in order]

=== TEST RUN COMPLETE: N total, N passed, N passed (adaptive), N failed ===
```
