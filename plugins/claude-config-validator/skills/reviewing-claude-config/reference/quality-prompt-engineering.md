# Prompt Engineering Quality Reference

Comprehensive guide to evaluating and improving Claude configuration quality across all file types.

---

## Table of Contents

**Fundamentals:**
- [Clarity](#clarity) - Instructions are specific, unambiguous, and easy to understand
- [Specificity](#specificity) - Concrete details and precise requirements over general guidance

**Content Quality:**
- [Examples](#examples) - Demonstrate concepts with concrete examples, not just descriptions
- [Context](#context) - Provide necessary background without overwhelming
- [Actionability](#actionability) - Clear guidance on what to do, not just problem identification

**Formatting:**
- [Emphasis](#emphasis) - Proper formatting highlights critical information
- [Structure](#structure) - Logical organization aids comprehension and navigation

**Advanced Techniques:**
- [Structured Thinking](#structured-thinking) - Use `<thinking>` blocks to guide reasoning
- [Improvement Patterns](#improvement-patterns) - Common patterns for enhancement

**Quick Reference:**
- [Quality Checklist](#quality-checklist) - Use this to evaluate any Claude configuration

---

## Clarity

Instructions are specific, unambiguous, and easy to understand.

### Good Clarity

✅ **SPECIFIC:**
```markdown
Analyze modified Kotlin files for MVVM violations:
- Exposed MutableStateFlow (should be StateFlow)
- Missing @HiltViewModel annotation
- Direct repository access in UI layer
```

✅ **UNAMBIGUOUS:**
```markdown
Review all files changed in the current PR. For each file:
1. Check for security issues
2. Validate architectural patterns
3. Document findings with inline comments
```

### Poor Clarity

❌ **VAGUE:**
```markdown
Look at the code and find problems.
```

❌ **AMBIGUOUS:**
```markdown
Review the changes and let me know what you think.
```

### Improvement Techniques

- Use specific technical terms, not generic words
- Break complex instructions into numbered steps
- Define what "done" looks like
- Provide decision criteria

---

## Specificity

Concrete details and precise requirements over general guidance.

### Good Specificity

✅ **CONCRETE REQUIREMENTS:**
```markdown
All ViewModel state must follow this pattern:

\```kotlin
private val _state = MutableStateFlow<State>(Initial)
val state: StateFlow<State> = _state.asStateFlow()
\```

Rationale: Prevents external mutation, enforces unidirectional data flow.
```

✅ **PRECISE CRITERIA:**
```markdown
Skill files must be ≤ 500 lines. If longer:
1. Identify distinct responsibilities
2. Extract to supporting files in subdirectories
3. Load supporting files on-demand
```

### Poor Specificity

❌ **GENERIC:**
```markdown
Follow best practices for state management.
```

❌ **IMPRECISE:**
```markdown
Keep files reasonably sized.
```

### Improvement Techniques

- Provide exact thresholds (500 lines, not "reasonably sized")
- Show specific code patterns to follow
- Name specific files, functions, or patterns
- Include concrete examples

---

## Examples

Demonstrate concepts with concrete examples, not just descriptions.

### Good Examples

✅ **CODE EXAMPLES:**
```markdown
**Before (incorrect):**
\```kotlin
val state = MutableStateFlow<State>(Initial)
\```

**After (correct):**
\```kotlin
private val _state = MutableStateFlow<State>(Initial)
val state: StateFlow<State> = _state.asStateFlow()
\```
```

✅ **SAMPLE OUTPUTS:**
```markdown
Expected review comment format:

**file.kt:123** - CRITICAL: Exposes mutable state

Change MutableStateFlow to StateFlow:
[code example]

Rationale: Prevents external mutation.
```

### Poor Examples

❌ **DESCRIPTION ONLY:**
```markdown
State should be exposed as StateFlow, not MutableStateFlow.
```

❌ **ABSTRACT:**
```markdown
Follow the established pattern for state management.
```

### Example Categories

**Code Examples:**
- Before/after code snippets
- Correct implementation patterns
- Anti-patterns to avoid

**Format Examples:**
- Sample comment formats
- Expected output structure
- File structure examples

**Conceptual Examples:**
- Concrete scenarios
- Specific use cases
- Real-world applications

---

## Context

Provide necessary background without overwhelming with information.

### Good Context

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

### Poor Context

❌ **CONTEXT OVERLOAD:**
```markdown
[10 paragraphs of LLM history and theory before getting to actual instructions]
```

❌ **NO CONTEXT:**
```markdown
Use progressive disclosure.

[No explanation of what that means or why]
```

### Context Guidelines

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

---

## Actionability

Clear guidance on what to do, not just identification of problems.

### Good Actionability

✅ **SPECIFIC FIXES:**
```markdown
**CRITICAL**: Exposed MutableStateFlow

Change to private backing field pattern:

\```kotlin
private val _state = MutableStateFlow<State>(Initial)
val state: StateFlow<State> = _state.asStateFlow()
\```

This prevents external mutation while allowing internal updates.
```

✅ **CLEAR NEXT STEPS:**
```markdown
## If Security Issues Found

1. Stop review immediately
2. Flag as CRITICAL with specific issue
3. Provide exact remediation steps
4. Block approval until fixed
```

### Poor Actionability

❌ **PROBLEM ONLY:**
```markdown
This is wrong.
```

❌ **VAGUE GUIDANCE:**
```markdown
Fix the state management issue somehow.
```

### Actionability Techniques

**For Code Issues:**
- Show exact code to change
- Provide corrected version
- Explain why the fix works

**For Process Issues:**
- List specific steps to take
- Provide commands to run
- Show expected outcomes

**For Decisions:**
- Provide decision criteria
- List options with tradeoffs
- Recommend approach with rationale

---

## Emphasis

Proper formatting highlights critical information and organizes content.

### Good Emphasis

✅ **PROPER FORMATTING:**
```markdown
**CRITICAL**: All skills MUST have YAML frontmatter

Required fields:
- `name`: kebab-case skill identifier
- `description`: Clear purpose with activation triggers

**Without frontmatter, skill won't be recognized.**
```

✅ **VISUAL HIERARCHY:**
```markdown
# Main Topic

## Subtopic

### Specific Requirement

**Critical:** [urgent information]

- [ ] Checklist item
```

### Poor Emphasis

❌ **WALL OF TEXT:**
```markdown
All skills must have YAML frontmatter or they won't be recognized by Claude Code. The frontmatter requires a name field which should be in kebab-case format and a description field that clearly states the purpose and when to use the skill.
```

❌ **OVER-EMPHASIS:**
```markdown
**CRITICAL IMPORTANT URGENT: This is very very important!!!**
```

### Formatting Techniques

**Bold:**
- `**CRITICAL**`, `**IMPORTANT**` for priority levels
- `**Required**`, `**Optional**` for field requirements
- Key terms in first introduction

**Code Formatting:**
- `` `technical terms` `` for inline code/commands
- ` ```language ` blocks for multi-line code
- File paths: `` `.claude/settings.json` ``

**Lists:**
- Bulleted lists for unordered items
- Numbered lists for sequential steps
- Checklists `- [ ]` for validation items

**Headers:**
- `#` for major sections
- `##` for subsections
- `###` for specific topics

---

## Structure

Logical organization that aids comprehension and navigation.

### Good Structure

✅ **LOGICAL FLOW:**
```markdown
# Skill Name

## Purpose
[What this does and when to use it]

## Instructions

### Step 1: [First Action]
[Details]

### Step 2: [Second Action]
[Details]

## Examples
[Concrete examples]

## Common Issues
[Troubleshooting]
```

✅ **PROGRESSIVE DISCLOSURE:**
```markdown
# Main Skill (≤500 lines)
- High-level overview
- Decision routing logic
- References to detailed files

# Supporting Files
- Loaded on-demand
- Self-contained
- Specific deep-dives
```

### Poor Structure

❌ **NO ORGANIZATION:**
```markdown
Here's a bunch of information about the skill. It does various things...
[unstructured content continues]
```

❌ **INVERTED PRIORITY:**
```markdown
[500 lines of detailed implementation patterns]

## Purpose
Oh by the way, this skill reviews code.
```

### Structural Patterns

**Top-Down:**
1. Purpose and activation (what and when)
2. High-level approach (how)
3. Specific details (detailed guidance)
4. Examples (concrete demonstrations)

**Multi-Pass:**
1. First pass: Critical security checks
2. Second pass: Structure validation
3. Third pass: Quality review
4. Fourth pass: Optimization

**Routing:**
1. Detect type
2. Route to appropriate checklist
3. Checklists contain specific guidance
4. Reference files for deep dives

---

## Structured Thinking

Use `<thinking>` blocks to guide systematic reasoning before actions.

### Good Structured Thinking

✅ **SYSTEMATIC ANALYSIS:**
```markdown
### Step 1: Detect Change Type

<thinking>
Analyze the changeset systematically:
1. What files were modified? (code vs config vs docs)
2. What is the PR/commit title indicating?
3. Is there new functionality or just modifications?
4. What's the risk level of these changes?
</thinking>

Determine the primary change type:
[detection rules]
```

✅ **DECISION GUIDANCE:**
```markdown
<thinking>
Before writing each comment:
1. Is this issue Critical, Important, or Suggested?
2. Should I ask a question or provide direction?
3. What's the rationale I need to explain?
4. What code example would make this actionable?
</thinking>
```

### Poor Structured Thinking

❌ **NO GUIDANCE:**
```markdown
Review the code and find issues.
[No thinking guidance provided]
```

❌ **POST-HOC THINKING:**
```markdown
[Provides answer immediately]

<thinking>
I guess I should have thought about this first...
</thinking>
```

### Thinking Block Guidelines

**Place Before:**
- Major decisions
- Complex analysis
- Prioritization choices
- Output generation

**Include:**
- Key questions to consider
- Decision criteria
- Systematic approach
- What to evaluate

**Format:**
```markdown
<thinking>
1. [First consideration]
2. [Second consideration]
3. [Decision criteria]
</thinking>

[Then proceed with action based on thinking]
```

---

## Improvement Patterns

Common patterns for improving Claude configuration quality.

### Pattern 1: Vague → Specific

**Before:**
```markdown
Review the code for issues.
```

**After:**
```markdown
Analyze Kotlin files for MVVM violations:
1. Exposed MutableStateFlow (should use private backing)
2. Missing @HiltViewModel annotation
3. Direct repository access in UI layer

Document each issue with file:line reference.
```

---

### Pattern 2: Abstract → Concrete

**Before:**
```markdown
Follow best practices for file size.
```

**After:**
```markdown
Main skill file must be ≤ 500 lines (Anthropic progressive disclosure guideline).

If longer:
1. Extract supporting files to subdirectories
2. Keep main file as routing logic only
3. Load supporting files on-demand
```

---

### Pattern 3: No Examples → With Examples

**Before:**
```markdown
Use proper comment format.
```

**After:**
```markdown
Use inline comment format:

**file.kt:123** - CRITICAL: Issue description

[Specific fix with code example]

[Rationale]
```

---

### Pattern 4: Poor Structure → Clear Structure

**Before:**
```markdown
[Mixed details, examples, instructions, and background in no particular order]
```

**After:**
```markdown
# Purpose
[What and when]

## Instructions
[How - step by step]

## Examples
[Concrete demonstrations]

## Reference
[Deep dives loaded on-demand]
```

---

### Pattern 5: No Thinking → Structured Thinking

**Before:**
```markdown
Classify the priority of this issue.
```

**After:**
```markdown
<thinking>
1. Does this prevent functionality or expose security risk? → CRITICAL
2. Significantly impacts quality/maintainability? → IMPORTANT
3. Nice to have improvement? → SUGGESTED
4. Personal preference? → OPTIONAL
</thinking>

Classify as: [result based on criteria above]
```

---

## Quality Checklist

Use this checklist to evaluate Claude configuration quality.

### Clarity
- [ ] Instructions are specific and unambiguous
- [ ] Technical terms are defined or demonstrated
- [ ] Steps are clearly sequenced
- [ ] Success criteria are explicit

### Specificity
- [ ] Concrete thresholds provided (not "reasonable")
- [ ] Specific patterns shown (not "follow best practices")
- [ ] Exact files/functions named when relevant
- [ ] Precise requirements stated

### Examples
- [ ] Code examples for patterns to follow
- [ ] Before/after demonstrations
- [ ] Sample outputs showing expected format
- [ ] Anti-patterns illustrated

### Emphasis
- [ ] Bold for critical requirements
- [ ] Code formatting for technical terms
- [ ] Headers organize content logically
- [ ] Lists break down complexity

### Structure
- [ ] Logical flow (purpose → approach → details → examples)
- [ ] Progressive disclosure implemented
- [ ] Clear routing between files
- [ ] Appropriate depth at each level

### Context
- [ ] Necessary background provided
- [ ] Rationale explained (why it matters)
- [ ] No information overload
- [ ] Relevant research cited when applicable

### Actionability
- [ ] Specific fixes provided, not just problem identification
- [ ] Clear next steps outlined
- [ ] Decision criteria explicit
- [ ] Commands/code ready to use

### Structured Thinking
- [ ] `<thinking>` blocks before major decisions
- [ ] Key questions posed
- [ ] Systematic approach modeled
- [ ] Reasoning process explicit
