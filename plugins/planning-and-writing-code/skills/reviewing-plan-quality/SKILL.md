---
name: reviewing-plan-quality
description: Use when evaluating a technical implementation plan against quality criteria. Assesses requirements completeness, Jira alignment, technical approach, parallelization strategy, and clarity. Produces a structured review with severity-rated findings and a verdict.
---

# Reviewing Plan Quality

Assessment criteria for implementation plan quality. Apply each section in sequence against the plan under review.

<thinking>
Before beginning the assessment, establish context:
- Is Jira synthesis available from the researching-jira-issues skill? If so, the Jira alignment sub-section is active.
- What repos and layers does this plan cover (server, clients, database, both)?
- How many stages does the plan have, and does it claim any parallel workstreams?
These answers determine which assessment sections require the deepest scrutiny.
</thinking>

## 1. Requirements Completeness

<thinking>
If Jira synthesis is available, enumerate every acceptance criterion from the ticket explicitly before checking coverage — do not assess coverage vaguely. List each AC first, then check each one against the plan below.
</thinking>

### Jira alignment (if synthesis available)

Compare the plan against the `researching-jira-issues` synthesis output:

- **Acceptance criteria coverage**: For each acceptance criterion in the Jira ticket (from the description, custom fields, or linked Confluence docs), confirm there is a corresponding stage, success criterion, or test case in the plan. Flag any criterion with no coverage.
- **Scope gaps**: Does the plan address everything in the ticket's scope of work? Flag any requirements, sub-tasks, or linked issues that the plan omits without explanation.
- **Out-of-scope work**: Does the plan implement anything not described in the ticket? Flag items that appear to exceed the defined scope.
- **Dependencies honored**: Are blocking issues or prerequisite conditions from the ticket reflected in the plan's stage sequencing?

### Edge cases
- Empty/null inputs — are they addressed?
- Boundary conditions (empty collections, max lengths, zero values)?
- Concurrent or race condition scenarios if relevant?
- Failure of external dependencies (network, database, third-party service)?

### Error handling
- Is error handling described for each operation that can fail?
- Are error messages specific and user-friendly?
- Is the error propagation strategy defined (fail fast vs. graceful degradation)?

### Tests (TDD check)
- Does every stage with testable behavior list specific test cases?
- Are tests ordered before implementation within each stage?
- Do the listed tests cover the stated acceptance criteria?
- Are edge cases and error conditions represented in the test list?
- Are there stages where tests are missing entirely but should exist?

---

<thinking>
Before assessing pattern consistency, identify the specific files to read:
- Which files does the plan say it will create or modify?
- What are 2–3 adjacent or similar files in the same directory or layer?
Name them explicitly before reading any of them. The pattern consistency assessment is only as good as the files chosen for comparison.
</thinking>

## 2. Technical Approach

### Pattern consistency
Read 2–3 adjacent or similar files to the ones the plan modifies. Ask:
- Does the plan's described approach match the conventions in those files?
- Does it use the same dependency injection style, naming conventions, and abstractions already established?
- Flag any cases where the plan would introduce an inconsistent pattern into an area that already has a clear convention.

### Code smells and anti-patterns
Look for descriptions of:
- Methods or classes that take on too many responsibilities
- Deep conditional nesting without a simplification strategy
- Logic that duplicates something already present in the codebase
- Hard-coded values where constants or configuration should be used
- Missing dependency injection (instantiating dependencies directly instead of injecting)
- Shared mutable state across components
- Missing interface/abstraction where the pattern in adjacent code uses one

### Code snippet convention compliance
- Verify that code examples in the plan follow Bitwarden naming, patterns, and idioms for the relevant repo (server C#/.NET or clients Angular/TypeScript).
- Flag any snippets that contradict conventions in the adjacent codebase.

### Architecture concerns
- Is the stage sequence logical? Can later stages start without earlier ones being complete?
- Are there missing stages (e.g., plan adds a model and UI but skips the service/repository layer)?
- Is the separation of concerns maintained across layers?
- For parallel stages: are the pre-agreed contracts (type names, route paths, interface signatures) defined?

### Security
- Is sensitive data (tokens, credentials, PII) handled without logging or exposing it?
- Is user input validated before use?
- Are authorization checks described on operations that require them?

---

<thinking>
Before assessing the plan's parallelization claims, independently map the actual dependency graph:
- What does each stage produce that another stage consumes?
- Which stages share no state and have no hard dependency on each other?
Do not accept the plan's own parallelization claims at face value — verify them against the actual stage outputs and inputs you identified above.
</thinking>

## 3. Parallelization Review

### Missed parallelization opportunities
- Are there stages marked sequential that have no hard data dependency on each other? Flag each pair that could run concurrently.
- Would splitting a large sequential stage into parallel subagent workstreams meaningfully reduce implementation time?

### Incorrect parallelization
- Are any stages marked parallel that actually share a hard dependency (e.g., both write to the same file, one consumes a type the other produces, one registers something the other depends on at runtime)?
- If parallel stages exist, are the **pre-agreed contracts** (type names, file paths, route prefixes, interface signatures) fully defined so subagents can work without waiting on each other? Flag any contract that is missing or underspecified.

### Subagent scope quality
- If subagent scopes are defined, does each one include: the exact files to create/modify, what to read first for context, specific tasks to complete, and any constraints?
- Are any scopes so broad or vague that a subagent would need to make architectural decisions that should be pre-decided in the plan?

### Overall assessment
State one of:
- **Well-parallelized** — the dependency graph is correct and parallelization opportunities are exploited appropriately.
- **Over-sequentialized** — stages that could run in parallel are needlessly serialized; recommend restructuring.
- **Incorrectly parallelized** — stages are marked parallel but have real dependencies that would cause conflicts; recommend making them sequential or defining missing contracts.
- **Not applicable** — the work is inherently sequential with no meaningful parallelization opportunities (state why).

---

## 4. Clarity and Executability

Assess whether a coding agent can execute each step without guessing.

- **Specificity**: Do steps name the exact file, class, and method — or are they vague ("add a method", "update the component")?
- **Completeness**: Does each step specify what to create vs. modify, and where?
- **Unambiguous order**: Can each step be started knowing exactly what precedes it?
- **Undefined terms**: Flag any phrases like "similar to", "as appropriate", "handle accordingly" that require interpretation the plan does not resolve.
- **Missing context**: Are there steps that assume knowledge not stated in the plan?

---

## Review Output Format

Write the review using this exact structure. Omit tables for severity levels with no findings.

```markdown
# Plan Review

**Plan**: [plan file name]
**Reviewed**: YYYY-MM-DD HH:mm
**Verdict**: 🔴 Needs Revision | 🟡 Minor Issues | 🟢 Ready to Write

### Summary

[1–3 sentences describing overall plan quality and primary concerns.]

### Findings

#### 🔴 Critical — must fix before writing code

| # | Location | Issue | Recommended Fix |
|---|----------|-------|-----------------|
| 1 | Stage N, [ClassName] | Described method `Foo.Bar()` does not exist; the actual method is `Foo.BarAsync()` | Replace all references to `Foo.Bar()` with `Foo.BarAsync()` |

#### 🟠 High — likely to cause agent confusion or subtle bugs

| # | Location | Issue | Recommended Fix |
|---|----------|-------|-----------------|

#### 🟡 Medium — reduces risk or improves clarity

| # | Location | Issue | Recommended Fix |
|---|----------|-------|-----------------|

#### 🔵 Low — suggestions only

| # | Location | Issue | Recommended Fix |
|---|----------|-------|-----------------|

### Parallelization Assessment

**Overall**: Well-parallelized | Over-sequentialized | Incorrectly parallelized | Not applicable

[Describe the dependency graph issues or confirm the strategy is sound. List any stages that should be parallelized but aren't, any parallel stages with missing contracts, and any incorrectly parallel stages.]

### Verdict Explanation

[Explain the verdict and what must change before running `/planning-and-writing-code:implement-plan`.]
```

---

## Verdict Rules

<thinking>
Before writing the verdict label, count Critical and High findings from your table, then apply the Verdict Rules below mechanically. Do not assign the verdict intuitively — derive it from the counts.
</thinking>

- 🔴 **Needs Revision**: Any Critical issues present, OR 3 or more High issues
- 🟡 **Minor Issues**: 1–2 High issues or multiple Medium issues, no Critical issues
- 🟢 **Ready to Write**: No Critical or High issues (Medium and Low are acceptable to proceed)
