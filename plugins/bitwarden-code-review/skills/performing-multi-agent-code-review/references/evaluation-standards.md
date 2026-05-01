# Evaluation Standards

Loaded by the orchestrator in Step 1. **Severity Levels** and **Confidence Scoring** below are propagated verbatim into every Step 2–5 subagent prompt. The **Finding Shape** schema lives in `finding-shape.md` and is propagated the same way.

## Severity Levels

Every finding must be assigned one of the following. Do not guess — apply these definitions literally.

- 🛑 **Blocker** — Will cause a production failure, data loss, or security breach.
- ⚠️ **Important** — A real bug or significant risk that is likely to be hit in practice.
- ♻️ **Refactor** — True technical debt being created that will cost more to maintain over time, even if it doesn't cause immediate problems.
- 💡 **Suggestion** — Code structure or quality issue that makes the code harder to maintain or understand than necessary.

## Confidence Scoring

Rate each potential finding on a 0–100 scale:

- **0**: Not confident — false positive or pre-existing issue.
- **25**: Somewhat confident — might be real, might be a false positive. Stylistic issues not called out in project guidelines land here.
- **50**: Moderately confident — real issue, but a nitpick, unlikely to hit in practice, or is a stylistic preference without project-rule backing.
- **80**: Highly confident — verified; very likely to hit in practice. Directly impacts functionality or violates a project guideline.
- **100**: Certain — evidence directly confirms it will happen frequently.

**Only report findings with confidence ≥ 80.** Findings rated 50–79 are dismissed silently; do not re-rate upward to clear the threshold.

## Finding Shape

Every finding and every Step 4/5 return object follows the JSON schema in `finding-shape.md`. The main orchestrator loads that file in Step 1 and propagates its contents verbatim to every subagent.
