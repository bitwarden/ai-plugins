# Context

Provide necessary background without overwhelming with information.

---

## Definition

Provide necessary background without overwhelming with information.

## Good Context

✅ **SUFFICIENT CONTEXT:**
```markdown
## Progressive Disclosure

Anthropic recommends keeping main skill files under 500 lines. This improves token efficiency and loading performance.

Split larger skills into:
- Main orchestration file (routing logic)
- Supporting files (detailed guidance)
- Load supporting files on-demand
```

✅ **RELEVANT BACKGROUND:**
```markdown
## Structured Thinking

Research shows Chain of Thought prompting with `<thinking>` tags reduces logic errors by 40% (Anthropic, 2024).

Use structured thinking blocks before major decisions:
[example]
```

## Poor Context

❌ **CONTEXT OVERLOAD:**
```markdown
[10 paragraphs of LLM history and theory before getting to actual instructions]
```

❌ **NO CONTEXT:**
```markdown
Use progressive disclosure.

[No explanation of what that means or why]
```

## Context Guidelines

**Include:**
- Why this matters (rationale)
- When to apply (triggers)
- Research backing (if applicable)
- Brief background for unfamiliar concepts

**Exclude:**
- Tangential information
- Exhaustive background
- Information already known
- Redundant explanations
