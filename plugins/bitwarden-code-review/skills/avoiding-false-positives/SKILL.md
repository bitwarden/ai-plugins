---
name: avoiding-false-positives
description: Use this skill when validating ANY potential code review finding. Apply BEFORE classifying to verify the finding is real; can you trace incorrect behavior, is it handled elsewhere, and are you certain about framework semantics? If any answer is no, DO NOT create the finding.
---

# Avoiding False Positives

## Before Flagging Anything

**MUST verify ALL three:**

1. Can you trace the execution path showing incorrect behavior?
2. Is this handled elsewhere (error boundaries, middleware, validators)?
3. Are you certain about framework behavior, API contracts, and language semantics?

**If you cannot confidently answer all three, DO NOT create the finding.**

## Patterns to Recognize (DO NOT flag)

1. **Intentional simplicity** - Not every function needs error handling if caller handles it
2. **Framework conventions** - React hooks, dependency injection, ORM patterns have specific rules
3. **Test code** - Different standards apply (hardcoded values, no error handling often OK)
4. **Generated code** - Migrations, API clients, proto files (only review if hand-edited)
5. **Copied patterns** - If code matches existing patterns in codebase, consistency > "better" approach

**When uncertain about a pattern, search the codebase for similar examples before flagging.**

## Codebase Conventions

**Before suggesting changes:**

1. **Check existing patterns** - How does this codebase handle similar cases?
2. **Respect established conventions** - Even if non-standard, consistency > perfection
3. **Don't flag convention violations** unless they cause bugs or security issues

**Examples:**

- Codebase uses `any` types extensively → Don't flag individual uses
- Codebase has no error handling in services → Don't flag one missing try-catch
- Consistency matters more than isolated improvements

## Common False Positives to Avoid

**Do NOT flag when handled elsewhere or guaranteed by framework:**

- **Null checks**: Language/framework ensures non-null, or prior validation occurred
- **Error handling**: Error boundaries exist, function designed to throw, or caller handles
- **Race conditions**: Framework synchronizes (React state, DB transactions), or operations idempotent
- **Performance**: Data bounded (<100 items), runs once at startup, no profiling evidence
- **Security**: Framework sanitizes (parameterized queries, JSX escaping), or API layer validates

**When uncertain, assume the developer knows something you don't.**
