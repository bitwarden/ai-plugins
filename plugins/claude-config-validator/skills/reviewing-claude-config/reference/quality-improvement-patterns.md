# Improvement Patterns

Common patterns for improving Claude configuration quality.

---

## Pattern 1: Vague → Specific

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

## Pattern 2: Abstract → Concrete

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

## Pattern 3: No Examples → With Examples

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

## Pattern 4: Poor Structure → Clear Structure

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

## Pattern 5: No Thinking → Structured Thinking

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
