---
argument-hint: [plan-file-path]
allowed-tools: Glob, Grep, Read, Write, Skill, mcp__atlassian__*
description: Review and validate a technical implementation plan to ensure a coding agent can implement it without hallucinated references, missing requirements, or unclear steps.
---

You are executing the `review-plan` command. Your job is to critically review a technical implementation plan and produce actionable findings so a developer can refine it before handing it to a coding agent.

---

## Step 1 — Locate the Plan File

If the user provided a path, read that file. Otherwise scan `~/.claude/plans/` for the most recently modified `.md` file that is not a review file.

Read the entire plan before proceeding.

---

## Step 2 — Fetch Jira Context

Check the top of the plan file for a line matching:
```
**Jira:** [ISSUE-KEY](https://bitwarden.atlassian.net/browse/ISSUE-KEY)
```

If a Jira issue key is present, invoke the `bitwarden-atlassian-tools:researching-jira-issues` skill using the `Skill` tool, passing the issue key as the argument. This will return a synthesized view of the ticket including requirements, acceptance criteria, linked issues, and Confluence documentation.

Store the synthesis output — it will be used in Step 5 to validate the plan against the original requirements.

If no Jira reference is found, skip this step and proceed.

---

## Step 3 — Parse the Plan

Extract and record:
- **Affected repositories and directories** (file paths, mentions of `clients/`, `server/`, `billing-pricing/`, etc.)
- **Specific files** the plan says to create or modify
- **Classes, interfaces, services, methods, and properties** referenced by name
- **Libraries, packages, namespaces, and import paths** mentioned
- **Patterns described** (e.g., "follow the same pattern as X", "inject Y using Z")
- **All acceptance criteria and test cases** per stage
- **Stage sequence and dependencies**

---

## Step 4 — Validate Codebase References

Invoke `Skill(planning-and-writing-code:validating-codebase-references)` and apply its verification methodology to the references extracted in Step 3. This performs systematic anti-hallucination checks against the actual codebase.

---

## Step 5 — Assess Plan Quality

Invoke `Skill(planning-and-writing-code:reviewing-plan-quality)`, passing the Jira synthesis from Step 2 (if available) for requirements alignment checking.

Apply all four assessment sections from that skill:
1. Requirements Completeness (including Jira alignment if synthesis is available)
2. Technical Approach
3. Parallelization Review
4. Clarity and Executability

---

## Step 6 — Write the Review

Determine the directory containing the plan file. Write the review to a new file in that same directory using the `Write` tool. Name the file by taking the plan file's base name (without extension) and appending `-review`, e.g. if the plan file is `PM-12345-my-feature.md`, the review file is `PM-12345-my-feature-review.md`. Do **not** modify the plan file itself.

Use the review output format and verdict rules defined in the `planning-and-writing-code:reviewing-plan-quality` skill.

After writing the review, output a summary in the conversation with this structure:

---
**Review saved:** `<absolute path to review file>`

**Verdict:** [🟢 Ready to Write | 🟡 Needs Revision | 🔴 Major Issues]

**Top issues:**
- [Issue 1]
- [Issue 2]
- ...

**Next:** [If 🟢: "Run `/planning-and-writing-code:implement-plan` to begin implementation." If 🟡 or 🔴: "Address the issues above and re-run `/planning-and-writing-code:review-plan` before implementing."]

---
