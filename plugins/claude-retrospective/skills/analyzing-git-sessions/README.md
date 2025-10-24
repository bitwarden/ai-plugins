# Analyzing Git Sessions

Analyzes git commits and changes within a timeframe or commit range, providing structured summaries for various use cases.

## What It Does

This skill analyzes git repository activity and produces structured summaries including:
- Commit history with messages and authors
- File change statistics (additions, deletions, modifications)
- Identification of key files by change magnitude
- Optional code diffs for review
- Multiple output formats for different use cases

## When to Use

Use this skill when you need to:
- **Review your work**: "What did I accomplish in the last 2 hours?"
- **Prepare code reviews**: Generate PR descriptions and identify review focus areas
- **Write standups**: "What did I work on yesterday?"
- **Document sessions**: Capture work done during a coding session
- **Analyze branches**: "What changes are in my feature branch?"
- **Track activity**: Weekly or monthly contribution summaries

## How to Use

### Natural Language Invocations

**Time-based analysis**:
- "Analyze my git changes from the last 2 hours"
- "Show me what I committed today"
- "Summarize my work since 10am"
- "What changed in the last hour?"

**Commit range analysis**:
- "Show me changes between abc123 and def456"
- "Analyze commits from HEAD~5 to HEAD"
- "Compare feature-branch to main"

**With specific focus**:
- "Show me authentication module changes from today"
- "What test files did I modify this week?"
- "Analyze changes in the app directory since yesterday"

**Output format requests**:
- "Generate a code review summary for my last 3 commits"
- "Give me a concise summary of today's work"
- "Show detailed diffs for my morning commits"

### Direct Skill Invocation

```
/skill analyzing-git-sessions
```

The skill will prompt you for:
1. Time range or commit range
2. Optional path filters
3. Desired output depth (concise/detailed/code review)

## Output Formats

### 1. Concise Summary (Default)

Best for: Quick overview, standup reports, work logs

Includes:
- Commit count and authors
- Files changed summary (added/modified/deleted)
- Net line changes
- Top 5-10 files by change size
- Commit messages

**Example**:
```
Git Session Summary
Range: 2 hours ago to now
Commits: 8
Files Changed: 12 modified, 2 added
Net Changes: +340 -120 lines

Top Files:
1. AuthViewModel.kt (+85 -30)
2. LoginScreen.kt (+60 -15)
...
```

### 2. Detailed Summary

Best for: Session documentation, deeper review

Includes everything from Concise, plus:
- Full file list with statistics
- Author breakdown
- Diffs for top 3-5 files
- File categorization (source, test, config)

### 3. Code Review Format

Best for: PR preparation, team reviews

Includes:
- Suggested PR title (from commits)
- Changes grouped by module/directory
- Scope summary
- Test coverage assessment
- Formatted commits suitable for PR description
- Key diffs organized by module

## Configuration Options

### Output Depth

Control level of detail:
- **Concise**: Stats and commit list only (~500-1000 tokens)
- **Detailed**: Stats + top file diffs (~2000-5000 tokens)
- **Code Review**: Comprehensive with module grouping (~3000-8000 tokens)

The skill automatically suggests appropriate depth based on session size.

### Path Filters

Narrow analysis to specific paths:
- "Analyze changes in app/src/main/kotlin/auth/"
- "Show only test file changes"
- "Focus on gradle files"

### Author Filters

For multi-contributor analysis:
- "Show only my commits from today"
- "What did the team change this week?"

## Use Cases

### 1. Daily Standup Preparation

**Request**: "Summarize my git changes from yesterday"

**Result**: Concise list of commits and key files for standup discussion

### 2. Code Review Preparation

**Request**: "Generate code review summary for feature-auth-biometrics branch"

**Result**: PR-ready description with:
- What changed and why
- Files organized by module
- Test coverage notes
- Suggested review focus areas

### 3. Session Documentation

**Request**: "Detailed analysis of my work in the last 3 hours"

**Result**: Comprehensive summary for retrospective or work log:
- What was accomplished
- Which files were touched
- Magnitude of changes
- Key code diffs

### 4. Weekly Activity Summary

**Request**: "Show me all my commits from the last 7 days"

**Result**: Week-at-a-glance view of your contributions

### 5. Branch Comparison

**Request**: "Compare feature-branch to main"

**Result**: What's in the feature branch that's not in main
- Commits to be merged
- Files that will change
- Potential conflicts

### 6. Retrospective Git Data

**Request**: (Called by retrospecting skill during analysis)

**Result**: Git metrics for retrospective:
- Session scope (commit count, file count)
- Change velocity
- Areas of focus (which modules touched)

## Tips for Best Results

### Be Specific About Timeframe

**Good**:
- "Last 2 hours"
- "Since 2025-10-23 14:00"
- "Today from 9am to 5pm"

**Less specific** (still works, but may need clarification):
- "Recent changes" → skill will ask "how recent?"
- "My work" → skill will ask "from when?"

### Request Appropriate Depth

For quick checks: "Give me a concise summary"
For thorough review: "Detailed analysis with diffs"
For PR prep: "Code review format"

The skill will recommend depth based on session size, but you can override.

### Use Filters for Large Sessions

If you worked on multiple areas:
- "Show only authentication changes from today"
- "Analyze ViewModel changes in the last week"

This keeps output focused and context-efficient.

## Output Examples

### Example 1: Quick Work Log

**Input**: "What did I work on this morning?"

**Output**:
```markdown
Git Session Summary (9:00am - 12:00pm)

Commits: 6
Files: 9 modified, 1 added
Changes: +220 -65 lines

Commits:
- Add biometric authentication support
- Refactor LoginViewModel state handling
- Update authentication tests
- Fix credential manager integration
- Add error handling for biometric failures
- Update documentation

Key Files:
1. BiometricAuthManager.kt (+85 -15)
2. LoginViewModel.kt (+60 -25)
3. AuthenticationTests.kt (+45 -20)
```

### Example 2: Code Review Ready

**Input**: "Generate PR summary for my feature branch"

**Output**:
```markdown
Pull Request Summary

Title: Add Biometric Authentication Support

Overview:
- 12 commits over 3 days
- 15 files changed across 3 modules
- Adds biometric authentication flow with fallback

Commits:
1. Implement BiometricAuthManager for authentication
2. Add biometric prompt UI components
3. Integrate with CredentialManager API
...

Changes by Module:

app (8 files):
- BiometricAuthManager.kt: Core biometric logic
- LoginScreen.kt: UI integration
- AuthViewModel.kt: State management

core (4 files):
- CredentialProvider.kt: Credential management
- SecurityUtils.kt: Security helpers

tests (3 files):
- BiometricAuthTests.kt: Unit tests
- LoginFlowTests.kt: Integration tests

Test Coverage:
✓ 2 new test files added
✓ 45 new test cases
⚠ Consider: Error handling edge cases

[Diffs for key files would follow]
```

## Integration with Other Skills

This skill integrates with several workflows and can be invoked standalone or as part of other processes:

### Retrospecting Skill
- Invoked during Step 2 (Gather Data - Git Analysis)
- Provides commit history and change stats for retrospective analysis

### Code Review Preparation
- Generate PR descriptions
- Identify review focus areas
- Highlight test coverage changes

### Daily Standup Reports
- "What did I work on yesterday?"
- Quick summary of activity

### Work Log Generation
- Weekly/monthly activity summaries
- Contribution tracking

## Performance Notes

### Context Efficiency

- **Concise mode**: ~500-1K tokens (very efficient)
- **Detailed mode**: ~2-5K tokens (moderate)
- **Code Review mode**: ~3-8K tokens (comprehensive)

For large sessions (>30 files), the skill automatically uses concise mode to prevent context overflow.

### Speed

- Git commands are fast (typically <1 second)
- Analysis and formatting: 5-10 seconds
- Total time: Usually <30 seconds

## Limitations

**Cannot**:
- Analyze uncommitted changes (use `git status` or `git diff` directly)
- Access remote branches not fetched locally
- Interpret semantic meaning of changes (shows what changed, not why)
- Generate commits or modify git history

**Works best with**:
- Clean commit history with meaningful messages
- Commits pushed regularly (not one giant commit)
- Reasonable session sizes (<100 files changed)

## Troubleshooting

### "No commits found in range"

- Check your time syntax: "since 2 hours ago" not "2 hours"
- Verify commits exist: `git log --since="your timeframe"`
- Try absolute time: "since 2025-10-23 10:00"

### "Too many files changed, showing summary only"

- This is context protection (>30 files)
- Request specific paths: "Show only app/ changes"
- Use concise mode explicitly
- Split analysis into multiple focused queries

### "Commit range invalid"

- Check commit hashes exist: `git log abc123`
- Use correct range syntax: `start..end` (two dots)
- Ensure branch names are correct

### Output seems incomplete

- Specify "detailed" mode explicitly
- Check if session size triggered automatic concise mode
- Request specific files: "Show diffs for MainActivity.kt"

## Version History

**v1.0** (2025-10-23):
- Initial release
- Support for time ranges and commit ranges
- Three output formats (concise, detailed, code review)
- Context-aware depth selection
- Integration with retrospecting skill

## Feedback

Found an issue or want a feature?
- Update `.claude/skills/analyzing-git-sessions/SKILL.md`
- Modify this README for documentation improvements
- Suggest new output formats or filters

---

**Maintained By**: Project team
**Related Skills**: `retrospecting`, `reviewing-changes`