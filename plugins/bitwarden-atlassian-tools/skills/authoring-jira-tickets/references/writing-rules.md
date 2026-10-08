# Writing Rules

Apply these rules while drafting — not as a cleanup pass afterward. Tickets that are tight from the start are easier to review and easier to act on.

---

## Principle 1: One fact, one place

Every fact lives in exactly one section. If two sections would say the same thing, drop it from the second.

**Rules:**

- **Purpose leads with what this ticket covers.** It does not restate what lives in sibling tickets, the parent epic, or the broader feature. State only what this ticket delivers.
- **Decisions and trade-offs belong in one place.** Product or design decisions go in Questions and Answers. Technical or engineering decisions go in Technical Breakdown. Not both.
- **Concrete files and components belong only in Technical Breakdown.** Do not list files in Scope and again in Technical Breakdown. Pick one — and it should be Technical Breakdown.
- **Out of Scope belongs in Acceptance Criteria, not duplicated in Scope.** If a team convention moves Out of Scope, follow it — but do not put the same items in two places.

---

## Principle 2: Write for behavior, not implementation

Tickets describe what the user or system should **do**, not how the code does it. Implementation is owned by the pull request and changes over time. The ticket must stay readable for QA, product, and design after the code is written.

**Rules:**

- **Code identifiers only in Technical Breakdown.** Function names, class names, component names, file paths, and type names do not belong in Description, Acceptance Criteria, Scope, or Scenarios. If a criterion cannot be stated without naming a function, restate it as the observable behavior.
- **Technical Breakdown captures intent, not steps.** Write what the implementation must accomplish and why — constraints, trade-offs, non-obvious decisions. Point to where the behavior lives with real links. The PR owns the how; the ticket owns the why.
- **Describe the broad outcome, not a single granular case.** "The report loads when it contains invalid data" is a criterion. "A single application with an empty name is skipped" is a reproduction step for a bug ticket. Granular single-case detail belongs in Bug replication steps, not Scope or Acceptance Criteria.
- **Plain language over technical terms.** Use the words QA, product, and design use: "version" not "envelope"; "data" not "payload"; "shown", "visible", or "appears" not "rendered". When naming a feature flag, use its LaunchDarkly value, not the code enum name.
- **No placeholder scaffolding.** Do not mention hooks, stubs, or empty entry points for work owned by another ticket. That ticket adds its own integration point; placeholders create merge conflicts and drift.
- **Technical Breakdown documents effects, not decisions.** When a decision is pending, document what the implementation requires under each option — cost, constraints, and trade-offs. The decision question lives in Questions and Answers; Technical Breakdown covers what changes depending on which path is taken.
- **Feature flags are assumed for new features.** Do not state the flag in Scenarios or as a Gherkin Background precondition. Record the LaunchDarkly value in the Purpose block only — specifically the flag that gates this ticket's deliverable, not every flag that affects the area. Secondary flags (for example, a structural layout flag) belong in QA Testing Notes if QA must toggle them, or Risks / Considerations if the implementation must account for them.
- **Scope Acceptance Criteria and Scenarios to this increment.** Do not restate general platform behavior that is always true. That is assumed background, not this ticket's criteria.

---

## Principle 3: Cover deliverables, not definitions

A ticket documents the **changes it delivers**, not design definitions or features another ticket delivers.

**Rules:**

- **Reference tickets you depend on.** Include a link and explain the dependency — "builds upon PM-123" when this ticket modifies that ticket's deliverable; "reached from the dialog delivered in PM-123" when this ticket is a distinct new artifact.
- **Do not re-declare another ticket's deliverables.** State only what this ticket changes. If the dialog exists because PM-123 delivers it, this ticket does not need to describe the dialog — only the changes it makes to it.
- **Avoid context-free comparisons.** Do not write "the same as premium" or "unlike the free tier view" without naming and linking the other ticket. State this ticket's behavior as fact; if a comparison is unavoidable, name and link what you are comparing to.
- **Out of Scope bullets name the exclusion only.** Do not append "covered by PM-XXXX" to an Out of Scope item. If a sibling ticket owns the excluded work, add it to the Links metadata field with a "Relates to" relationship — not inline in the bullet.

---

## Style Rules

Apply by default. Override only when the ticket genuinely needs the extra context.

- **No intro sentences before a table or bullet list.** The section header is the intro. Delete "The following table lists…" or "The criteria are…"
- **One sentence per bullet.** If a bullet needs an explanatory follow-on sentence, the bullet itself is probably too vague — rewrite it. Use sub-bullets only when the parent genuinely needs the child to be distinct.
- **Table cells are phrases, not paragraphs.** Pros/cons and trade-off cells should be one short sentence each, ideally under 25 words.
- **No restating across sections.** If the Purpose says X, do not say X again in a later section in different words. Merge or drop.
- **Prefer tables and bullets over prose** for any content that has structure. Reserve prose for context the reader cannot infer from structure.
- **Titles: [Area] imperative verb, outcome.** When the ticket is client-specific, prefix with the area in brackets: `[Web]`, `[Server]`, `[Browser]`, or `[SDK]`. Example: `[Web] Add CSV export to the item list`. Omit the prefix when the ticket is not specific to one client. Not a noun phrase. Not a question. Matches sibling ticket style under the same parent.

---

## Gherkin Rules (Scenarios section)

Scenarios appear only in Story tickets. Follow Cucumber/Gherkin conventions.

**Cover:**

- Primary (happy) path
- User choices that branch the flow
- First-time vs. returning user behavior
- Error and failure states
- Boundary and empty-state conditions

**Rules:**

- Each `Scenario` tests one behavior — not a sequence of unrelated behaviors.
- `Given` sets up context (state, not actions). `When` is the single user action. `Then` states the observable outcome.
- Do not use `Background` for feature flags. The flag lives in the Purpose block only.
- Do not restate general platform behavior as a `Given` or `Then` — that is assumed.
- Scenario names are plain language: `User exports vault items as CSV`, not `Happy path test 1`.
