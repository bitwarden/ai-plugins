# Claude Retrospective Plugin

Comprehensive analysis of Claude Code sessions to identify successful patterns, problematic areas, and opportunities for improvement through multi-source data collection and evidence-based insights.

## Overview

The Claude Retrospective plugin provides systematic session analysis capabilities for Claude Code, helping you understand what worked well, what didn't, and how to continuously improve your AI-assisted development workflows. By examining git history, conversation logs, code quality metrics, and user feedback, it generates actionable retrospective reports that drive continuous improvement.

## Features

### Multi-Source Data Collection

Systematically gathers data from all available sources:

- **Git History**: Commits, diffs, file changes during session timeframe
- **Claude Native Session Logs**: Conversation transcripts from `~/.claude/projects/{project-dir}/{session-id}.jsonl`
- **Code Quality Metrics**: Test coverage, compilation status, standard compliance
- **User Feedback**: Direct input about goals, satisfaction, and pain points
- **Sub-agent Analysis**: Feedback from specialized agents used during the session

### Flexible Analysis Depths

Choose the right level of analysis for your needs:

| Depth             | Duration  | Use Case                             | Data Collection                                               |
| ----------------- | --------- | ------------------------------------ | ------------------------------------------------------------- |
| **Quick**         | 5-10 min  | Simple sessions, rapid feedback      | Git stats only, error summary, 2-3 questions                  |
| **Standard**      | 15-20 min | Typical sessions, balanced analysis  | Full commits, selective diffs, metadata, 5-7 questions        |
| **Comprehensive** | 30+ min   | Complex sessions, deep-dive analysis | Everything: full logs, diffs, quality metrics, 8-10 questions |

The skill automatically recommends an appropriate depth based on session size (commits, log volume) but allows user override.

### Evidence-Based Insights

Every finding is backed by concrete evidence:

- **Quantitative Metrics**: Session scope, quality indicators, efficiency metrics
- **Qualitative Assessment**: Successful patterns, problematic areas, root causes
- **Specific References**: File:line citations for all claims
- **Actionable Recommendations**: What, why, how, and expected impact

### Configuration Improvement Loop

Retrospectives can identify patterns that should become standard practice:

1. Analyze session to identify improvement opportunities
2. Suggest specific updates to `.claude/CLAUDE.md`, `SKILL.md`, or agent definitions
3. Show proposed changes to user
4. Apply with approval, creating continuous improvement cycle

### Context-Aware Processing

Intelligent handling of large sessions to prevent context overflow:

- Checks session size before loading data
- Adjusts depth automatically based on available context budget
- Uses targeted extraction for large log files (>2000 lines)
- Progressive disclosure: start high-level, drill down on request

## Installation

### Add Bitwarden Marketplace (if not already added)

```bash
/plugin marketplace add bitwarden/ai-marketplace
```

### Install the Plugin

```bash
/plugin install claude-retrospective@bitwarden-marketplace
```

## Usage

### Basic Invocation

**Natural language**:

- "Can you do a retrospective on what we just accomplished?"
- "How did that session go?"
- "Analyze the last 2 hours of work"
- "What could we improve about how we worked together?"

**Direct skill invocation**:

```bash
/skill retrospecting
```

### Use Cases

#### 1. Post-Session Review

**Scenario**: You've completed a coding session and want to understand what worked well and what could be improved.

**Usage**:

```
Do a retrospective on the last 2 hours of work
```

**Output**:

- Quantitative metrics (commits, files changed, test coverage)
- Success patterns identified with evidence
- Pain points with root causes
- Prioritized recommendations for future sessions

---

#### 2. Feature Implementation Analysis

**Scenario**: You've completed a significant feature implementation and want detailed analysis of the approach and outcomes.

**Usage**:

```
I want a comprehensive retrospective on the authentication refactor we completed today
```

**Output**:

- Detailed git analysis with commit-by-commit review
- Code quality assessment
- Architecture decisions made and their rationale
- Testing coverage and quality
- Communication effectiveness
- Reusable patterns extracted for future use

---

#### 3. Troubleshooting Workflow Issues

**Scenario**: A session felt inefficient or frustrating, and you want to identify specific bottlenecks.

**Usage**:

```
Analyze why testing took so long in this session
```

**Output**:

- Focused analysis on testing workflow
- Identification of specific delays (test failures, environment issues, unclear requirements)
- Root cause analysis for each bottleneck
- Specific recommendations to improve testing efficiency

---

#### 4. Pattern Library Building

**Scenario**: You want to extract successful approaches from a particularly effective session to replicate in future work.

**Usage**:

```
This session went really smoothly - help me identify the patterns we should keep using
```

**Output**:

- Successful patterns documented with examples
- Environmental factors that contributed to success
- Recommendations for codifying patterns in configuration files
- Suggestions for `.claude/CLAUDE.md` or skill updates

---

#### 5. Multi-Session Trend Analysis

**Scenario**: You want to analyze patterns across multiple sessions to identify systemic issues or improvements.

**Usage**:

```
Analyze all sessions from the last week and identify trends
```

**Output**:

- Aggregated metrics across sessions
- Common success patterns and recurring issues
- Workflow trends (improving, declining, stable)
- Strategic recommendations for long-term improvement

## Skills Included

### retrospecting

**Description**: Performs comprehensive analysis of Claude Code sessions, examining git history, conversation logs, code changes, and user feedback to generate actionable retrospective reports.

**Working Process**:

1. **Session Assessment**: Determine appropriate analysis depth based on session size
2. **Scope Definition**: Establish time/commit range and session goals
3. **Data Collection**: Gather git history, logs, code quality metrics, user feedback
4. **Analysis**: Calculate metrics, identify patterns, assess communication effectiveness
5. **Report Generation**: Create structured report using appropriate template
6. **Validation**: Gather user feedback on report accuracy
7. **Configuration Improvements**: Suggest updates to Claude configuration files
8. **Archive Information**: Document where session logs are stored

**Output**: Structured markdown reports saved to `${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/reports/`

---

### extracting-session-data

**Description**: Locates, lists, filters, and extracts structured data from Claude Code native session logs stored in `~/.claude/projects/{project-dir}/{session-id}.jsonl`.

**Capabilities**:

- **locate-logs.sh**: Find log directories and session file paths
- **list-sessions.sh**: Enumerate sessions with metadata (ID, size, lines, date, branch)
- **extract-data.sh**: Parse JSONL logs and extract specific data types:
  - Metadata (session info, timestamps, branch)
  - User prompts
  - Tool usage statistics
  - Errors and failed tool calls
  - Thinking blocks (if extended thinking enabled)
  - Text responses
  - Session statistics
- **filter-sessions.sh**: Find sessions by criteria (date range, branch, size, errors, keywords)

**Key Principle**: Extracts raw data only - returns data to calling skills for analysis without interpretation.

---

### analyzing-git-sessions

**Description**: Analyzes git commits and changes within a timeframe or commit range, providing structured summaries for code review, retrospectives, or work logs.

**Capabilities**:

- Parse time ranges ("last 2 hours", "since 10am") or commit ranges ("abc123..def456")
- Extract commit history with authors and timestamps
- Generate change statistics (insertions/deletions by file)
- Identify key files for detailed analysis (prioritized by change size)
- Provide selective diffs based on depth (concise/detailed/code review)
- Categorize files by type (source, test, config, docs)
- Handle large sessions with context overflow protection

**Output Formats**:

- **Concise**: Stats only, no diffs
- **Detailed**: Top 3-5 file diffs
- **Code Review**: Full analysis grouped by module

## Report Structure

### Quick Retrospective Template

```markdown
## Session Summary

- Duration: X hours
- Goals: [What you were trying to accomplish]
- Outcome: [Success/Partial/Issues]

## Highlights

- [Top 2-3 successes]

## Challenges

- [Main 1-2 issues encountered]

## Key Learnings

- [Most important insight]

## Action Items

1. [First priority improvement]
2. [Second priority improvement]
```

### Comprehensive Retrospective Template

```markdown
## Executive Summary

- Session scope metrics
- Overall assessment
- Key achievements

## Session Metrics

[Quantitative data table]

## What Went Well

[Success patterns with evidence]

## Pain Points

[Issues with root cause analysis]

## Workflow Analysis

- Communication effectiveness
- Tool usage patterns
- Decision-making quality

## Code Quality Assessment

- Test coverage
- Compilation success
- Standard compliance

## Recommendations

[Prioritized by impact: High/Medium/Low]

## Patterns for Future Reference

- Successful approaches to replicate
- Anti-patterns to avoid

## Configuration Suggestions

[Proposed updates to .claude files]
```

## File Organization

```
plugins/claude-retrospective/
├── .claude-plugin/
│   └── plugin.json                       # Plugin manifest
├── skills/
│   ├── retrospecting/
│   │   ├── SKILL.md                      # Main retrospective skill
│   │   ├── README.md                     # User documentation
│   │   ├── contexts/
│   │   │   └── session-analytics.md     # Analysis framework (auto-loaded)
│   │   ├── templates/
│   │   │   └── retrospective-templates.md # Report templates (auto-loaded)
│   │   ├── reports/                      # Generated reports (YYYY-MM-DD-*.md)
│   │   └── scripts/
│   │       └── analyze-session-logs.sh  # Helper script
│   ├── extracting-session-data/
│   │   ├── SKILL.md                      # Log extraction skill
│   │   ├── README.md                     # Extraction documentation
│   │   └── scripts/
│   │       ├── locate-logs.sh           # Find log directories
│   │       ├── list-sessions.sh         # List all sessions
│   │       ├── extract-data.sh          # Extract specific data types
│   │       └── filter-sessions.sh       # Filter by criteria
│   └── analyzing-git-sessions/
│       ├── SKILL.md                      # Git analysis skill
│       ├── README.md                     # Git analysis documentation
│       └── contexts/
│           └── example-outputs.md       # Example git summaries
└── README.md                             # This file
```

## Tips for Best Results

### Provide Clear Session Goals

When asked "What were you trying to accomplish?", be specific:

- ✅ **Good**: "Refactor authentication to use biometric providers and add unit tests"
- ❌ **Less helpful**: "Work on authentication"

### Be Honest About Pain Points

Candid feedback leads to better insights:

- Where did you get confused?
- What took longer than expected?
- What would you change about the workflow?

### Use Retrospectives Regularly

- **After major features**: Capture complex implementation insights
- **Weekly/sprint boundaries**: Track progress and improvement trends
- **After challenging sessions**: Learn from difficulties
- **After smooth sessions**: Identify what made them effective

### Follow Up on Recommendations

Retrospectives are most valuable when acted upon:

- Implement high-priority improvements in next session
- Update configuration files with better practices
- Share learnings with team (if applicable)

## Dependencies

**Required**:

- `bash` (v4.0+)
- `jq` (JSON parser for log extraction)

Scripts check for `jq` and provide installation instructions if missing:

```bash
brew install jq  # macOS
apt-get install jq  # Linux
```

## Privacy & Security

### What Data is Analyzed

- Git commits and diffs visible in your repository
- Claude Code native session logs from `~/.claude/projects/{project-dir}/`
- File contents of changed files
- Your explicit feedback responses

### Data Storage

- All analysis happens locally in your session
- Reports stored in your repository (`.claude/skills/retrospecting/reports/`)
- No data sent to external services
- Session logs managed by Claude Code (can be deleted after retrospective if desired)

### Sensitive Information

If your session involved sensitive data:

- Review generated reports before committing them
- Retrospectives can be run without committing reports
- You can request specific sections be excluded from the report

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

- The validation step is designed for this feedback
- Tell the skill what's missing or incorrect
- It will refine the analysis based on your input

### "Context window exceeded"

- Request a "quick" retrospective for large sessions
- The skill will summarize logs instead of reading them fully
- Focus on specific areas rather than comprehensive analysis

## Contributing

Contributions welcome! Please follow:

- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com)
- Repository standards in root `README.md`
- Code quality requirements in `.editorconfig`

## Support

- **Issues**: [GitHub Issues](https://github.com/bitwarden/ai-plugins/issues)
- **Documentation**: [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/)
- **Marketplace**: [Bitwarden AI Marketplace](https://github.com/bitwarden/ai-plugins)
