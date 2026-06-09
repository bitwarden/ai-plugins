---
name: build-test-cases
description: Build structured Playwright test cases for Bitwarden web changes. Use when you have plan context (file paths, acceptance criteria, UI flows) and need to define starting URLs, interaction sequences, and screenshot checkpoints. Labels external trigger steps (flows initiated by external systems like the marketing website) so they are visible at approval time. Returns a test case list.
---

Given the plan context and Application Context (from `exploring-application-context`), build concrete test cases for Playwright execution.

## Prerequisite: Application Context

This skill must receive an `## Application Context` section in the prompt, produced by the `exploring-application-context` skill. The Application Context contains exactly two top-level sections: `## States` and `## Flows`. Use it to ground every test case in the actual codebase:

- **Starting URLs** come from a state's `UI projection > Route` line. Do not infer URLs from Jira descriptions.
- **Setup sequences** come from `## Flows` entries — each flow declares a `Precondition state:` and `Post-condition state:`, and the planner chains flows by matching post-conditions to required preconditions.
- **Assertions** come from a state's `UI projection > Verification points`. Each verification point identifies the state; assert it exactly as the Application Context records it — a text-content point by its resolved text (not a container class or `data-testid`), a structure/state point by its selector.

If no Application Context is present, return an error asking the caller to run `exploring-application-context` first.

## Tool Policy

Read `${CLAUDE_PLUGIN_ROOT}/references/tool-policy.md` for the complete four-category tool policy. Apply it throughout test case construction — every step you generate must fall into one of the four categories, Category 3 steps must carry the EXTERNAL TRIGGER label defined in the policy, and no step may write to Stripe or query the database directly.

The mailcatcher reader script is at `${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read-mailcatcher.sh`. Use this absolute path verbatim in any setup step that reads email.

## Admin Portal

The Bitwarden Admin portal at `http://localhost:62911` is a legitimate application UI for administrative test setup — creating discount records, managing subscription state, verifying users. Use it instead of direct Stripe API calls or database manipulation when it supports the entity you need.

## Setup Steps

Any test case that creates a user account must write the exact email address into the SETUP step. Use the format `testuser-s<N>-<YYYYMMDDHHMMSS>@example.com` where `<N>` is the test case number and `<YYYYMMDDHHMMSS>` is a timestamp generated at plan-writing time. Never use a generic placeholder or reuse the same address across test cases in the same run.

Before writing any setup steps or test step sequences, read the Application Context's `## States` and `## Flows` sections. For each test case:

1. **Identify the precondition state slug** the test requires (e.g., `state:authenticated-premium-user`). Find a flow in `## Flows` whose `Post-condition state(s)` includes that slug, and inline its atomic steps directly into the test case's Setup Steps. If a chain of flows is needed (e.g., signup → purchase-premium), inline each in order.
2. **For test exercise:** find a flow whose Steps exercise the UI the test verifies → compose its steps inline with assertions inserted at the matching step's inline `- Feedback:` sub-item.
3. **For test-case-specific steps that don't fit a named flow:** write them inline in the test case's Setup Steps list, intermixed with inlined flow steps as needed.

**If the required precondition state has `Reachable by playwright: no`:** read its `Reach via:` recipe and inline each recipe line as a step in the test case. Preserve `[HUMAN]` markers verbatim. Expand any nested `Run flow:<slug>` invocations to their atomic steps (with parameter substitution baked in at plan-write time) — the test plan does not contain a shared flow definitions section, so all steps must be self-contained.

  **Step placement.** Place the recipe lines at the point in the test case where the state transition occurs:
  - **Setup Steps** when the unreachable state is the test's precondition (most common — the recipe drives the application *into* the state before the Test Steps assert it).
  - **Test Steps** when the unreachable state is produced or driven through as part of the test exercise.

  Make the placement decision at plan-write time based on the test's intent. Do not duplicate recipe steps in both sections.

Repetition is acceptable. If the same multi-step sequence appears in two or more test cases, inline it in each — the test plan is generated, not maintained, so DRY across test cases isn't a goal.

Only write setup steps from scratch when no named entry in `## Flows` covers the required precondition. In that case, use the Application Context's `## States` entries (routes, verification points) to identify the right mechanism and break it into individual atomic actions (navigate, fill, click, wait for response).

`Setup Steps:` is mandatory whenever the precondition state requires any of:
- Navigating the Admin portal to create/import records (e.g., subscription discounts, organization seats) — typically uses `flow:authenticate-admin-portal` plus inline admin actions
- Querying Stripe for coupon/discount IDs (Category 4 read-only calls)
- Creating a user account or registering a new organization — typically `flow:create-new-user-and-login`, optionally followed by `flow:purchase-premium-subscription` or `flow:create-paid-org`
- Purchasing a subscription or plan upgrade via the web vault checkout flow

For these cases, every action needed to reach that state must appear as a numbered `SETUP:` step. The executor will run these steps before the Test Steps begin.

If no precondition requires active setup (e.g., the test case tests a page that is visible to any authenticated user without prior state changes), omit the `Setup Steps:` block entirely.

## Test Case Construction

For each test case, define:
1. **Starting URL** — from Application Context
2. **Sequence of interactions** (click, fill, navigate, assert)
3. **Pass/fail criteria** — what constitutes a pass vs. a failure
4. **Descriptive name** — used in the report

Be specific:
- **Good (interaction)**: "Navigate to `https://localhost:8080/#/vault`, click the '+ New Item' button"
- **Good (assertion)**: "Assert: `[data-testid='discount-section']` — exactly 2 elements | Fail: 0 elements found (server may not be returning Discounts array)"
- **Bad**: "Verify discounts are shown"

**Exploit the Application Context fully.** Every step and assertion must be grounded in the specific details the Application Context provides — do not paraphrase or generalize when exact information is available:

- **Interaction steps**: Use the exact URL from "UI projection > Route." Name the specific button label, form field, or control. Don't write "fill in payment details" — write "fill the Stripe card number iframe (`[title='Secure card number input frame']`) with `4242424242424242`."

- **Assertion steps**: Use the exact `Selector value` and `Selector type` from "UI projection > Verification points" — a `data-testid`, CSS selector, element role, or `text`. When the observable is **text content** (a message, a localized or computed term, a relabeled control — anything whose point is that the right text renders), the verification point's `Selector type` is `text`: assert the resolved text substring. When the substring is short or could occur elsewhere on the page, keep `Selector type: text` but scope the read to the nearest stable region named in the point's `Source:` rather than searching the whole page; the region only bounds the search and is never the asserted value (never a container class or `data-testid`). When the observable is **structure/state** (count, visible/hidden, enabled/disabled, element presence), assert via the selector. Each assertion must state:
  1. The selector or text being queried (e.g., `[data-testid="discount-section"]`, or text `"A cohort with this name already exists."`)
  2. The expected count, text, or state (e.g., "exactly 2 elements", "text contains '-$5.00'")
  3. What a failure looks like (e.g., "0 elements — server not returning Discounts array")

- **All verification points must appear**: Every item under "UI projection > Verification points" in the Application Context must map to at least one explicit assertion step. If a verification point has no corresponding assertion, the test case is incomplete.

**Interactive elements must be exercised.** When the plan describes collapsible sections, accordions, tabs, expandable cards, or modal triggers, each must have a dedicated step that:
1. Performs the interaction (click to expand, open tab, trigger modal)
2. Asserts the content *inside* is correct

Verifying that a header or trigger is visible is not sufficient — the hidden content must also be verified.

**Realistic user paths only.** Every step must be something a real user can do through the UI. A test case may **not** use a DOM bypass — writing to a hidden or disabled field, or otherwise bypassing the form's own change handlers — to construct a precondition. If a scenario can only be staged that way, it is not a valid test case — drop it. (Example of an invalid case: filling a coupon field that the form hides and blanks in the current state — the field is not user-editable, so there is no real user path to that input.)

**Assert states only as the Application Context licenses them.** Build assertions solely from the verification points the Application Context records for a state. Do not synthesize a new initial-state or default-state assertion by re-interpreting a conditional. If the context records "element hidden when X" but does not record "element hidden on initial load," do not assert the initial-load case — the default branch may not satisfy the condition. If the context did not record a point as observable in a state, do not assert it visible in that state.

**No un-grounded test cases.** Every test case must trace to a state, flow, or verification point in the Application Context — its Starting URL, steps, and assertions all come from what the context records. Do not invent a test case for a behavior the context does not model, and do not guess a selector, URL, or query parameter the context did not provide. If a behavior that should be tested is not modeled in the Application Context, surface it as a gap — add a `Notes: Coverage gap — <behavior> not modeled in the Application Context` line on the test case whose scenario is closest to the missing behavior, so a reviewer can spot it for a follow-up context pass.

## Billing Prerequisites Check

Scan the plan's features, acceptance criteria, and file paths for billing signals:
- Billing operations: subscriptions, Secrets Manager add-on, plan upgrades, payment methods
- API endpoints containing `subscribe`, `billing`, `payment`, `upgrade`, or `secrets-manager`
- UI flows navigating to billing settings, subscription pages, or Secrets Manager enablement

If any match, read
`${CLAUDE_SKILL_DIR}/references/billing-test-data.md`
before constructing any billing-related test cases, and incorporate the Stripe card numbers,
iframe selectors, and discount eligibility details directly into the relevant test-case steps.

## Output

Emit a single markdown document with this exact structure. The first non-empty line must be the `## Test Cases` heading — downstream agents anchor on it positionally and shape-validate the response.

```
## Test Cases

<one block per test case, see Test Cases format below>
```

Do not preface this document with any narrative or commentary. The entire output is the artifact, beginning with `## Test Cases`.

**Test Cases format** — one block per test case:

```
**Test Case N: <name>**
- Starting URL: <exact URL from a state's UI projection Route in the Application Context>
- Precondition: <one-line summary of the required end-state in plain English (e.g., "A premium user with two active discounts is logged in")>
- Setup Steps:
  1. SETUP: <atomic browser interaction, navigation, fill, or click>
  2. SETUP: [HUMAN] <description of the human action required, e.g. "Attach a Stripe test clock to the subscription">
  3. SETUP: Use the <skill-name> skill to <task>
  4. SETUP: Inspect <path> for <pattern>
  ...
- Test Steps:
  1. <atomic browser interaction or navigation>
  2. Assert: <selector> — <expected value/count/state> | Fail: <what failure looks like>
  3. [HUMAN] <description of the human action required, when the test exercise itself includes one>
  ...
- Notes: <optional free-form notes>
```
