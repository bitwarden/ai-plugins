# ## Example 2: CLAUDE.md Review - Duplication Issue

**Context:** Reviewing CLAUDE.md that duplicates architecture documentation.

### Review Comments

**`.claude/CLAUDE.md:50-250`** - IMPORTANT: Duplicates docs/ARCHITECTURE.md content

This section copies 200 lines of MVVM patterns, Hilt DI setup, and module organization from `docs/ARCHITECTURE.md`.

Replace with reference:

```markdown
## Core Directives

1. **Adhere to Architecture**: All code MUST follow patterns in `docs/ARCHITECTURE.md`
2. **Follow Code Style**: ALWAYS follow `docs/STYLE_AND_BEST_PRACTICES.md`
3. **Error Handling**: Use Result types and sealed classes per architecture guidelines

## Reference Documentation

Critical resources:
- `docs/ARCHITECTURE.md` - Architecture patterns and principles
- `docs/STYLE_AND_BEST_PRACTICES.md` - Code style guidelines

**Do not duplicate information from these files - reference them instead.**
```

Rationale: CLAUDE.md should provide high-level directives and references, not duplicate detailed specs. This:
- Reduces token usage (200 lines → 10 lines)
- Prevents documentation drift (single source of truth)
- Improves maintainability

Reference: Progressive disclosure, DRY principle

---

**`.claude/CLAUDE.md:300`** - SUGGESTED: Add decision-making guidance

Consider adding clear guidance on when to ask vs proceed autonomously:

```markdown
## Decision-Making

Defer to user for high-impact decisions:
- Architecture/module changes
- Public API modifications
- Security mechanism changes

Proceed autonomously for:
- Implementation details within established patterns
- Test additions
- Bug fixes following existing patterns
```

This helps Claude make appropriate judgment calls without over-asking or under-asking.

---

### Summary Comment

**Overall Assessment:** REQUEST CHANGES

**Must Fix (IMPORTANT):**
- Remove duplicated architecture content, replace with references

This reduces token usage by ~80% while improving maintainability. The rest of the file is well-structured.

---

