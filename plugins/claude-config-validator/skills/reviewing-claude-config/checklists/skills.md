# Skills Review Checklist

Review checklist for changes to Claude Code skill files (`SKILL.md` and supporting files).

---

## Multi-Pass Review Strategy

### First Pass: Structure and Security

<thinking>
Critical structural elements:
1. Is YAML frontmatter present and valid?
2. Is the skill file within 500 line limit?
3. Are there any security issues (hardcoded secrets, committed settings)?
4. Do all file references point to existing files?
5. Is progressive disclosure properly implemented?
</thinking>

**Focus Areas:**

- [ ] YAML frontmatter present and valid
- [ ] Skill file size ≤ 500 lines (progressive disclosure requirement)
- [ ] No hardcoded secrets or credentials
- [ ] File references point to existing files
- [ ] Supporting files are properly organized

**Critical Issues to Flag Immediately:**

- Missing YAML frontmatter (skill won't be recognized)
- File > 500 lines without progressive disclosure
- Hardcoded API keys, tokens, or passwords
- Broken file references
- Committed settings.local.json

---

### Second Pass: YAML Frontmatter Validation

<thinking>
YAML frontmatter requirements:
1. Is the `name` field present and kebab-case?
2. Is the `description` clear with activation triggers?
3. If versioned, does it follow semver?
4. Are there any malformed YAML syntax issues?
</thinking>

**Required Fields:**

```yaml
---
name: skill-name-in-kebab-case
description: Clear description with activation triggers
---
```

**Optional Fields:**

```yaml
version: 1.0.0 # Semver format if marketplace-bound
```

**Check For:**

- [ ] `name` field exists and is kebab-case
- [ ] `description` field exists and is clear
- [ ] Description includes activation triggers (when to use)
- [ ] YAML syntax is valid (proper indentation, no tabs)
- [ ] If versioned, follows semver (MAJOR.MINOR.PATCH)

**Common Issues:**

- Missing name or description
- Name not in kebab-case (use-dashes-not-underscores)
- Description too vague ("does stuff" → specify what and when)
- Malformed YAML (tabs instead of spaces, missing colons)

---

### Third Pass: Progressive Disclosure

<thinking>
Progressive disclosure requirements:
1. Is the main skill.md file under 500 lines?
2. Are supporting files properly referenced?
3. Are supporting files self-contained?
4. Is the loading strategy clear (when to load what)?
</thinking>

**Main skill.md Requirements:**

- [ ] File size ≤ 500 lines
- [ ] Clear routing logic (when to load which files)
- [ ] Structured thinking blocks guide decision-making
- [ ] References supporting files explicitly

**Supporting Files Requirements:**

- [ ] Each file is self-contained (understandable in isolation)
- [ ] Clear purpose stated at top of file
- [ ] No circular dependencies between files
- [ ] Loaded on-demand, not all at once

**File Organization Patterns:**

```
skill-name/
├── skill.md              # Main orchestration (≤500 lines)
├── checklists/           # Task-specific procedures
├── reference/            # Detailed criteria loaded as needed
├── examples/             # Sample outputs for guidance
└── scripts/              # Executable automation (if applicable)
```

**Red Flags:**

- Main skill.md > 500 lines (should be split into supporting files)
- Supporting files reference each other in circles
- All context loaded upfront instead of on-demand
- Supporting files not self-contained (require reading multiple files)

---

### Fourth Pass: Prompt Engineering Quality

<thinking>
Quality criteria for skill instructions:
1. Are instructions clear and specific?
2. Are examples provided for complex concepts?
3. Is proper emphasis used (bold, code blocks, sections)?
4. Do structured thinking blocks guide reasoning?
5. Is the tone constructive and actionable?
</thinking>

**Clarity:**

- [ ] Instructions are specific, not vague
- [ ] Technical terms are defined or demonstrated
- [ ] Expected behavior is clearly stated
- [ ] Step-by-step procedures where appropriate

**Examples:**

- [ ] Code examples for patterns to follow
- [ ] Sample outputs showing expected format
- [ ] Anti-patterns demonstrated (what NOT to do)
- [ ] File structure examples where relevant

**Emphasis:**

- [ ] **Bold** for critical requirements
- [ ] `Code blocks` for technical terms and examples
- [ ] Headers organize content logically
- [ ] Lists break down complex information

**Structured Thinking:**

- [ ] `<thinking>` blocks guide systematic analysis
- [ ] Key questions posed before each major step
- [ ] Decision criteria made explicit
- [ ] Reasoning process modeled for complex decisions

**Constructive Tone:**

- [ ] Focus on "do this" not just "don't do that"
- [ ] Explain rationale (why things matter)
- [ ] Provide actionable fixes, not just problem identification
- [ ] Avoid blame or judgment language

---

### Fifth Pass: Token Efficiency

<thinking>
Token efficiency considerations:
1. Is information organized for on-demand loading?
2. Are redundancies eliminated?
3. Is verbose language minimized without losing clarity?
4. Are examples concise but sufficient?
</thinking>

**Efficient Organization:**

- [ ] Progressive disclosure implemented (load only what's needed)
- [ ] No duplicate information across files
- [ ] Reference other docs instead of copying content
- [ ] Clear routing to minimize unnecessary context loading

**Concise Language:**

- [ ] Direct statements preferred over verbose explanations
- [ ] Technical precision without fluff
- [ ] Examples are minimal but sufficient
- [ ] Headers and structure reduce need for transitional text

**Avoid:**

- Repeating same information in multiple places
- Loading all context upfront "just in case"
- Verbose explanations when examples suffice
- Including information not directly relevant to task

---

## Priority Classification

Classify findings using `reference/priority-framework.md`:

- **CRITICAL** - Prevents functionality or exposes security vulnerabilities
- **IMPORTANT** - Significantly impacts quality or maintainability
- **SUGGESTED** - Improvements that aren't essential
- **OPTIONAL** - Personal preferences

---

## Common Skill Anti-Patterns

**Monolithic Skills:**

- Single file > 500 lines
- All context loaded upfront
- No progressive disclosure strategy
- Fix: Split into main orchestration + supporting files

**Vague Activation:**

- Description: "Helps with code stuff"
- Better: "Reviews Kotlin code for MVVM violations. Use when checking ViewModels, state management, or UI layer architecture."

**Missing Structured Thinking:**

- Instructions without guidance on reasoning process
- No decision criteria for complex choices
- Fix: Add `<thinking>` blocks with key questions

**Broken Progressive Disclosure:**

- Supporting files reference each other circularly
- Files not self-contained
- Unclear when to load what
- Fix: Clear routing logic, self-contained files

**Token Waste:**

- Duplicate information across files
- Loading all context upfront
- Verbose explanations without adding value
- Fix: Reference instead of duplicate, load on-demand

---

## Final Checklist Summary

Before completing review, verify:

- [ ] YAML frontmatter present and valid
- [ ] Main skill.md ≤ 500 lines
- [ ] No security issues (secrets, credentials)
- [ ] All file references valid
- [ ] Progressive disclosure properly implemented
- [ ] Structured thinking blocks present
- [ ] Clear activation triggers in description
- [ ] Examples provided for complex concepts
- [ ] Token-efficient organization
- [ ] Constructive, actionable feedback tone
