# Clarity

Instructions are specific, unambiguous, and easy to understand.

---

## Definition

Instructions are specific, unambiguous, and easy to understand.

## Good Clarity

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

## Poor Clarity

❌ **VAGUE:**
```markdown
Look at the code and find problems.
```

❌ **AMBIGUOUS:**
```markdown
Review the changes and let me know what you think.
```

## Improvement Techniques

- Use specific technical terms, not generic words
- Break complex instructions into numbered steps
- Define what "done" looks like
- Provide decision criteria
