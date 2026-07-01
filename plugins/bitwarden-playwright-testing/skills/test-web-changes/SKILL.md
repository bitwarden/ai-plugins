---
name: test-web-changes
description: End-to-end Playwright testing pipeline for local Bitwarden web changes. Uses an agent team to generate test cases from a Jira ticket or feature implementation plan, start required services, run Playwright tests, and produce an HTML report — all in a single command. Use when you want to plan and run UI tests for local web changes without manual steps. Accepts a Jira ticket ID, a feature implementation plan file path, or a feature description. Add --confirm to pause for test case review before starting test execution.
argument-hint: "<jira-ticket-id | feature-plan-path | feature-description> [--confirm]"
allowed-tools: [Read, Write, Bash]
---

You are the team lead for the Bitwarden web test pipeline. Your role is orchestration plus artifact persistence: you dispatch agents, wait for them to complete, and write their responses to artifact files. You do no research, exploration, or test execution yourself.

## Step 0 — Parse input

Extract from the arguments:

- **`--confirm` flag**: present or absent. If present, strip it from the remaining input.
- **Input value**: the remaining argument text after stripping the flag above.
- **Input type**: detect from the input value:
  - Jira ticket: matches `[A-Z]+-\d+` (e.g., `PM-12345`)
  - Plan file: ends with `.md` and looks like a file path
  - Free-form description: anything else

**Generate timestamp** (`YYYYMMDD-HHmm`) once now. Reuse it for all artifact filenames and <timestamp> placeholders in this run.

**Derive slug** from the input value: lowercase, spaces and underscores replaced with hyphens, truncated to 40 chars. Fallback: `pwt-<timestamp>`.

**Create output directory** and derive the `<artifacts-output-dir>` token: resolve the absolute path `<current working directory>/.playwright-testing-artifacts/<slug>/`, create that directory, and use it for `<artifacts-output-dir>` in every artifact path in the steps below.

---

## Step 1 — Create team and add teammates

Create team named `pwt-<slug>`. Add all seven teammates:

| Teammate | Agent type |
|---|---|
| `context-gatherer` | `bitwarden-playwright-testing:context-gatherer` |
| `code-explorer` | `bitwarden-playwright-testing:code-explorer` |
| `service-mapper` | `bitwarden-playwright-testing:service-mapper` |
| `test-planner` | `bitwarden-playwright-testing:test-planner` |
| `service-manager` | `bitwarden-playwright-testing:service-manager` |
| `test-runner` | `bitwarden-playwright-testing:test-runner` |
| `report-compiler` | `bitwarden-playwright-testing:report-compiler` |

All teammates wait for explicit dispatch. They must not self-activate.

---

## Task 1: Gather context

Dispatch `context-gatherer` with:

```
Input type: <jira-ticket | plan-file | description>
Input value: <value>
```

Wait for completion. The agent returns the full context as a markdown response.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/context-<timestamp>.md` using the `Write` tool.

---

## Task 2: Explore codebase *(blockedBy: Task 1)*

Dispatch `code-explorer` with:

```
Context artifact path: <artifacts-output-dir>/context-<timestamp>.md
```

Wait for completion. The agent returns the Application Context as a markdown response.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/app-context-<timestamp>.md` using the `Write` tool.

---

## Task 3: Determine required services *(blockedBy: Task 2)*

Dispatch `service-mapper` with:

```
Context artifact path: <artifacts-output-dir>/context-<timestamp>.md
App-context artifact path: <artifacts-output-dir>/app-context-<timestamp>.md
```

Wait for completion. The agent returns the services list as a markdown response.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/services-<timestamp>.md` using the `Write` tool.

---

## Task 4: Build test cases *(blockedBy: Task 2)*

Dispatch `test-planner` with:

```
Context artifact path: <artifacts-output-dir>/context-<timestamp>.md
App-context artifact path: <artifacts-output-dir>/app-context-<timestamp>.md
```

Wait for completion. The agent returns the test cases as a markdown response. The response begins with the `## Test Cases` heading.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/test-cases-<timestamp>.md` using the `Write` tool.

---

## Task 5: Compose test plan *(blockedBy: Task 4)*

This is pure team-lead work — no agent dispatch. Read both planning artifacts and assemble the final test plan.

1. Read `<artifacts-output-dir>/services-<timestamp>.md` — this is the full services list.
2. Read `<artifacts-output-dir>/test-cases-<timestamp>.md` — this is the full test-cases list.
3. Write `<artifacts-output-dir>/test-plan-<timestamp>.md` using this exact template:

```markdown
# Test Plan

**Generated:** <timestamp>

<contents of services-<timestamp>.md, verbatim>

<contents of test-cases-<timestamp>.md, verbatim>
```

---

## Shut down planning teammates

Shut down `context-gatherer`, `code-explorer`, `service-mapper`, and `test-planner`. Standing teammates (`service-manager`, `test-runner`, `report-compiler`) remain.

---

## Optional review gate *(only if `--confirm` was set)*

Read `<artifacts-output-dir>/test-plan-<timestamp>.md`. Count the test cases and extract their names.

Display:

> "Test plan written to `<artifacts-output-dir>/test-plan-<timestamp>.md`
>
> **Test Cases (<N>):**
> - <test case name 1>
> - <test case name 2>
> - ...
>
> Proceed with test execution? (yes/no)"

- **No**: shut down remaining teammates, delete team, tell user the test plan path. Stop.
- **Yes**: continue.

If `--confirm` was not set, print: "Test plan complete — proceeding to test execution." and continue immediately.

---

## Task 6: Verify environment health *(blockedBy: Task 5)*

Dispatch `service-manager` with:

```
Test plan path: <artifacts-output-dir>/test-plan-<timestamp>.md
Artifacts output dir: <artifacts-output-dir>
```

Wait for completion. The agent will return either:

- A one-line success of the form `Environment verified: <N> services healthy, render OK.`
- Or an error block from the verifying-environment-health skill (preflight failure, health-check timeout, or render failure).

If the response is **not** the success confirmation, paste the response to the user and halt the run. Do not dispatch `test-runner`, do not write any artifact, do not run cleanup. If it is the success confirmation, proceed to Task 7.

No artifact is written for this task.

---

## Task 7: Execute tests *(blockedBy: Task 6)*

Dispatch `test-runner` with:

```
Test plan path: <artifacts-output-dir>/test-plan-<timestamp>.md
Artifacts output dir: <artifacts-output-dir>
```

Wait for the test-runner to return a response. 

### Handling test-runner pause responses

When the `test-runner` response contains `Need user input:`, it is a pause response with two parts:

1. **Partial results chunk**: everything up to and including `=== PARTIAL RUN — PAUSED ===`
2. **Question**: the `Need user input:` line (always last)

**On each pause:**

1. Extract the partial results chunk and the question.
2. Write/append the partial results chunk to `<artifacts-output-dir>/checkpoint-<timestamp>.md`:
   - First pause: create the file and write the chunk.
   - Subsequent pauses: open the file in append mode and add the chunk with a blank-line separator.
3. Surface the question to the user and capture the answer.
4. Re-dispatch `test-runner` with:

```
Test plan path: <artifacts-output-dir>/test-plan-<timestamp>.md
Checkpoint path: <artifacts-output-dir>/checkpoint-<timestamp>.md
Artifacts output dir: <artifacts-output-dir>
Resume: A prior test-runner agent paused at a [HUMAN] step. The user has now completed that action.
  Paused at: <verbatim text after "Need user input: ">
  User's answer: <user's answer>
```

5. Repeat from step 1 if the new agent also pauses.

### Handling test-runner complete response

When the test-runner returns a response containing `=== TEST RUN COMPLETE` (the full marker includes totals, e.g. `=== TEST RUN COMPLETE: 3 total, 2 passed, 0 passed (adaptive), 1 failed ===`), proceed to persist the artifact.

### Persist artifact 

Write `<artifacts-output-dir>/test-results-<timestamp>.md`. The file is one bare raw output block — no headers or markdown or any added prose or commentary.

**If no test pauses occurred** (no `checkpoint-<timestamp>.md` file exists): write the test-runner's response verbatim using the `Write` tool. It is already a single raw output block.

**If test pauses occurred** (checkpoint file exists): append the final raw output segment from the test-runner's response to `checkpoint-<timestamp>.md` with a blank-line separator, then assemble one merged raw output block:

*Note: the checkpoint file contains multiple raw output segments separated by blank lines. Each segment begins with `=== TEST RUN RESULTS ===` and ends with either `=== PARTIAL RUN — PAUSED ===` or `=== TEST RUN COMPLETE: ... ===`. Discard all segment headers, all intermediate `SUMMARY:` lines, and all `=== PARTIAL RUN — PAUSED ===` markers.*

1. Read `checkpoint-<timestamp>.md` in full.
2. Collect every `--- TEST CASE N: <name> --- ... --- END TEST CASE N ---` block across all segments, in order.
3. Sum the `SUMMARY:` counts across all segments to produce final totals (total, passed, adaptive, failed).
4. Write `test-results-<timestamp>.md` as exactly one block, verbatim:
   ```
   === TEST RUN RESULTS ===

   SUMMARY: <summed total> test cases | <summed passed> passed | <summed adaptive> passed (adaptive) | <summed failed> failed

   <all test case blocks from step 2, in order>

   === TEST RUN COMPLETE: <total> total, <passed> passed, <adaptive> passed (adaptive), <failed> failed ===
   ```

Capture the final totals from the `=== TEST RUN COMPLETE: ... ===` marker — you will reuse them in the Shutdown summary.

---

## Task 8: Compile report *(blockedBy: Task 7)*

Dispatch `report-compiler` with:

```
Test plan path: <artifacts-output-dir>/test-plan-<timestamp>.md
Test results path: <artifacts-output-dir>/test-results-<timestamp>.md
```

Wait for completion. The agent returns a single fenced ```html``` block containing the full HTML document.

**Persist artifact**: Extract the HTML body (the content between the ```html and ``` fences) and write it verbatim to `<artifacts-output-dir>/report-<timestamp>.html` using the `Write` tool.

---

## Shutdown

Shut down remaining teammates (`service-manager`, `test-runner`, `report-compiler`). Delete team `pwt-<slug>`.

Present final summary:

```
Test run complete for <input value>

Test plan: <artifacts-output-dir>/test-plan-<timestamp>.md
Report (HTML): <artifacts-output-dir>/report-<timestamp>.html

Results: <N> total | <N> passed | <N> passed (adaptive) | <N> failed
```
