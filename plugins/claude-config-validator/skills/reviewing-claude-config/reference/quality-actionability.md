# Actionability

Clear guidance on what to do, not just identification of problems.

---

## Definition

Clear guidance on what to do, not just identification of problems.

## Good Actionability

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

## Poor Actionability

❌ **PROBLEM ONLY:**
```markdown
This is wrong.
```

❌ **VAGUE GUIDANCE:**
```markdown
Fix the state management issue somehow.
```

## Actionability Techniques

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
