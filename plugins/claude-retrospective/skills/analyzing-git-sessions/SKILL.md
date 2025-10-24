---
name: analyzing-git-sessions
description: Analyzes git commits and changes within a timeframe or commit range, providing structured summaries for code review, retrospectives, work logs, or session documentation.
---

# Analyzing Git Sessions

## Core Responsibility

Generate structured analysis of git activity for specified timeframe or commit range, including commit history, file changes, statistics, and optional diffs.

## Inputs

Accept from user:
- **Time range**: "last 2 hours", "since 10am", "today", "since 2025-10-23 14:00"
- **Commit range**: "abc123..def456", "HEAD~5..HEAD", "feature-branch..main"
- **Optional filters**: Specific paths, authors, or file types
- **Output depth**: Concise (default), Detailed, or Code Review format

## Working Process

### Step 1: Parse and Validate Input

1. **Determine range type**:
   - Time-based: Parse relative or absolute time
   - Commit-based: Validate commit references exist
   - Branch-based: Resolve branch names to commits

2. **Validate git repository**:
   ```bash
   git rev-parse --git-dir
   ```

3. **Check range has commits**:
   ```bash
   git log <range> --oneline | head -1
   ```
   If empty, inform user and exit.

### Step 2: Extract Commit History

```bash
# Get all commits in range
git log <range> --oneline --no-decorate

# Get detailed commit info
git log <range> --format="%h|%an|%ar|%s" --no-decorate

# Count commits
git log <range> --oneline | wc -l
```

Store commit data for summary.

### Step 3: Generate Statistics

**Overall change statistics**:
```bash
# Summary stats (insertions/deletions by file)
git diff <start>..<end> --stat

# Numeric stats for parsing
git diff <start>..<end> --numstat

# Count total changes
git diff <start>..<end> --shortstat
```

**Author breakdown** (if multiple authors):
```bash
git shortlog <start>..<end> -sn
```

**File categorization**:
- Identify new files (show in status "A")
- Identify deleted files (show in status "D")
- Identify renamed files (show in status "R")
- Modified files with change magnitude

### Step 4: Identify Key Files for Detailed Analysis

**Prioritization rules**:
1. **Large changes** (>100 lines modified): Always include
2. **New files**: Include (especially if >50 lines)
3. **Deleted files**: Note but don't diff
4. **Architecture files**: `build.gradle.kts`, `AndroidManifest.xml`, module configs
5. **Test files**: Flag separately for test coverage assessment

**Extract key file list**:
```bash
# Files changed with line counts
git diff <start>..<end> --numstat | sort -rn -k1 -k2
```

Limit to top 10 files by default to avoid context overflow.

### Step 5: Generate Selective Diffs (Based on Depth)

**Concise mode**: No diffs, stats only

**Detailed mode**: Diffs for top 3-5 key files
```bash
git diff <start>..<end> -- path/to/key/file.kt
```

**Code Review mode**: Diffs for all modified files, grouped by module
```bash
# Group by directory
git diff <start>..<end> --name-only | cut -d'/' -f1-2 | sort -u

# Generate diffs per module
for module in modules; do
  git diff <start>..<end> -- $module/
done
```

**Context overflow protection**:
- If >10 files changed significantly, limit to top 5 diffs
- Warn user: "Showing top 5 files by change size. Request specific files for full diffs."

### Step 6: Present Structured Summary

**Format based on depth**:

#### Concise Summary
```markdown
## Git Session Summary

**Range**: <start-commit> to <end-commit> (<timeframe>)
**Commits**: X commits by Y author(s)
**Files Changed**: A modified, B added, C deleted
**Net Changes**: +X -Y lines

### Commits
- abc123 Commit message 1
- def456 Commit message 2
...

### Top Files Changed
1. path/to/file1.kt (+50 -20)
2. path/to/file2.kt (+30 -15)
...
```

#### Detailed Summary
Includes:
- Full commit list with authors and timestamps
- Complete file list with change stats
- Author breakdown
- Top 3-5 diffs for review

#### Code Review Format
```markdown
## Code Review Summary

### Overview
- **PR Title**: [Suggested from commit messages]
- **Changes**: X files across Y modules
- **Scope**: [Inferred from changed files]

### Commits
[Formatted commit list suitable for PR description]

### Changes by Module
**Module: app**
- file1.kt: Description of changes
- file2.kt: Description of changes

**Module: core**
...

### Key Changes
[Diffs for significant modifications]

### Test Coverage
- Test files modified: X
- New tests added: ~Y
```

## Output Guidelines

### Commit Messages
- Show short hash (7 chars)
- Show first line of commit message only
- Truncate long messages to 80 chars
- Group by author if multiple contributors

### File Paths
- Use relative paths from repo root
- Format as code: `path/to/file.kt`
- Include line change magnitude: (+X -Y)
- Highlight file type (source, test, config)

### Statistics
Present in clear tables:
```markdown
| Metric | Count |
|--------|-------|
| Commits | 15 |
| Files Changed | 23 |
| Insertions | +450 |
| Deletions | -180 |
```

### Diffs
- Include file path as header: `### path/to/file.kt`
- Use code blocks with syntax highlighting
- Show context lines (git default: 3 lines before/after)
- Truncate very large diffs (>200 lines) with summary

## Context Budget Management

**Monitor diff sizes**:
- Small session (<10 files, <500 lines): Safe for detailed mode
- Medium session (10-30 files, 500-2000 lines): Use selective diffs
- Large session (>30 files, >2000 lines): Concise mode with warnings

**Progressive disclosure**:
1. Always start with concise summary
2. Ask user: "Would you like detailed diffs for specific files?"
3. Generate diffs on demand rather than upfront

**Fallback for large sessions**:
"This session modified 45 files with 5000+ line changes. Showing concise summary. Request specific files or modules for detailed diffs."

## Anti-Patterns to Avoid

**Don't**:
- Generate diffs for all files in large sessions (context overflow)
- Include full diffs without asking (waste context on unneeded details)
- Ignore file types (treat test changes same as source changes)
- Lose context on what user wants to know
- Use generic summaries ("modified 10 files") without specifics

**Do**:
- Ask user what level of detail they need
- Prioritize key files by change magnitude
- Categorize files (source, test, config, docs)
- Provide actionable summaries
- Offer to drill down on specific files

## Success Criteria

A good git session analysis should:
1. **Inform**: User understands scope of changes at a glance
2. **Focus**: Highlights most significant changes first
3. **Actionable**: Provides paths and diffs for deeper review
4. **Efficient**: Doesn't waste context on unnecessary details
5. **Adaptable**: Adjusts depth based on session size and user needs

## Example Outputs

### Example 1: Concise (Small Session)
```markdown
## Git Session Summary

**Range**: 2025-10-23 14:00 to 16:30 (2.5 hours)
**Commits**: 5 commits
**Files Changed**: 7 modified, 2 added
**Net Changes**: +180 -45 lines

### Commits
- 3be876a Add session logging hooks
- 60d00cf Format file paths and code references
- 9a0bd0b Remove line references from SKILL.md
- dec2ed7 Add CODEOWNERS for Claude files
- b7fb072 Add reviewing-changes skill

### Top Files Changed
1. `${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/SKILL.md` (+85 -30)
2. `.claude/skills/reviewing-changes/SKILL.md` (+120 -0) [NEW]
3. `.claude/hooks/prompt-submit.sh` (+25 -10)
```

### Example 2: Code Review Format
```markdown
## Code Review Summary

### Overview
- **Suggested PR Title**: "Add retrospective skill with session logging"
- **Changes**: 9 files across 2 areas (skills, hooks)
- **Scope**: New skill creation + infrastructure improvements

### Commits (3)
- Add comprehensive retrospective skill with analysis framework
- Implement session logging hooks for skill consumption
- Add code review skill for PR validation

### Changes by Area

**Skills** (6 files):
- `${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/SKILL.md`: New skill definition
- `${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/contexts/session-analytics.md`: Analysis framework
- `.claude/skills/reviewing-changes/SKILL.md`: New code review skill

**Infrastructure** (3 files):
- `.claude/hooks/prompt-submit.sh`: Add logging on session events
- `.claude/CODEOWNERS`: Add ownership for Claude config files
- `docs/ARCHITECTURE.md`: Document skill system

### Test Coverage
- No test files modified
- Consider: Unit tests for log parsing logic

[Key diffs would follow...]
```