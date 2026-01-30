# Knowledge Extraction Reference

Reference formats and quality guidelines for extracting code review knowledge.

---

## Failed Detections Format

**Table Structure**:
```markdown
| Issue | Why Missed | Detection Strategy | Review Date | PR Link | Type |
|-------|------------|-------------------|-------------|---------|------|
```

**Columns**:
- **Issue**: Specific problem description (30-50 words max)
- **Why Missed**: Root cause—what caused reviewer to miss it
- **Detection Strategy**: Actionable strategy with search patterns
- **Review Date**: YYYY-MM-DD format
- **PR Link**: `[#123](full-url)`
- **Type**: `VALID_ISSUE` | `FALSE_POSITIVE`

**Quality Examples**:

✅ **GOOD - Specific and actionable**:
```
Authentication bypass in vault unlock flow | Focused on UI changes, didn't trace authorization | Search for `checkPermission()` calls in auth PRs | 2025-12-15 | [#789](url) | VALID_ISSUE
```

❌ **BAD - Vague**:
```
Security issue | Missed it | Check for security problems | 2025-12-15 | [#789] | VALID_ISSUE
```

---

## Repository Gotchas Format

**Structure**:
```markdown
### [Pattern Name]

**Pattern**: [Description]
**Common Mistake**: [What goes wrong]
**Detection Strategy**: [How to spot violations]
**Impact**: [Consequences]
**References**: [PR links]
```

**Example**:
```markdown
### Sealed Class State Management

**Pattern**: All ViewModel state changes must flow through sealed class handlers

**Common Mistake**: Direct `.postValue()` calls bypassing sealed class pattern

**Detection Strategy**:
- Search for `.postValue(` in ViewModel files
- Verify all matches are within sealed class handlers
- Check `/sealed/` directory structure

**Impact**: Runtime crashes, state inconsistency, race conditions

**References**: [#756](url), [Architecture Doc](url)
```

---

## Methodology Insights Format

**Structure**:
```markdown
## [Strategy Name]

**What Worked**: [Effective approach]
**What Didn't Work**: [Ineffective approach]
**Lesson**: [Key takeaway]
**Applicability**: [When to use]
**Example**: [PR reference]
```

**Example**:
```markdown
## Test-First Review

**What Worked**: Reading test files first to understand expected behavior

**What Didn't Work**: Starting with implementation without understanding requirements

**Lesson**: Tests document expected behavior more clearly than PR descriptions

**Applicability**: PRs with test coverage, feature additions, complex logic

**Example**: [#892](url) - Caught edge case handling error
```

---

## Quality Guidelines

### High-Quality Knowledge

✅ **Specific**: Include search patterns, class names, method signatures
✅ **Actionable**: Copy-paste ready commands or checklists
✅ **Concrete**: Link specific PRs, code locations
✅ **Root cause**: Explain WHY missed, not just WHAT
✅ **Concise**: 30-50 words per entry

### Low-Quality Knowledge (Avoid)

❌ Vague advice: "Be careful", "Check thoroughly"
❌ No strategy: Missing detection approach
❌ Generic: Could apply to any repository
❌ No examples: No PR references or code patterns
