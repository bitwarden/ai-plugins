---
name: recalling-review-knowledge
description: Retrieves code review institutional knowledge for a repository including failed detections, repository gotchas, and review methodology from SKILL.md format. Use before starting code reviews to learn from past experience.
---

# Recalling Review Knowledge

Retrieve institutional knowledge from previous code reviews to avoid repeating mistakes. Loads SKILL.md files containing structured knowledge with frontmatter and organized sections.

---

## Workflow

### 1. Detect Repository

Identify the current repository owner and name.

**Error Handling**: If repository detection fails, inform the user to check authentication or git configuration.

### 2. Locate Knowledge

Check your known Skills for existing knowledge. It will be in the format `{repo_owner}-{repo_name}-review-knowledge`.

**If knowledge exists**: Load and display it
**If no knowledge exists**: Inform user and suggest running `/retrospective-review` after their next code review

### 3. Load Knowledge Files

Read and display the following files if they exist:
1. **Primary**: `SKILL.md` (always present if skill exists)
2. **Optional**: `references/troubleshooting.md` (error-solution mappings)

### 4. Provide Review Guidance

After loading knowledge, provide actionable guidance:

```markdown
---

## 💡 Review Guidance

**Before starting your review**:

1. **Review Failed Detections**: Learn from past mistakes and near-misses
2. **Check Repository Gotchas**: Verify architectural patterns specific to this codebase
3. **Apply Detection Strategies**: Use proven search patterns and validation techniques
4. **Reference Troubleshooting**: Check error-solution mappings if you encounter known patterns

**After completing your review**:
- Run `/retrospective-review` to add new learnings from this review
- Update SKILL.md if you discovered new patterns or gotchas

---
```

---

## Expected SKILL.md Structure

The loaded SKILL.md should contain:

```yaml
---
name: ${owner}-${repo}-review-knowledge
description: Code review knowledge for ${owner}/${repo} ([languages]). Usage scenarios...
verified_on: [languages/frameworks]
last_updated: YYYY-MM-DD
---

# Code Review Knowledge: ${owner}/${repo}

## Experiment Overview
[Summary of review learnings and purpose]

## Failed Detections
[Table: Issue | Why Missed | Detection Strategy | Review Date | PR Link | Type]

## Repository Gotchas
[Codebase-specific patterns, architectural decisions, conventions]

## Methodology Improvements
[Process improvements, calibration adjustments]

## Verified Detection Strategies
[Working detection commands by category]
```

---

## Output Format

**When knowledge exists**:
- Display complete SKILL.md content
- Display troubleshooting.md if present
- Provide actionable review guidance

**When no knowledge exists**:
- Inform user no knowledge captured yet
- Suggest running `/retrospective-review` after next code review
- List other repositories with available knowledge

---

## Error Handling

**Repository detection fails**:
- Inform user to check authentication or git configuration
- Provide clear error message with remediation steps

**Knowledge file is malformed**:
- Display successfully parsed sections
- Warn about corrupted sections

---

## Success Criteria

✅ **Knowledge successfully loaded when**:
- Repository detected correctly
- SKILL.md found and readable
- Optional troubleshooting.md loaded if present
- Clear guidance provided for upcoming review

✅ **Graceful handling when**:
- No knowledge exists yet for this repository
- Repository detection fails with clear remediation steps
- Partial content loaded with warnings for corrupted sections
