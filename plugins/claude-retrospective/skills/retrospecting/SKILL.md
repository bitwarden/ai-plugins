---
name: retrospecting
description: Performs comprehensive analysis of Claude Code sessions, examining git history, conversation logs, code changes, and gathering user feedback to generate actionable retrospective reports with insights for continuous improvement.
---

# Session Retrospective Skill

## Auto-Loaded Context

**Session Analytics**: [`contexts/session-analytics.md`](contexts/session-analytics.md) - Provides comprehensive framework for analyzing sessions, including data sources, metrics, and analysis methods.

**Retrospective Templates**: [`templates/retrospective-templates.md`](templates/retrospective-templates.md) - Standardized report templates for different retrospective depths.

## Core Responsibilities

### 1. Multi-Source Data Collection

Systematically gather data from all available sources:

- **Git History**: Commits, diffs, file changes during session timeframe
- **Claude Logs**: Conversation transcripts, tool usage, decision patterns
- **Project Files**: Test coverage, code quality, compilation status
- **User Feedback**: Direct input about goals, satisfaction, pain points
- **Sub-agent Interactions**: When sub-agents were used, gather their feedback

### 2. Quantitative Analysis

Calculate measurable metrics:

- Session scope (duration, tasks completed, files changed)
- Quality indicators (compilation rate, test coverage, standard compliance)
- Efficiency metrics (tool success rate, rework rate, completion rate)
- User experience data (satisfaction, friction points)

### 3. Qualitative Assessment

Identify patterns and insights:

- Successful approaches that led to good outcomes
- Problematic patterns that caused issues or delays
- Reusable solutions worth extracting for future use
- Context-specific learnings applicable to this project type

### 4. Report Generation

Create structured retrospective report using appropriate template:

- **Quick Retrospective**: Brief session wrap-ups (5-10 minutes)
- **Comprehensive Retrospective**: Detailed analysis for significant sessions
- Choose template based on session complexity and user needs

## Working Process

### Step 0: Quick Session Assessment

Before gathering data, determine the appropriate analysis depth:

1. **Check session size**:

   ```bash
   # Count recent commits
   git log --oneline --since="1 hour ago" | wc -l

   # List session log files with metadata
   ${CLAUDE_PROJECT_DIR}/.claude/skills/extracting-session-data/scripts/list-sessions.sh --sort date | head -5
   ```

2. **Suggest depth to user** based on metrics:
   - **Quick** (<10 commits, <5MB logs): "5-10 min lightweight analysis"
   - **Standard** (10-25 commits, 5-20MB logs): "15-20 min balanced analysis"
   - **Comprehensive** (>25 commits, >20MB logs): "30+ min deep-dive analysis"

3. **Let user override**: "Based on [X commits, Y MB logs], I recommend a [MODE] retrospective (~Z minutes). Does this work for you, or would you prefer a different depth?"

4. **Early exit clause**: If user says "just a quick summary" or "high-level overview", automatically use Quick mode regardless of session size.

### Step 1: Establish Session Scope

1. Ask user to define session boundaries (time range or commit range)
2. Clarify session goals: "What were you trying to accomplish?"
3. Confirm retrospective depth from Step 0

### Step 2: Gather Data

Execute data collection based on confirmed depth mode:

#### Depth-Specific Data Collection

**Quick Mode**:

- Git: `git diff <start>..<end> --stat` only (no full diffs)
- Logs: Extract statistics and errors only via `extracting-session-data` skill
- Files: Check compilation status only
- User: 2-3 targeted questions
- Skip: Sub-agent feedback, detailed file analysis

**Standard Mode**:

- Git: Full commit history + stats, selective diffs for key files
- Logs: Extract metadata, statistics, tool-usage, and errors via `extracting-session-data` skill
- Files: Quality metrics for changed files
- User: 5-7 questions covering main areas
- Include: Sub-agent feedback if applicable

**Comprehensive Mode**:

- Git: Everything (full logs, diffs, file analysis)
- Logs: Extract all data types via `extracting-session-data` skill, may read full logs if <500 lines
- Files: Deep analysis including tests, architecture compliance
- User: Extensive feedback (8-10 questions)
- Include: All sub-agent feedback, pattern extraction

#### Git Analysis

Use the `analyzing-git-sessions` skill to collect git data:

**Quick Mode**: Request "concise" output (stats only, no diffs)
**Standard Mode**: Request "detailed" output for key files
**Comprehensive Mode**: Request "code review" format for full analysis

Invoke skill with session timeframe:

```
Skill: analyzing-git-sessions
Input: "<start-time> to <end-time>" or "<start-commit>..<end-commit>"
Depth: [concise|detailed|code-review] based on retrospective mode
```

The skill will return structured git metrics needed for retrospective analysis.

#### Log Processing (Size-Aware)

Use the `extracting-session-data` skill to access Claude Code native session logs efficiently.

1. **List Available Sessions**:

   ```bash
   # List all sessions with metadata (size, lines, date, branch)
   ${CLAUDE_PROJECT_DIR}/.claude/skills/extracting-session-data/scripts/list-sessions.sh
   ```

2. **Check Session Size**:

   ```bash
   # Get statistics for specific session
   ${CLAUDE_PROJECT_DIR}/.claude/skills/extracting-session-data/scripts/extract-data.sh \
       --type statistics --session SESSION_ID
   ```

3. **Extract Data Based on Session Size and Mode**:

   **Quick Mode** (or any session >2000 lines):

   ```bash
   # Extract only statistics and errors
   extract-data.sh --type statistics --session SESSION_ID
   extract-data.sh --type errors --session SESSION_ID --limit 10
   ```

   **Standard Mode** (sessions 500-2000 lines):

   ```bash
   # Extract metadata, statistics, tool usage, and errors
   extract-data.sh --type metadata --session SESSION_ID
   extract-data.sh --type statistics --session SESSION_ID
   extract-data.sh --type tool-usage --session SESSION_ID
   extract-data.sh --type errors --session SESSION_ID
   ```

   **Comprehensive Mode** (sessions <500 lines):

   ```bash
   # Extract all available data
   extract-data.sh --type all --session SESSION_ID

   # Or read full log file if needed for detailed analysis
   # (Only for small sessions - check line count first!)
   ```

4. **Multi-Session Analysis**:

   ```bash
   # Filter sessions by criteria
   filter-sessions.sh --since "7 days ago" --branch main

   # Extract data from all filtered sessions (omit --session flag)
   extract-data.sh --type statistics  # Runs on all sessions
   ```

5. **Synthesize Extracted Data**:
   After extraction, synthesize data into compact summary (max 200 lines) before continuing to analysis.

**Path Calculation**: The `extracting-session-data` skill handles all path calculations automatically. Session logs are stored in `~/.claude/projects/{project-identifier}/` where the identifier is derived from the working directory path.

#### Project Analysis

Examine changed files, tests, documentation (depth-appropriate)

#### User Feedback

Prompt for direct feedback on session experience (question count based on depth mode)

#### Sub-agent Feedback

If sub-agents were used, invoke them to gather their perspective (Standard/Comprehensive modes only)

### Step 3: Analyze Data

Apply session-analytics.md framework:

- Calculate quantitative metrics
- Identify success and problem indicators
- Extract patterns (successful approaches and anti-patterns)
- Assess communication effectiveness and technical quality

### Step 4: Generate Insights

Synthesize analysis into actionable insights:

- What went well and why (specific evidence)
- What caused problems and their root causes
- Opportunities for improvement (prioritized by impact)
- Patterns to replicate or avoid in future sessions

### Step 5: Create Report

Use appropriate template from retrospective-templates.md:

- Structure findings clearly with evidence
- Include specific file:line references where relevant
- Prioritize recommendations by impact and feasibility
- Make all suggestions actionable and specific

### Step 6: Gather User Validation

Present report and ask:

- Does this match your experience?
- Are there other pain points we missed?
- Which improvements would be most valuable to you?

### Step 7: Suggest Configuration Improvements

If the retrospective identifies areas for improvement in Claude or Agent interactions:

1. Analyze whether improvements could be codified in configuration files:
   - **CLAUDE.md**: Core directives, workflow practices, communication patterns
   - **SKILL.md files**: Skill-specific instructions, working processes, anti-patterns
   - **Agent definition files**: Agent prompts, tool usage, coordination patterns
2. Draft specific, actionable suggestions for configuration updates:
   - Quote the current text that should be modified (if updating existing content)
   - Provide the proposed new or additional text
   - Explain the rationale based on retrospective findings
3. Present suggestions to the user:
   - "Based on this retrospective, I've identified potential improvements to [file]. Would you like me to implement these changes?"
   - Show the specific changes that would be made
4. If the user approves:
   - Apply the changes using the Edit tool
   - Confirm what was updated
5. If the user declines:
   - Document the suggestions in the retrospective report for future consideration

### Step 8: Session Archive Information

After the retrospective report is created and validated:

1. Inform the user where session logs are stored:
   - "Session logs are permanently stored in `~/.claude/projects/{project-dir}/{session-id}.jsonl`"
   - "These logs are managed by Claude Code and should not be deleted manually"
2. Explain that retrospective reports are saved separately in:
   - `${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/reports/`
3. Note that Claude Code manages session log retention automatically

## Output Standards

### Report Quality Requirements

- **Evidence-Based**: Every claim backed by specific examples
- **Actionable**: All recommendations include implementation guidance
- **Specific**: Avoid vague statements; use concrete examples
- **Prioritized**: Clear indication of high vs low impact items
- **Balanced**: Acknowledge successes while identifying improvements

### File References

Use `file:line_number` format when referencing specific code locations.

### Metrics Presentation

Present metrics in clear tables or lists with context for interpretation.

### Recommendations Format

Each recommendation should include:

- **What**: Specific action to take
- **Why**: Root cause or rationale
- **How**: Implementation approach
- **Impact**: Expected benefit

## Integration with Sub-agents

When sub-agents were used during the session:

### Feedback Collection

Invoke each sub-agent that participated with prompts like:

- "What aspects of this session worked well for you?"
- "What instructions or context were unclear?"
- "What tools or capabilities did you need but lack?"
- "How could coordination with Claude be improved?"

### Synthesis

Incorporate sub-agent feedback into retrospective:

- Identify coordination issues or handoff problems
- Note gaps in instruction clarity or context
- Recognize successful collaboration patterns
- Recommend improvements to sub-agent usage

## Context Budget Management

Monitor context usage throughout retrospective to prevent overflow:

### Budget Thresholds

- **Skill instructions**: ~6-8K tokens (this file + auto-loaded contexts)
- **Small log file**: 2-5K tokens per file
- **Large log file**: 10-50K+ tokens if read fully
- **Git diffs**: 5-20K tokens for large changes
- **User conversation**: Variable (2-10K tokens)

### Adaptive Strategy Based on Remaining Budget

**High Budget (>100K tokens remaining)**:

- Safe to use Comprehensive mode
- Read full logs if <2000 lines
- Include full git diffs
- Load detailed metrics from session-analytics.md if needed

**Medium Budget (50-100K tokens remaining)**:

- Use Standard mode by default
- Summarize logs before reading (use bash extraction)
- Selective git diffs for key files only
- Skip extended context loading

**Low Budget (<50K tokens remaining)**:

- Force Quick mode regardless of session size
- Bash-only log summarization (no full reads)
- Git stats only, no diffs
- Warn user: "Limited context available - providing focused analysis on key areas only"

### Context Preservation Tactics

1. **Extract and discard**: Pull key metrics from large files, discard verbose source immediately
2. **Synthesize early**: Create compact summaries (max 200 lines) before continuing
3. **Progressive refinement**: Start high-level, drill down only where user indicates interest
4. **Spot sampling**: Read representative sections rather than entire files

### Emergency Fallback

If approaching context limit during analysis:

1. Stop data collection immediately
2. Generate report from data gathered so far
3. Note in report: "Analysis limited by context constraints - [specific areas not covered]"
4. Offer to do targeted follow-up on specific aspects in new conversation

## Anti-Patterns to Avoid

**Don't**:

- Generate retrospectives without gathering actual data
- Make vague, non-actionable recommendations
- Focus only on negatives; acknowledge what worked well
- Ignore user's stated priorities and goals
- Create overly long reports that bury key insights
- Analyze sessions without understanding the context and goals

**Do**:

- Ground analysis in concrete evidence from session data
- Provide specific, actionable recommendations with implementation guidance
- Balance positive recognition with improvement opportunities
- Align recommendations with user's priorities
- Create concise reports that highlight key insights prominently
- Understand session context before analyzing effectiveness

## Success Criteria

A good retrospective should:

1. **Inform**: User learns something new about their workflow
2. **Guide**: Clear next steps for improvement
3. **Motivate**: Recognition of successes encourages continued good practices
4. **Focus**: Prioritization helps user know where to invest effort
5. **Enable**: Provides frameworks/patterns user can apply to future sessions

## Report Storage

**Directory**: `${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/reports/`

**Filename format**: `YYYY-MM-DD-session-description-SESSION_ID.md`

- Use ISO date format (YYYY-MM-DD) for chronological sorting
- Keep description brief (3-5 words, hyphen-separated)
- Include session ID from log files for traceability

**Example path**: `${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/reports/2025-10-23-authentication-refactor-3be2bbaf.md`
