---
name: avoiding-false-positives
description: Use this skill to validate findings during a code review. For each finding, run the rejection criteria and verification checks. If a finding fails any check, drop it.
---

# Validating Findings

## Rejection Criteria

A finding is a false positive — **drop it** — if ANY of the following are true:

- **Pre-existing** — code existed before this PR and was not modified by this change
- **Not actually buggy** — appears wrong but is correct (e.g., variable IS defined, logic DOES produce correct results)
- **Pedantic nitpick** — a senior engineer would not flag this in a real review
- **Linter-catchable** — a linter or type checker will catch this; do not duplicate their work
- **Generic concern** — "lacks test coverage", "general security issue" without a specific, traceable problem
- **Explicitly silenced** — lint ignore comments, pragma suppressions, or documented exceptions
- **Handled elsewhere** — error boundaries, middleware, validators, or framework guarantees make the issue moot

## Verification Checks

For each finding that passes rejection criteria, verify ALL three:

1. Can you trace the execution path showing incorrect behavior?
2. Is this handled elsewhere (error boundaries, middleware, validators)?
3. Are you certain about framework behavior, API contracts, and language semantics?

**If you cannot confidently answer all three, drop the finding.**

## Patterns to Recognize (DO NOT flag)

1. **Intentional simplicity** - Not every function needs error handling if caller handles it
2. **Framework conventions** - React hooks, dependency injection, ORM patterns have specific rules
3. **Test code** - Different standards apply (hardcoded values, no error handling often OK)
4. **Generated code** - Migrations, API clients, proto files (only review if hand-edited)
5. **Copied patterns** - If code matches existing patterns in codebase, consistency > "better" approach

**When uncertain about a pattern, search the codebase for similar examples before flagging.**

## Codebase Conventions

1. **Check existing patterns** - How does this codebase handle similar cases?
2. **Respect established conventions** - Even if non-standard, consistency > perfection
3. **Don't flag convention violations** unless they cause bugs or security issues

**Examples:**

- Codebase uses `any` types extensively → Don't flag individual uses
- Codebase has no error handling in services → Don't flag one missing try-catch
- Consistency matters more than isolated improvements

## Common False Positives

**Do NOT flag when handled elsewhere or guaranteed by framework:**

- **Null checks**: Language/framework ensures non-null, or prior validation occurred
- **Error handling**: Error boundaries exist, function designed to throw, or caller handles
- **Race conditions**: Framework synchronizes (React state, DB transactions), or operations idempotent
- **Performance**: Data bounded (<100 items), runs once at startup, no profiling evidence
- **Security**: Framework sanitizes (parameterized queries, JSX escaping), or API layer validates

**When uncertain, assume the developer knows something you don't.**
