---
name: classifying-review-findings
description: Classifies code review findings into severity categories (CRITICAL, IMPORTANT, DEBT, SUGGESTED, QUESTION) following Bitwarden standards. Use when determining severity levels, categorizing PR comments, deciding what emoji to use, or verifying if something should be flagged at all.
---

# Classifying Review Findings

## Severity Categories

| Emoji | Category  | Criteria                                                                       |
| ----- | --------- | ------------------------------------------------------------------------------ |
| ❌    | CRITICAL  | Will break, crash, expose data, or violate requirements                        |
| ⚠️    | IMPORTANT | Missing error handling, unhandled edge cases, could cause bugs                 |
| ♻️    | DEBT      | Duplicates patterns, violates conventions, needs rework within 6 months        |
| 🎨    | SUGGESTED | Measurably improves security, reduces complexity by 3+, eliminates bug classes |
| ❓    | QUESTION  | Requires human knowledge - unclear requirements, intent, or system conflicts   |

**ALWAYS** use hybrid emoji + text format for each finding (if multiple severities apply, use the most severe: ❌ > ⚠️ > ♻️ > 🎨 > ❓):

## Before Classifying

Verify ALL three:

1. Can you trace the execution path showing incorrect behavior?
2. Is this handled elsewhere (error boundaries, middleware, validators)?
3. Are you certain about framework behavior and language semantics?

**If any answer is "no" or "unsure" → DO NOT classify as a finding.**

## Not Valid Findings (Reject)

- Praise ("great implementation")
- Vague suggestions ("could be simpler")
- Style preferences without enforced standard
- Naming nitpicks unless actively misleading
