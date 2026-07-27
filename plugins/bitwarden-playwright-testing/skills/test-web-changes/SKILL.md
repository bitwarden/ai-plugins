---
name: test-web-changes
description: End-to-end Playwright testing pipeline for local Bitwarden web changes. Uses an agent team to generate test cases from a Jira ticket or feature implementation plan, start required services, run Playwright tests, and produce an HTML report — all in a single command. Use when you want to plan and run UI tests for local web changes without manual steps. Accepts a Jira ticket ID, a feature implementation plan file path, or a feature description. Add --confirm to pause for test case review before starting test execution.
argument-hint: "<jira-ticket-id | feature-plan-path | feature-description> [--confirm]"
allowed-tools:
  [
    Read,
    Write,
    Bash(mkdir *),
    Bash(*/bitwarden-playwright-testing/skills/compiling-test-report/scripts/merge_results.py *),
    Bash(*/bitwarden-playwright-testing/skills/compiling-test-report/scripts/render_report.py *),
  ]
---

You are the team lead for the Bitwarden web test pipeline. Your role is orchestration plus artifact persistence: you dispatch agents, wait for them to complete, and write their responses to artifact files. You do no research, exploration, or test execution yourself.

## Step 0 — Parse input

**`--confirm` flag**: present or absent. If present, strip it from the remaining input. Call what remains the raw input.

**Primary source**: the first whitespace-delimited token of the raw input determines the input type and `<input value>`:

| First token                                                          | Input type    | `<input value>`      |
| -------------------------------------------------------------------- | ------------- | -------------------- |
| Matches `[A-Z]{2,10}-\d+`, or is an `atlassian.net/browse/<KEY>` URL | `jira-ticket` | The key, uppercased  |
| Ends with `.md`, or otherwise reads as a filesystem path             | `plan-file`   | The token as given   |
| Anything else                                                        | `description` | The entire raw input |

**Extra instructions**: everything after the first token, when the input type is `jira-ticket` or `plan-file`. This is guidance for you, not a value substituted anywhere by rule. Fold whatever is relevant into the dispatch prompts you write for each agent. If it references other tickets, research them with the skills available to you.

**Generate timestamp** (`YYYYMMDD-HHmm`) once now. Reuse it for all artifact filenames and <timestamp> placeholders in this run.

**Derive run ID**: the Jira key lowercased, else the plan filename without its extension, else the timestamp. Used only for the team name.

---

## Step 1 — Create team and add teammates

Create team named `pwt-<run-id>`. Add all six teammates:

| Teammate           | Agent type                                      |
| ------------------ | ----------------------------------------------- |
| `context-gatherer` | `bitwarden-playwright-testing:context-gatherer` |
| `code-explorer`    | `bitwarden-playwright-testing:code-explorer`    |
| `service-mapper`   | `bitwarden-playwright-testing:service-mapper`   |
| `test-planner`     | `bitwarden-playwright-testing:test-planner`     |
| `service-manager`  | `bitwarden-playwright-testing:service-manager`  |
| `test-runner`      | `bitwarden-playwright-testing:test-runner`      |

All teammates wait for explicit dispatch. They must not self-activate.

---

## Task 1: Gather context

Dispatch `context-gatherer` with:

```
Input type: <jira-ticket | plan-file | description>
Input value: <input value>
```

Wait for completion. The agent returns the full context as a markdown response.

**Derive the slug** from that returned context:

| Input type    | Slug                                                                                                                                               |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `jira-ticket` | The key lowercased, then a few words naming the feature, drawn from the response's Feature Description section: `pm-38333-deferred-price-schedule` |
| `plan-file`   | The filename without its extension                                                                                                                 |
| `description` | A few words naming the feature, your judgement                                                                                                     |

Then sanitize it. The slug is used as a path segment, as a CLI argument, and in the final summary, so it may contain only `a-z`, `0-9`, and `-`: lowercase it; replace every character that is not `a-z` or `0-9` with a hyphen, deny-by-default with nothing exempt; collapse hyphen runs into one; strip leading and trailing hyphens; cap at 50 characters and strip a resulting trailing hyphen. The result must match `^[a-z0-9][a-z0-9-]*$`, otherwise use `pwt-<timestamp>`. A slug containing `/` is always wrong: it silently creates a nested tree instead of one artifact folder.

**Create output directory** and derive the `<artifacts-output-dir>` token: resolve the absolute path `<current working directory>/.playwright-testing-artifacts/<slug>/`, create that directory, and use it for `<artifacts-output-dir>` in every artifact path in the steps below.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/context-<timestamp>.md` using the `Write` tool.

---

## Task 2: Explore codebase _(blockedBy: Task 1)_

Dispatch `code-explorer` with:

```
Context artifact path: <artifacts-output-dir>/context-<timestamp>.md
```

Wait for completion. The agent returns the Application Context as a markdown response.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/app-context-<timestamp>.md` using the `Write` tool.

---

## Task 3: Determine required services _(blockedBy: Task 2)_

Dispatch `service-mapper` with:

```
Context artifact path: <artifacts-output-dir>/context-<timestamp>.md
App-context artifact path: <artifacts-output-dir>/app-context-<timestamp>.md
```

Wait for completion. The agent returns the services list as a markdown response.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/services-<timestamp>.md` using the `Write` tool.

---

## Task 4: Build test cases _(blockedBy: Task 2)_

Dispatch `test-planner` with:

```
Context artifact path: <artifacts-output-dir>/context-<timestamp>.md
App-context artifact path: <artifacts-output-dir>/app-context-<timestamp>.md
```

Wait for completion. The agent returns the test cases as a markdown response. The response begins with the `## Test Cases` heading.

**Persist artifact**: Write the agent's response text verbatim to `<artifacts-output-dir>/test-cases-<timestamp>.md` using the `Write` tool.

---

## Task 5: Compose test plan _(blockedBy: Tasks 3 and 4)_

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

Shut down `context-gatherer`, `code-explorer`, `service-mapper`, and `test-planner`. Standing teammates (`service-manager`, `test-runner`) remain.

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

- **No**: shut down remaining teammates, delete team, tell user the test plan path. Stop.
- **Yes**: continue.

If `--confirm` was not set, print: "Test plan complete — proceeding to test execution." and continue immediately.

---

## Task 6: Verify environment health _(blockedBy: Task 5)_

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

## Task 7: Execute tests _(blockedBy: Task 6)_

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

Read `abort_reason` from `<artifacts-output-dir>/test-results-<timestamp>.json`, surface it to the user as the run outcome, and skip Task 8 (there are no cases to report). Proceed directly to Shutdown.

### complete

Capture the totals from the merge stdout line for the Shutdown summary, and proceed to Task 8. The canonical `test-results-<timestamp>.json` is already written.

---

## Task 8: Compile report _(blockedBy: Task 7)_

This is pure team-lead work, no agent dispatch. Read the `## Required Services` line from `<artifacts-output-dir>/test-plan-<timestamp>.md` to form the services-tested string and the primary base URL, then run the render script:

```
<plugin>/skills/compiling-test-report/scripts/render_report.py \
  --results <artifacts-output-dir>/test-results-<timestamp>.json \
  --template-dir <plugin>/skills/compiling-test-report/templates \
  --output <artifacts-output-dir>/report-<timestamp>.html \
  --plan-name "<input value>" \
  --date "<timestamp>" \
  --slug "<slug>" \
  --services-tested "<services with ports, e.g. web (8080)>" \
  --base-url "<primary test URL, e.g. https://localhost:8080>"
```

where `<plugin>` is `${CLAUDE_PLUGIN_ROOT}`. The script writes `report-<timestamp>.html` directly. If it exits non-zero, surface its stderr to the user as a report-generation failure and proceed to Shutdown.

---

## Shutdown

Shut down remaining teammates (`service-manager`, `test-runner`). Delete team `pwt-<run-id>`.

Present final summary:

```
Test run complete for <input value>

Test plan: <artifacts-output-dir>/test-plan-<timestamp>.md
Report (HTML): <artifacts-output-dir>/report-<timestamp>.html

Results: <N> total | <N> passed | <N> passed (adaptive) | <N> failed | <N> errored
```
