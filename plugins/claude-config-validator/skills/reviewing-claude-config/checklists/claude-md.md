# CLAUDE.md Review Checklist

Review checklist for changes to CLAUDE.md files at any level (project root, `.claude/` directory, or subdirectories).

**Valid CLAUDE.md Locations:**

- Project root: `/CLAUDE.md` - Global project instructions
- Claude directory: `/.claude/CLAUDE.md` - Claude Code-specific instructions
- Subdirectories: `/path/to/subdirectory/CLAUDE.md` - Scoped instructions for specific modules/components

All locations are valid and serve different scoping purposes. This checklist applies equally to all locations.

---

## Multi-Pass Review Strategy

### First Pass: Security and Permissions

<thinking>
Security considerations for CLAUDE.md:
1. Are there any hardcoded credentials or secrets?
2. Are file permissions appropriately scoped?
3. Are there references to sensitive paths that shouldn't be exposed?
4. If auto-approved commands listed, are they safe?
</thinking>

**Critical Security Checks:**

- [ ] No hardcoded API keys, tokens, or passwords
- [ ] No sensitive environment variables exposed
- [ ] No overly broad file permissions (e.g., Read:/\*)
- [ ] No dangerous auto-approved commands (rm -rf, etc.)
- [ ] No paths exposing sensitive user data

**Common Security Issues:**

```markdown
❌ BAD: apiKey: "sk-1234567890abcdef"
✅ GOOD: Reference: Use environment variable $API_KEY

❌ BAD: Auto-approve: Bash(rm -rf:_)
✅ GOOD: Auto-approve: Bash(npm install:_)

❌ BAD: Read://Users/username/.ssh/**
✅ GOOD: Read://Users/username/projects/myproject/**
```

---

### Second Pass: Structure and Clarity

<thinking>
CLAUDE.md structure considerations:
1. Are directives clearly stated and prioritized?
2. Is information organized logically?
3. Are references to other docs used instead of duplication?
4. Is the purpose of each section clear?
</thinking>

**Organizational Requirements:**

- [ ] Clear section headers organize content
- [ ] Core directives stated upfront
- [ ] References to detailed docs (not duplication)
- [ ] Logical flow from general to specific
- [ ] Purpose of file is immediately clear

**Example Structure:**

```markdown
# Project Guidelines

Core directives for [project purpose].

## Core Directives

[High-level must-follow rules]

## Code Quality Standards

[Brief standards, reference detailed docs]

## Workflow Practices

[How to approach tasks]

## Reference Documentation

[Links to detailed architecture/style docs]
```

**Red Flags:**

- No clear organization or section headers
- Mixing high-level directives with low-level details
- Duplicating content from other documentation files
- Unclear what the core requirements are

---

### Third Pass: Avoid Duplication

<thinking>
Duplication check:
1. Is content copied from other documentation files?
2. Are there references to source docs instead of duplication?
3. If something is detailed elsewhere, is it just linked?
4. Are core directives vs detailed specs properly separated?
</thinking>

**Anti-Pattern: Duplicating Architecture Docs**

❌ **BAD - Copying detailed patterns into CLAUDE.md:**

```markdown
## MVVM Pattern

ViewModels must expose StateFlow...
[500 lines of detailed MVVM guidance]
```

✅ **GOOD - Reference detailed docs:**

```markdown
## Core Directives

1. Adhere to Architecture: All code MUST follow `docs/ARCHITECTURE.md`
2. Follow Code Style: ALWAYS follow `docs/STYLE_AND_BEST_PRACTICES.md`
```

**Principle:** CLAUDE.md provides high-level directives and references. Detailed specs live in their own documentation files.

**Appropriate Content:**

- Core must-follow directives
- Workflow practices (before/during/after implementation)
- Decision-making guidance (when to ask vs proceed)
- References to detailed documentation

**Inappropriate Content:**

- Detailed API documentation (belongs in code docs)
- Complete architecture patterns (belongs in ARCHITECTURE.md)
- Full style guide (belongs in STYLE_AND_BEST_PRACTICES.md)
- Library-specific usage (belongs in library docs)

---

### Fourth Pass: Clarity and Actionability

<thinking>
Clarity considerations:
1. Are directives specific and actionable?
2. Is it clear WHEN each directive applies?
3. Are examples provided for ambiguous concepts?
4. Is the tone appropriate (directive vs suggestive)?
</thinking>

**Specific vs Vague Directives:**

❌ **VAGUE:** "Write good code"
✅ **SPECIFIC:** "Follow Kotlin idioms: immutability, appropriate data structures, coroutines"

❌ **VAGUE:** "Test your changes"
✅ **SPECIFIC:** "All code must pass testing rites before deployment liturgies commence"

❌ **VAGUE:** "Use dependency injection"
✅ **SPECIFIC:** "Use Hilt DI patterns: @Inject constructor, interface injection, @HiltViewModel"

**Actionable Decision Guidance:**

✅ **GOOD - Clear when to ask vs proceed:**

```markdown
## Decision-Making

Defer to user for high-impact decisions:

- Architecture/module changes
- Public API modifications
- Security mechanism changes
- Database migrations
- Third-party library additions

Proceed autonomously for:

- Implementation details within established patterns
- Test additions
- Documentation updates
- Bug fixes following existing patterns
```

---

### Fifth Pass: Token Efficiency

<thinking>
Token efficiency for CLAUDE.md:
1. Is the file concise without losing critical information?
2. Are references used instead of duplication?
3. Is verbose language minimized?
4. Is information organized for quick scanning?
</thinking>

**Efficiency Techniques:**

**Use References:**

```markdown
Reference Documentation:

- `docs/ARCHITECTURE.md` - Architecture patterns
- `docs/STYLE_AND_BEST_PRACTICES.md` - Code style

Do not duplicate information from these files.
```

**Use Lists and Headers:**

```markdown
Anti-Patterns:

- Creating new patterns when established ones exist
- Exception-based error handling in business logic
- Direct dependency access (use DI)
```

**Be Concise:**
❌ "It is very important that you should always make sure to..."
✅ "Always..."

---

## Priority Classification

Classify findings using `reference/priority-framework.md`:

- **CRITICAL** - Prevents functionality or exposes security vulnerabilities
- **IMPORTANT** - Significantly impacts quality or maintainability
- **SUGGESTED** - Improvements that aren't essential
- **OPTIONAL** - Personal preferences

---
