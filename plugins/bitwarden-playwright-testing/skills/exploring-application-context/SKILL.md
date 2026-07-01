---
name: exploring-application-context
description: Explore the Bitwarden codebase (clients and server) to build a state-centric Application Context for test planning. Use before building test cases whenever a Jira ticket or plan is provided. Returns a markdown document with two sections — ## States (real-user-reachable, observable UI conditions with their verification points) and ## Flows (sequences that transition between states) — grounded in real client and server code.
---

Given the affected repos, feature description, and acceptance criteria, build a state-centric Application Context by exploring the codebase. This is what `build-test-cases` consumes to generate grounded, accurate test cases.

The artifact is a contract: every state the planner can ask the application to be in, the flows that put it there, and the UI projections it can assert. Information that does not serve that contract is out of scope.

Model what a **real user can reach and observe** — not every selector in the blast radius. Scale your effort to the change: model the minimal set of states needed to assert the change and its acceptance criteria, then stop. Minimal does not mean partial — the target states should *span* the change's blast radius (the observable behaviors the diff touches), not only the headline symptom. Cover every observable behavior the change introduces or modifies, and stop there: the diff is the boundary, so this is not a license to model behaviors the change does not touch.

## Gathering procedure

Read `${CLAUDE_SKILL_DIR}/references/known-flows.md` once before gathering states and flows. It holds two pre-grounded catalogs — `## Known States` (reusable setup states) and `## Known Flows` (reusable flows) — that both sections below draw from; copy relevant entries verbatim rather than re-deriving them.

### Gather the blast radius

For each affected repo passed in by the calling agent, run:

```bash
git diff origin/main...HEAD --name-only -- <repo-path>
```

Read the change set. For each changed component, controller, command, or template, trace the handlers and templates it references to identify the **trace surface** — non-diff code you need to read to identify states and flows. The change set and trace surface together form the blast radius. The blast radius is working context only — do not emit it.

### Gather `## States`

States come in two tiers:

- **Target state** — a state the change *produces or modifies*, and that a test asserts against. Model these fully (route + verification points), applying the validity gates below.
- **Setup state** — a state that only *positions* the app for the test (a precondition or a generic authenticated context); never the assertion target. Satisfy a setup state one of two ways:
  - **Catalog copy:** if the state appears under `## Known States` in the catalog, copy its entry verbatim. Do not re-ground it.
  - **Route-only:** otherwise, declare it with its `Route` and a single landmark check confirming the page loaded.

A state is a **target** state if and only if it is the post-condition of a *change-driven* flow — one you traced from the diff. Every state referenced as a precondition or post-condition of a *copied catalog flow* is a **setup** state.

#### Validity gates — apply as you mint each state and verification point

Before recording any state or verification point, confirm all three. If one fails, drop it from the artifact — remove the state *and* its producing flow. Recognizing a failure in prose is not enough: never emit a failed-gate state with a disclaimer that it isn't really reachable; delete it.

1. **Actually observable.** Assert only what a user would *see* in this state. An element present in the DOM but hidden — by the `hidden` attribute, `display:none`, a collapsed/accordion container, an unsatisfied `@if`/`*ngIf`, or any framework's equivalent — is not observable. Reason about the state's real rendered condition in whatever framework renders it (Angular client or server-rendered Razor).
2. **Correct branch / default.** When behavior is conditional, identify which branch is live in the state you are modeling. For an initial or landing state, check the actual default value that drives the condition, and assert only that branch. Never promote a conditional rule ("hidden iff churn-only") into a default-state assertion ("hidden on load").
3. **Requirement-anchored.** Assert what the change and the acceptance criteria require. Do not invent expectations the code never promises and no criterion asks for.

#### Recording a target state

- **Slug.** Choose a kebab-slug that encodes distinguishing features when near-neighbor states exist; never reuse a user-intent label across distinct states (e.g. `state:subscription-pending-cancellation` vs. `state:subscription-pending-cancellation-with-deferred-price-schedule`).
- **Route.** The Angular route or full URL the planner navigates to to assert this state.
- **Verification points.** Record the points that identify this state. For each point: Selector value, Selector type, Expectation, and a `Source:` citation (`file:line`) for where the asserted element or message is defined. **The first grounded, observable selector that identifies the state wins.** If observability in this state depends on a gate (a collapsed container, a conditional), note that gate in prose in `Source:`. If the gate is unsatisfied in this state's landing condition, the point is not observable here (gate 1) — choose a different point, or model the state as the condition in which the element *is* observable and have its producing flow drive into that condition.
- **Choose the assertion basis by what you are observing — text content vs. structure/state.**
  - **Text content.** When the verification is that some *text* renders correctly — a validation error, toast, banner/callout, a localized or runtime-computed term (e.g. `/ 年`), a relabeled control, any case where "is the right text on screen?" is the question — the verification point **must use `Selector type: text`**, with the text substring as the Selector value. A `text contains "..."` expectation may **not** be grounded on any structural selector (`data-testid`, `tag`, `role`, or `css`). Collision-safety comes from a **distinctive substring**, not a structural selector — assert the longest literal substring that excludes placeholder tokens and cannot match elsewhere on the page (e.g. `Churn-only cohorts cannot have a proactive discount coupon.`, not a short fragment). If no distinctive substring exists — a short localized unit or computed term like `/ 年` has none — keep `Selector type: text` and name its nearest stable container in `Source:` so the read can be scoped there; the container only bounds the search, it never becomes the assertion basis. Only assert text the change affects.
  - **Structure / state.** When the verification is a non-text property — element count, visible/hidden, enabled/disabled, the presence of a structural element — assert via the **selector + `Expectation`**. This is where a `data-testid`/role selector is the right assertion basis. A hyphenated tag (`bit-select`, `bit-input`, `bit-radio-*`) is a Bitwarden component, not native HTML, and does not render as its namesake — never ground on `<tag>#id` (e.g. `select#locale`); use its `role` (a `bit-select` renders as a combobox) or a stable `data-testid`.
- **Reachability.** Every state declares `Reachable by playwright:`. Set it to `yes` if a producer flow or mechanism can drive the application into this state using only the playwright-cli skill. Otherwise set it to `no` and add an **`If no — why:`** one-liner and a **`Reach via:`** recipe describing the sanctioned out-of-band action (a `[HUMAN]` step, a database row a sanctioned tool inserts, or a non-playwright skill) that reaches it.
- **Producers.** Leave `**Produced by:**` lines in place; fill them in after `## Flows` is gathered.
- **Flag-conditional UI variants fan out into separate states** with distinct slugs, not one state with conditional verification points.

#### Reach via conventions

For states with `Reachable by playwright: no`, the `Reach via:` recipe documents how the team-lead or user can drive the application into the state using tools beyond playwright-cli. Free-form prose with these conventions:

- **Reference flows by slug:** `Run flow:create-paid-org with orgName=…`
- **Reference skills by name:** `Use the invoke-stripe-api skill to advance the test clock by 14 days.`
- **Mark human steps explicitly:** `[HUMAN] Attach a Stripe test clock to the subscription.` The bracketed `[HUMAN]` prefix is a structural marker — downstream consumers detect it deterministically.
- **Mark `[HUMAN]` verification points the same way:** when confirming a state requires a check the tool policy disallows (a database-field inspection, or any verification playwright cannot perform), record it as a verification point prefixed with `[HUMAN]`.

### Gather `## Flows`

1. From the catalog's `## Known Flows` section, copy relevant entries through verbatim if their post-condition state matches a state in `## States`, OR their precondition/steps exercise UI affected by the change. (Setup states their preconditions reference are minted in `## States` via catalog copy or route-only, per Gather `## States` above.)
2. **Token resolution:** When copying any flow whose Steps contain `<bitwarden-portal-admin-email>`, read `server/dev/secrets.json` in the server repo and extract the first entry under the `admins` key. Substitute the resolved address for every occurrence. If the file is absent or `admins` is empty, surface this as a self-review error — do not leave the placeholder unresolved.
3. For change-driven flows not in the catalog: trace the click handler or form submission through the server controller, command, and integration calls. Enumerate atomic steps, inline per-step feedback (a `- Feedback:` sub-item on each step that produces a visible response), post-condition state, and any branch conditions. Every step must be a real user interaction.
4. After flows are populated, return to `## States` and fill in each state's `**Produced by:**` line with the slug(s) of the flow(s) whose post-condition is that state.

Every flow obeys these rules:

- **Each flow has exactly one terminal state per branch.** Split multi-stage journeys into one flow per state transition.
- **Producing flows must reveal their post-condition's gated elements.** If a target state has a verification point whose element is hidden by default, the flow's Steps must include the reveal interaction, and that step's `- Feedback:` sub-item must state that the gated element becomes visible.
- **`When <condition>:` is free-form prose** (flag conditions or runtime conditions). If the planner can't evaluate the condition at plan time, it picks Default.

## Output schema

Produce a single markdown document with exactly two top-level sections, in this order: `## States` then `## Flows`. No other top-level sections.

### `## States`

For each state:

```
### state:<short-kebab-slug>

**State type:** target | setup

**Produced by:**
- flow:<slug>
- <one or more producer flows; if none, the state is reachable out-of-band (see Reach via:), in which case write `none`>

**Reachable by playwright:** yes | no
**If no — why:** <one line>  (only when "no")
**Reach via:**  (only when "no")
- <numbered recipe — see Reach via conventions>

**UI projection:**
- Route: <URL>
- Verification points:
  - Selector: <selector value>
    - Selector type: tag | data-testid | role | text | css  (text-content points must use `text`; structure/state points use a structural type)
    - Expectation: <visible | hidden | disabled | text contains "..." | count = N>
    - Source: <file:line where the element/message is defined; note in prose any gate affecting observability in this state>
```

### `## Flows`

For each flow:

```
### flow:<short-kebab-slug>

**Use when:** <one-sentence summary>
**Parameters:** <comma-separated placeholder names, or "none">
**Precondition state:** state:<slug> | "none"
**Steps:**
1. <atomic UI action with selector and value>
   - Feedback: <visible response — only on steps that produce one>
2. ...
**Post-condition state(s):**
- Default: state:<slug>
- When <condition>: state:<slug>  (only when post-condition branches)
```

## Producing the document — work in notes, serialize once

Do all reasoning in working notes as you explore: accumulate states and verification points, applying the validity gates as you mint each one. **Do not write out the full `## States` / `## Flows` document as an intermediate step.** The complete document appears for the first and only time as your final response — it is a serialization of notes you have already validated, not a draft you revise.

### Terminal self-review (one read-only pass over your notes)

Run these checks once, against your notes, just before serializing. They are read-only — do not re-read source files, and do not re-open a state you have already validated.

1. **Slug resolution.** Every `Precondition state:` and `Post-condition state:` slug exists as a `### state:<slug>` heading. Every `Produced by:` slug exists as a `### flow:<slug>` heading.
2. **Parameter coverage.** Every parameter declared on a flow appears as a `<placeholder>` in its Steps, and every `<placeholder>` in Steps is declared in Parameters.
3. **Target-state completeness.** Every target state has at least one observable verification point.
4. **Text-content selector basis.** Every verification point whose `Expectation` is `text contains "..."` has `Selector type: text` — never a structural selector (`data-testid`, `tag`, `role`, or `css`).

On any failure, surface the inconsistency in your return — do not self-fix by re-opening exploration.

### Done condition

You are done when every target state has at least one observable verification point and every referenced slug resolves. When that holds, serialize the document once and stop.
