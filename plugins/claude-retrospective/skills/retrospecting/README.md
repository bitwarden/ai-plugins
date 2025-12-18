# Session Retrospective Skill

Comprehensive analysis of Claude Code sessions to identify successful patterns, problematic areas, and opportunities for improvement.

## What It Does

This skill analyzes completed Claude Code sessions by examining:

- Git history (commits, diffs, file changes)
- Claude Code native session logs from `~/.claude/projects/{project-dir}/{session-id}.jsonl`
- Code quality metrics (tests, compilation, standards)
- Your direct feedback about the session

It produces a structured retrospective report with:

- Quantitative metrics (files changed, test coverage, tool usage)
- Qualitative insights (what worked, what didn't, why)
- Actionable recommendations for future sessions
- Reusable patterns and anti-patterns

## When to Use

Invoke this skill when you want to:

- Review what was accomplished in a session
- Understand what went well and what could improve
- Get feedback on workflow effectiveness
- Document lessons learned for future reference
- Analyze a particularly successful or challenging session

### Example Invocations

**Natural language:**

- "Can you do a retrospective on what we just accomplished?"
- "How did that session go?"
- "Analyze the last 2 hours of work"
- "What could we improve about how we worked together?"

**Direct skill invocation:**

```
/skill retrospecting
```

## What to Expect

### Process Flow

1. **Scope Definition** - You'll be asked:
   - Time range or commit range for the session
   - What you were trying to accomplish
   - How detailed of an analysis you need (quick/standard/comprehensive)

2. **Data Collection** - The skill will:
   - Analyze git history for the session timeframe
   - Parse Claude Code native session logs from `~/.claude/projects/{project-dir}/{session-id}.jsonl`
   - Examine changed files and code quality
   - Gather your feedback through targeted questions

3. **Analysis & Report** - You'll receive:
   - Structured retrospective report (markdown format)
   - Evidence-based findings with specific examples
   - Prioritized recommendations
   - Patterns worth replicating or avoiding

4. **Validation & Refinement** - You can:
   - Confirm the analysis matches your experience
   - Add pain points that were missed
   - Prioritize which improvements matter most
   - Request configuration updates based on findings

5. **Cleanup** (Optional) - You can:
   - Delete the session log files after analysis
   - Keep them for future reference

### Time Investment

- **Quick retrospective**: 5-10 minutes (brief summary)
- **Standard retrospective**: 15-20 minutes (balanced analysis)
- **Comprehensive retrospective**: 30+ minutes (detailed deep-dive)

The skill will recommend a depth based on your session size (commits, log volume, complexity).

## Output Format

### Report Types

**Quick Retrospective** - Concise summary with:

- Highlights (top successes)
- Challenges (main issues)
- Key learnings
- 2-3 action items

**Comprehensive Retrospective** - Detailed analysis with:

- Executive summary with metrics
- Success patterns with evidence
- Pain points with root causes
- Workflow optimization analysis
- Prioritized recommendations
- Patterns for future reference

### Report Storage

All reports are saved to:

```
${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/reports/YYYY-MM-DD-description-SESSION_ID.md
```

Example:

```
${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/reports/2025-10-23-authentication-refactor-3be2bbaf.md
```

The session ID links the report to the original conversation logs for traceability.

## File Organization

```
${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/
├── README.md                    # This file (user documentation)
├── SKILL.md                     # Skill instructions (for Claude)
├── contexts/
│   └── session-analytics.md    # Analysis framework (auto-loaded)
├── templates/
│   └── retrospective-templates.md  # Report templates (auto-loaded)
├── reports/
│   └── YYYY-MM-DD-*.md         # Generated retrospective reports
└── scripts/
    └── analyze-session-logs.sh # Session log analysis helper

Session logs are stored by Claude Code in:
~/.claude/projects/{project-dir}/{session-id}.jsonl
(where {project-dir} is your working directory path with slashes replaced by dashes)
```

## Configuration

### Retrospective Depth

You can request a specific depth level:

- **Quick**: Fast summary for simple sessions
- **Standard**: Balanced analysis for typical sessions
- **Comprehensive**: Deep dive for complex or significant sessions
- **Custom**: Focus on specific areas you define

The skill will suggest an appropriate depth based on session metrics, but you can override.

### Focus Areas

You can request focus on specific aspects:

- "Focus on code quality and testing"
- "Analyze communication effectiveness"
- "Look for security considerations we might have missed"
- "Compare this session to previous similar work"

## Integration with Other Features

### Configuration Improvements

If the retrospective identifies patterns that should become standard practice, the skill will:

1. Suggest updates to `.claude/CLAUDE.md`, `SKILL.md` files, or agent definitions
2. Show you the proposed changes
3. Apply them with your approval

This creates a continuous improvement loop.

### Pattern Libraries

Successful patterns and anti-patterns are extracted into reusable libraries (future feature):

```
${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/patterns/
├── successful-patterns.md
└── anti-patterns-to-avoid.md
```

### Log Cleanup

After generating a report, you can optionally delete the session logs to reduce repository size. The retrospective report preserves key insights, so logs are often not needed afterward.

## Tips for Best Results

### Provide Clear Session Goals

When asked "What were you trying to accomplish?", be specific:

- **Good**: "Refactor authentication to use biometric providers and add unit tests"
- **Less helpful**: "Work on authentication"

### Be Honest About Pain Points

The skill asks for feedback about friction areas. Candid input leads to better insights:

- Where did you get confused?
- What took longer than expected?
- What would you change about the workflow?

### Use Retrospectives Regularly

- **After major features**: Capture complex implementation insights
- **Weekly/sprint boundaries**: Track progress and improvement trends
- **After challenging sessions**: Learn from difficulties
- **After smooth sessions**: Identify what made them effective

### Follow Up on Recommendations

Retrospectives are most valuable when recommendations are acted upon:

- Implement high-priority improvements in next session
- Update configuration files with better practices
- Share learnings with team (if applicable)

## Troubleshooting

### "Session logs not found"

- Session logs are automatically generated by Claude Code in `~/.claude/projects/{project-dir}/`
- Project directory is derived from your working directory (slashes replaced with dashes)
- Example: `/Users/user/project` → `~/.claude/projects/-Users-user-project/`
- You can still do a retrospective using git history + your feedback if logs are unavailable

### "Report seems generic"

- Provide more specific session goals upfront
- Add detailed feedback when prompted
- Request a comprehensive retrospective for deeper analysis

### "Analysis doesn't match my experience"

- The validation step (Step 6) is exactly for this
- Tell the skill what's missing or incorrect
- It will refine the analysis based on your input

### "Context window exceeded"

- Request a "quick" retrospective for large sessions
- The skill will summarize logs instead of reading them fully
- Focus on specific areas rather than comprehensive analysis

## Privacy & Security

### What Data is Analyzed

- Git commits and diffs visible in your repository
- Claude Code native session logs from `~/.claude/projects/{project-dir}/{session-id}.jsonl`
- File contents of changed files
- Your explicit feedback responses

### Data Storage

- All analysis happens locally in your session
- Reports stored in your repository (`${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/reports/`)
- No data sent to external services
- Logs can be deleted after retrospective if desired

### Sensitive Information

If your session involved sensitive data:

- Review generated reports before committing them
- Retrospective can be run without committing reports
- You can request specific sections be excluded from the report

## Examples

### Example 1: Quick Post-Session Review

**User**: "Can you do a quick retrospective on what we just did?"

**Process**:

1. Skill checks: 8 commits, 3 log files, ~45 minutes of work
2. Suggests: Quick retrospective (5-10 min)
3. Analyzes git changes, skims logs, asks 2-3 questions
4. Generates quick report with highlights, challenges, learnings
5. Takes ~7 minutes total

### Example 2: Comprehensive Feature Analysis

**User**: "I want a detailed retrospective on the entire authentication refactor we did today"

**Process**:

1. Skill checks: 34 commits, 12 log files, ~4 hours of work
2. Recommends: Comprehensive retrospective (30 min)
3. Deep analysis of git history, detailed log parsing, code quality metrics
4. Extensive user feedback gathering (7-10 questions)
5. Generates full report with metrics, patterns, recommendations
6. Suggests 3 configuration improvements for `.claude/CLAUDE.md`
7. Offers to delete logs after report validated

### Example 3: Focus on Specific Issues

**User**: "Analyze why testing took so long this session"

**Process**:

1. Skill identifies custom focus: testing workflow
2. Examines test-related commits and file changes
3. Searches logs for test failures, retry patterns
4. Asks targeted questions about testing pain points
5. Generates focused report on testing efficiency with specific recommendations

## Future Enhancements

Planned improvements to this skill:

- Automated CI integration (run retrospectives on PR merge)
- Trend analysis across multiple sessions
- Pattern library with searchable best practices
- Comparative analysis (this session vs similar past sessions)
- Team retrospectives (multi-user session analysis)

## Feedback

Found an issue or have a suggestion? Update the skill:

- Modify `${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/SKILL.md` (Claude's instructions)
- Modify this README.md (user documentation)
- Add context files in `contexts/` for additional analysis frameworks
- Update templates in `templates/` for different report formats
