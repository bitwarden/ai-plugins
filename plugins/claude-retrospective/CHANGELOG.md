# Changelog

All notable changes to the Claude Retrospective Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-03

### Added

- Initial release of `claude-retrospective` plugin
- **Multi-source data collection system**:
  - Git history analysis (commits, diffs, file changes)
  - Claude Code native session log access from `~/.claude/projects/{project-dir}/{session-id}.jsonl`
  - Code quality metrics (test coverage, compilation status, standards compliance)
  - Direct user feedback collection through targeted questions
  - Sub-agent feedback integration when specialized agents were used
- **Three-tier analysis depth system**:
  - Quick retrospective (5-10 min): Stats only, error summary, 2-3 questions
  - Standard retrospective (15-20 min): Full commits, selective diffs, metadata, 5-7 questions
  - Comprehensive retrospective (30+ min): Everything including full logs, diffs, quality metrics, 8-10 questions
  - Automatic depth recommendation based on session size (commits, log volume, complexity)
- **Session assessment framework**:
  - Pre-analysis session size calculation
  - Intelligent depth suggestion to user with override capability
  - Early exit clause for quick summaries regardless of session size
- **Session log extraction toolkit** (`extracting-session-data` skill):
  - `locate-logs.sh`: Find log directories and session file paths
  - `list-sessions.sh`: Enumerate sessions with metadata (ID, size, lines, date, branch)
  - `extract-data.sh`: Parse JSONL logs with 8 extraction types:
    - Metadata (session info, timestamps, branch, working dir)
    - User prompts (all user messages)
    - Tool usage (tool call statistics)
    - Errors (failed tool calls with timestamps)
    - Thinking blocks (if extended thinking enabled)
    - Text responses (assistant responses only)
    - Statistics (message counts, tool calls, errors)
    - All (combined extraction)
  - `filter-sessions.sh`: Filter sessions by 8 criteria:
    - Date range (--since, --until)
    - Git branch (--branch)
    - File size (--min-size, --max-size)
    - Line count (--min-lines, --max-lines)
    - Error presence (--has-errors)
    - Keyword search (--keyword)
  - Output format options: table, JSON, CSV, list, paths
  - Context-aware processing: checks size before loading, prevents context overflow
- **Git session analysis toolkit** (`analyzing-git-sessions` skill):
  - Time range parsing ("last 2 hours", "since 10am", "today", absolute timestamps)
  - Commit range support ("abc123..def456", "HEAD~5..HEAD", branch comparisons)
  - Commit history extraction with authors and timestamps
  - Change statistics (insertions/deletions by file, author breakdown)
  - File categorization (new, deleted, renamed, modified with magnitude)
  - Key file identification (prioritized by change size, file type, architecture impact)
  - Three output formats:
    - Concise: Stats only, no diffs
    - Detailed: Top 3-5 file diffs
    - Code Review: Full analysis grouped by module
  - Context overflow protection (limits diffs for large sessions)
- **Quantitative analysis framework**:
  - Session scope metrics (duration, tasks completed, files changed)
  - Quality indicators (compilation rate, test coverage, standard compliance)
  - Efficiency metrics (tool success rate, rework rate, completion rate)
  - User experience data (satisfaction, friction points)
- **Qualitative assessment framework**:
  - Success pattern identification with evidence
  - Problematic pattern detection with root cause analysis
  - Reusable solution extraction for future reference
  - Context-specific learnings for project type
- **Two report templates**:
  - Quick retrospective: Concise summary with highlights, challenges, key learnings, 2-3 action items
  - Comprehensive retrospective: Full analysis with executive summary, metrics, success patterns, pain points, workflow analysis, prioritized recommendations, patterns library
- **Evidence-based reporting standards**:
  - Every claim backed by specific examples
  - All recommendations include implementation guidance (what, why, how, impact)
  - File:line references for code locations
  - Clear prioritization (high vs medium vs low impact)
  - Balanced acknowledgment of successes and improvements
- **Configuration improvement loop**:
  - Identification of patterns that should become standard practice
  - Specific suggestions for `.claude/CLAUDE.md`, `SKILL.md`, or agent definition updates
  - Draft proposed changes with rationale
  - User approval workflow before applying changes
  - Document suggestions in report if user declines
- **Context budget management system**:
  - Budget thresholds defined (skill instructions: 6-8K, small logs: 2-5K, large logs: 10-50K+)
  - Adaptive strategy based on remaining budget:
    - High budget (>100K tokens): Comprehensive mode safe, read full logs if <2000 lines
    - Medium budget (50-100K tokens): Standard mode default, summarize logs, selective diffs
    - Low budget (<50K tokens): Force quick mode, bash-only summarization, stats only
  - Context preservation tactics (extract and discard, synthesize early, progressive refinement, spot sampling)
  - Emergency fallback for context limit (stop collection, generate from gathered data, note limitations)
- **Sub-agent integration framework**:
  - Feedback collection from specialized agents that participated
  - Synthesis of sub-agent feedback into retrospective
  - Identification of coordination issues and handoff problems
  - Recognition of successful collaboration patterns
- **Eight-step working process**:
  1. Quick session assessment (check size, suggest depth, allow override)
  2. Establish session scope (boundaries, goals, depth confirmation)
  3. Gather data (depth-specific collection based on mode)
  4. Analyze data (metrics, indicators, patterns, quality)
  5. Generate insights (successes, problems, opportunities, patterns)
  6. Create report (structured, evidence-based, actionable)
  7. Gather user validation (match experience, missed pain points, priorities)
  8. Suggest configuration improvements (draft, present, apply/document)
  9. Session archive information (log locations, retention policy)
- **Report storage system**:
  - Directory: `${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/reports/`
  - Filename format: `YYYY-MM-DD-session-description-SESSION_ID.md`
  - ISO date format for chronological sorting
  - Session ID for traceability to original logs
- **Auto-loaded context files**:
  - `contexts/session-analytics.md`: Comprehensive framework for analyzing sessions (data sources, metrics, analysis methods)
  - `templates/retrospective-templates.md`: Standardized report templates for different depths
- **Anti-pattern documentation**:
  - Don't: Generate retrospectives without data, vague recommendations, only negatives, ignore user priorities, overly long reports, analyze without context
  - Do: Ground in evidence, provide specific guidance, balance positive/negative, align with priorities, concise with prominent insights, understand context first
- **Success criteria framework**:
  - Inform: User learns about workflow
  - Guide: Clear next steps
  - Motivate: Recognition encourages good practices
  - Focus: Prioritization guides effort investment
  - Enable: Frameworks/patterns for future sessions
- **Dependencies management**:
  - Bash 4.0+ required
  - jq (JSON parser) required with installation instructions
  - Automatic dependency checking with helpful error messages
- Plugin manifest with metadata and skill registration
- Comprehensive README documentation with use cases, examples, and troubleshooting

---

## Version Format

Plugin version tracks retrospective system changes:

- **Major version**: Breaking changes to report templates, data collection methods, or skill interfaces
- **Minor version**: New analysis features, additional data sources, new report types, skill enhancements
- **Patch version**: Bug fixes, clarifications, documentation improvements, script refinements
