# Specificity

Concrete details and precise requirements over general guidance.

---

## Definition

Concrete details and precise requirements over general guidance.

## Good Specificity

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

## Poor Specificity

❌ **GENERIC:**
```markdown
Follow best practices for state management.
```

❌ **IMPRECISE:**
```markdown
Keep files reasonably sized.
```

## Improvement Techniques

- Provide exact thresholds (500 lines, not "reasonably sized")
- Show specific code patterns to follow
- Name specific files, functions, or patterns
- Include concrete examples
