# Examples

Demonstrate concepts with concrete examples, not just descriptions.

---

## Definition

Demonstrate concepts with concrete examples, not just descriptions.

## Good Examples

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

## Poor Examples

❌ **DESCRIPTION ONLY:**
```markdown
State should be exposed as StateFlow, not MutableStateFlow.
```

❌ **ABSTRACT:**
```markdown
Follow the established pattern for state management.
```

## Example Categories

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
