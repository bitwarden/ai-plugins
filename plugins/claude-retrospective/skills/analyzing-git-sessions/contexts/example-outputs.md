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
1. `.claude/skills/retrospecting/SKILL.md` (+85 -30)
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
- `.claude/skills/retrospecting/SKILL.md`: New skill definition
- `.claude/skills/retrospecting/contexts/session-analytics.md`: Analysis framework
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
