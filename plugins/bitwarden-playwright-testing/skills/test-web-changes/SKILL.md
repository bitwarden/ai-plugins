---
name: test-web-changes
description: Use when you want UI tests planned and run against local Bitwarden web changes, starting from a Jira ticket, an implementation plan, or a description of the feature. Requires the Bitwarden local dev environment to already be running; this pipeline verifies services but never starts them. Accepts a Jira ticket ID, a Jira browse URL, an implementation plan file path, or a feature description, optionally followed by extra instructions. Add --confirm to review the test cases before execution begins.
argument-hint: "<jira-ticket-id | jira-url | feature-plan-path | feature-description> [extra instructions] [--confirm]"
allowed-tools:
  [
    Agent,
    Read,
    Write,
    Bash(mkdir *),
    Bash(*/bitwarden-playwright-testing/skills/compiling-test-report/scripts/merge_results.py *),
    Bash(*/bitwarden-playwright-testing/skills/compiling-test-report/scripts/render_report.py *),
  ]
---

You are the orchestrator for the Bitwarden web test pipeline. Your role is orchestration plus artifact persistence: you dispatch agents with the `Agent` tool, wait for each to return, and write their responses to artifact files. You do no research, exploration, or test execution yourself.

## Step 0 — Parse input

**`--confirm` flag**: present or absent. If present, strip it from the remaining input. Call what remains the raw input.

If the raw input is empty, show the user the usage line from this skill's `argument-hint` and stop.

**Primary source**: the first whitespace-delimited token of the raw input determines the input type and `<input value>`. Evaluate the rows in order and take the first match:

| First token                                                                                                                                                 | Input type    | `<input value>`      |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | -------------------- |
| The whole token matches `^[A-Za-z]{2,10}-\d+$` in any case, or the token is an `atlassian.net/browse/<KEY>` URL, with or without a query string or fragment | `jira-ticket` | The key, uppercased  |
| Ends with `.md`, or otherwise reads as a filesystem path. A URL is never a plan file.                                                                       | `plan-file`   | The token as given   |
| Anything else                                                                                                                                               | `description` | The entire raw input |

**Extra instructions**: everything after the first token, when the input type is `jira-ticket` or `plan-file`. This is guidance for you, not a value substituted anywhere by rule. Fold whatever is relevant into the dispatch prompts you write for each agent. If it references other tickets, research them with the skills available to you.

**Generate timestamp** (`YYYYMMDD-HHmm`) once now. Reuse it for all artifact filenames and <timestamp> placeholders in this run.

---

## The agents in this pipeline

Dispatch each with the `Agent` tool, using the agent type in the right column. Each returns its whole artifact as its final response; none of them persist anything themselves.

| Agent              | Agent type                                      |
| ------------------ | ----------------------------------------------- |
| `context-gatherer` | `bitwarden-playwright-testing:context-gatherer` |
| `code-explorer`    | `bitwarden-playwright-testing:code-explorer`    |
| `service-mapper`   | `bitwarden-playwright-testing:service-mapper`   |
| `test-planner`     | `bitwarden-playwright-testing:test-planner`     |
| `service-manager`  | `bitwarden-playwright-testing:service-manager`  |
| `test-runner`      | `bitwarden-playwright-testing:test-runner`      |

---

## Task 1: Gather context

Dispatch `context-gatherer` with:

```
Input type: <jira-ticket | plan-file | description>
Input value: <input value>
```

Wait for completion. The agent returns the full context as a markdown response.

**Derive the slug**:

| Input type    | Slug                                                                                                                                               |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `jira-ticket` | The key lowercased, then a few words naming the feature, drawn from the response's Feature Description section: `pm-38333-deferred-price-schedule` |
| `plan-file`   | The filename without its extension                                                                                                                 |
| `description` | A few words naming the feature, your judgement                                                                                                     |

Then sanitize it. The slug is used as a path segment, as a CLI argument, and in the final summary, so it may contain only `a-z`, `0-9`, and `-`: lowercase it; replace every character that is not `a-z` or `0-9` with a hyphen, deny-by-default with nothing exempt; collapse hyphen runs into one; strip leading and trailing hyphens; cap at 50 characters and strip a resulting trailing hyphen. The result must match `^[a-z0-9][a-z0-9-]*$`, otherwise use `pwt-<timestamp>`. A slug containing `/` is always wrong: it silently creates a nested tree instead of one artifact folder.

**Create output directory** and derive the `<artifacts-output-dir>` token: resolve the absolute path `<current working directory>/.playwright-testing-artifacts/<slug>/`, create that directory, and use it for `<artifacts-output-dir>` in every artifact path in the steps below.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/context-<timestamp>.md` using the `Write` tool.

---

## Task 2: Explore codebase

Dispatch `code-explorer` with:

```
Context artifact path: <artifacts-output-dir>/context-<timestamp>.md
```

Wait for completion. The agent returns the Application Context as a markdown response.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/app-context-<timestamp>.md` using the `Write` tool.

---

## Task 3: Determine required services

Tasks 3 and 4 both need only the artifacts from Task 2, so dispatch `service-mapper` and `test-planner` in the same message and let them run concurrently. Wait for both before starting Task 5.

Dispatch `service-mapper` with:

```
Context artifact path: <artifacts-output-dir>/context-<timestamp>.md
App-context artifact path: <artifacts-output-dir>/app-context-<timestamp>.md
```

Wait for completion. The agent returns the services list as a markdown response.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/services-<timestamp>.md` using the `Write` tool.

---

## Task 4: Build test cases

Dispatched together with Task 3, see above.

Dispatch `test-planner` with:

```
Context artifact path: <artifacts-output-dir>/context-<timestamp>.md
App-context artifact path: <artifacts-output-dir>/app-context-<timestamp>.md
```

Wait for completion. The agent returns the test cases as a markdown response. The response begins with the `## Test Cases` heading.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/test-cases-<timestamp>.md` using the `Write` tool.

---

## Task 5: Compose test plan

This is pure orchestrator work, no agent dispatch. Read both planning artifacts and assemble the final test plan.

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

## Optional review gate _(only if `--confirm` was set)_

Read `<artifacts-output-dir>/test-plan-<timestamp>.md`. Count the test cases and extract their names.

Display:

> "Test plan written to `<artifacts-output-dir>/test-plan-<timestamp>.md`
>
> **Test Cases (<N>):**
>
> - <test case name 1>
> - <test case name 2>
> - ...
>
> Proceed with test execution? (yes/no)"

- **No**: tell the user the test plan path and stop.
- **Yes**: continue.

If `--confirm` was not set, print: "Test plan complete — proceeding to test execution." and continue immediately.

---

## Task 6: Verify environment health

Dispatch `service-manager` with:

```
Test plan path: <artifacts-output-dir>/test-plan-<timestamp>.md
Artifacts output dir: <artifacts-output-dir>
```

Wait for completion. The agent will return either:

- A one-line success of the form `Environment verified: <N> services healthy, render OK.`
- Or an error block from the verifying-environment-health skill (preflight failure, health-check timeout, or render failure).

If the response is **not** the success confirmation, paste the response to the user and halt the run. Do not dispatch `test-runner` and do not write any artifact. If it is the success confirmation, proceed to Task 7.

No artifact is written for this task.

---

## Task 7: Execute tests

Track a segment counter `K`, starting at 1.

Dispatch `test-runner` with:

```
Test plan path: <artifacts-output-dir>/test-plan-<timestamp>.md
Artifacts output dir: <artifacts-output-dir>
```

Wait for the test-runner to return a JSON object. Then, on every response:

1. Write the response verbatim to `<artifacts-output-dir>/segment-<K>-<timestamp>.json` using the `Write` tool.
2. Run the merge script over all segment files so far, writing the canonical results file:

   ```
   <plugin>/skills/compiling-test-report/scripts/merge_results.py \
     <artifacts-output-dir>/segment-1-<timestamp>.json \
     ... \
     <artifacts-output-dir>/segment-<K>-<timestamp>.json \
     --output <artifacts-output-dir>/test-results-<timestamp>.json
   ```

   where `<plugin>` is `${CLAUDE_PLUGIN_ROOT}`. Read the `run_status=<status>` value from the script's stdout line.

3. Branch on `<status>`:

### paused

Read `need_user_input` from `<artifacts-output-dir>/test-results-<timestamp>.json`. Surface it to the user and capture the answer. Increment `K`, then re-dispatch `test-runner` with:

```
Test plan path: <artifacts-output-dir>/test-plan-<timestamp>.md
Checkpoint path: <artifacts-output-dir>/test-results-<timestamp>.json
Artifacts output dir: <artifacts-output-dir>
Resume: A prior test-runner agent paused at a [HUMAN] step. The user has now completed that action.
  Paused at: <the need_user_input text>
  User's answer: <user's answer>
```

Return to step 1 with the new response.

### aborted

Read `abort_reason` from `<artifacts-output-dir>/test-results-<timestamp>.json` and surface it to the user as the run outcome.

Then check the `cases` array in that same file:

- **`cases` is non-empty** (a resumed segment aborted after earlier segments completed work): proceed to Task 8. The report renders the completed cases with the abort reason banner at the top. Do NOT discard the run.
- **`cases` is empty** (setup failed before any test case ran): skip Task 8 and proceed directly to the final summary.

### complete

Capture the totals from the merge stdout line for the final summary, and proceed to Task 8. The canonical `test-results-<timestamp>.json` is already written.

---

## Task 8: Compile report

This is pure orchestrator work, no agent dispatch. Read the `## Required Services` line from `<artifacts-output-dir>/test-plan-<timestamp>.md` to form the services-tested string and the primary base URL, then run the render script:

```
<plugin>/skills/compiling-test-report/scripts/render_report.py \
  --results <artifacts-output-dir>/test-results-<timestamp>.json \
  --template-dir <plugin>/skills/compiling-test-report/templates \
  --output <artifacts-output-dir>/report-<timestamp>.html \
  --plan-name "<input value>" \
  --date "<timestamp>" \
  --slug "<slug>" \
  --services-tested "<services with ports, e.g. web (8080)>" \
  --base-url "<primary test URL, e.g. https://localhost:8080>" \
  --plan-file <artifacts-output-dir>/test-plan-<timestamp>.md
```

where `<plugin>` is `${CLAUDE_PLUGIN_ROOT}`. The script writes `report-<timestamp>.html` directly. If it exits non-zero, surface its stderr to the user as a report-generation failure and proceed to the final summary.

---

## Final summary

Present the final summary:

```
Test run complete for <input value>

Test plan: <artifacts-output-dir>/test-plan-<timestamp>.md
Report (HTML): <artifacts-output-dir>/report-<timestamp>.html

Results: <N> total | <N> passed | <N> passed (adaptive) | <N> failed | <N> errored
```
