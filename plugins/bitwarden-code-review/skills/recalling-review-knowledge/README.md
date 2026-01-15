# recalling-review-knowledge

Retrieves institutional knowledge for a repository before starting code reviews, providing context on past failures, architectural patterns, and effective review methodologies.

## Overview

This skill loads repository-specific code review knowledge from SKILL files, presenting it in a format optimized for reviewers to quickly understand what to watch for based on historical learnings.

## Usage

```bash
# Before starting a code review (auto-detects repository from git remote)
/advise-review

# In bitwarden/clients repository
/advise-review
# → Loads skills/bitwarden-clients-review-knowledge/SKILL.md
```

## What It Does

1. **Detects current repository** from git remote (e.g., `bitwarden/clients`)
2. **Looks for corresponding SKILL** at `skills/{owner}-{repo}-review-knowledge/SKILL.md`
3. **If found**: Displays the knowledge using Read tool
4. **If not found**: Provides friendly message suggesting first review capture

## Output Format

When knowledge exists, displays the complete SKILL file content:

```markdown
# Code Review Guidance: bitwarden/clients

## 🎯 Failed Detections to Watch For

| Issue | Why Missed | Detection Strategy | Review Date | PR | Severity |
|-------|------------|-------------------|-------------|----|----------|
| Auth bypass in vault unlock | Focused on UI, missed authorization check | Always verify permission checks when auth code changes | 2025-12-15 | #789 | ❌ CRITICAL |

### Key Patterns
- Authentication checks often missed when UI code changes
- State management violations hard to spot without architecture knowledge

## 🏗️ Repository Gotchas

### Sealed Class State Management
**Pattern**: All ViewModel state changes must go through sealed class handlers

**Common Mistake**: Direct `.postValue()` calls bypassing sealed classes

**Detection Strategy**: Search for `.postValue(` outside sealed handler directories

**Impact**: Runtime crashes, state inconsistency, race conditions

**References**: PR [#756](https://github.com/bitwarden/clients/pull/756)

## 📊 Methodology Improvements

### Test-First Review Strategy

**What Worked**: Starting review by reading test files first to understand expected behavior

**What Didn't Work**: Starting with implementation without understanding requirements

**Lesson**: Tests provide a roadmap for review. They document expected behavior more clearly than PR descriptions.

**Applicability**: PRs with comprehensive test coverage, feature additions, complex business logic
```

## When No Knowledge Exists

If this is the first review for the repository:

```
ℹ️  No knowledge captured yet for bitwarden/clients

Run '/retrospective-review' after completing a code review to begin capturing institutional knowledge.
```

## How It Finds Skills

The skill uses Claude Code's skill discovery mechanism:

1. Checks `skills/{owner}-{repo}-review-knowledge/SKILL.md`
2. Skills with trigger-rich descriptions are automatically suggested by Claude Code
3. The YAML frontmatter makes skills discoverable:

```yaml
---
name: bitwarden-clients-review-knowledge
description: "Code review knowledge for bitwarden/clients (TypeScript, Kotlin, Swift). Usage scenarios: (1) When reviewing PRs in bitwarden/clients, (2) When encountering sealed class state management, (3) When checking authentication flows. Verified on TypeScript, Kotlin, Swift."
---
```

## Knowledge Freshness

The SKILL file includes metadata about knowledge freshness:

- **Review Count**: Number of reviews analyzed
- **Date Range**: First to last review
- **Last Updated**: Most recent knowledge capture

This helps reviewers assess how current and comprehensive the knowledge is.

## Requirements

- Claude Code with plugin support
- Git repository with GitHub remote
- Existing SKILL file for the repository (created by `capturing-review-knowledge`)

## Configuration

No special configuration required. The skill works out of the box.

## Example Workflow

```bash
# 1. Start review session
cd ~/repos/bitwarden/clients

# 2. Load institutional knowledge
/advise-review

# 3. Review the displayed knowledge:
#    - Failed Detections: Issues to watch for
#    - Repository Gotchas: Architectural patterns
#    - Methodology Improvements: Effective approaches

# 4. Perform code review with context
/code-review-local

# 5. After review, capture new learnings
/retrospective-review
```

## Tips for Effective Use

1. **Always run before reviewing**: Make it a habit to load knowledge first
2. **Reference detection strategies**: Use the copy-paste commands when checking code
3. **Trust the gotchas**: These are patterns that have caused real issues
4. **Apply methodologies**: Use proven approaches from methodology improvements
5. **Update after reviewing**: Capture new learnings to build institutional memory

## Integration with Review Workflow

This skill complements the review process:

```
Before Review          During Review                    After Review
─────────────         ──────────────                   ─────────────
/advise-review   →    Use loaded knowledge       →     /retrospective-review
(Load context)        Check for known patterns         (Capture new learnings)
```

## See Also

- [capturing-review-knowledge](../capturing-review-knowledge/README.md) - Capture learnings after reviews
- [Main Plugin README](../../README.md) - Overview and examples
