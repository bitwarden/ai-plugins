---
name: Sprint Workability Analysis
description: |
  This skill should be used when the user asks to "analyze sprint workability",
  "review sprint tickets", "check sprint blockers", "evaluate ticket readiness",
  "what's blocking the sprint", or requests a sprint health assessment.
  Orchestrates the full workflow from data retrieval through categorized reporting.
version: 1.0.0
---

# Sprint Workability Analysis

## Purpose

Analyze sprint tickets to determine their workability status, identifying blockers,
stalled work, and items needing clarification.

## Required Information

To perform analysis, gather:
1. **Data Source**: Confluence page ID, JIRA sprint name, or ticket list
2. **Sprint Identifier**: Date range or sprint name (if using Confluence)
3. **Platform Filter**: Which platform(s) to analyze (optional)
4. **Output Preference**: How results should be formatted (optional)

## Workflow

### Step 1: Data Source Resolution
Determine how to retrieve ticket data:
- If Confluence page ID provided: Use `parsing-sprint-data` skill
- If JIRA sprint name provided: Use JQL search
- If ticket list provided: Retrieve directly

### Step 2: Ticket Filtering
Apply filters to narrow ticket set:
- Platform/Component (Android, iOS, Server, etc.)
- Status (exclude Done by default)
- Sprint date range matching

### Step 3: Parallel Investigation
Deploy a team of `ticket-investigator` agents to investigate each ticket:
- Use Task tool with run_in_background: true
- Launch all agents in parallel
- Collect results with TaskOutput

### Step 4: Categorization
Apply `categorizing-workability` skill:
- Group tickets by workability category
- Calculate metrics per category
- Prioritize within categories

### Step 5: Report Generation
Use `generating-report` skill:
- Format output per user preference
- Include executive summary
- Provide actionable recommendations

## Invocation of Sub-Skills
1. Invoke: parsing-sprint-data
   - Input: source, sprint identifier
   - Output: List of ticket keys

2. For each ticket, deploy: ticket-investigator (parallel)
   - Input: ticket key
   - Output: Investigation result with workability assessment

3. Invoke: categorizing-workability
   - Input: All investigation results
   - Output: Categorized and prioritized results

4. Invoke: generating-report
   - Input: Categorized results, output format preference
   - Output: Final report

## Example Interaction

User: "Can you analyze the Android tickets from our Dec 15-26 sprint?
       The sprint data is on Confluence page 2270330935"

Response:
1. Parse Confluence page to extract Dec 15-26 section tickets
2. Filter for Android component
3. Deploy parallel investigators for each ticket
4. Categorize results
5. Generate markdown report with findings
