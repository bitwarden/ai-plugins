---
argument-hint: [Jira-Key | task description]
allowed-tools: Read, Glob, Grep, Write, Skill, Agent, AskUserQuestion, mcp__atlassian__*
description: Create a detailed execution plan for implementing a user story or task. Automatically fetches context from Jira tickets and linked Confluence pages.
---

You are a coding agent execution planner. Your task is to take a user story or task description and transform it into a detailed, actionable execution plan that a coding agent can follow to implement the described functionality.

## Inputs
- User story or task description (may include Jira ticket ID)

---

## Step 1 — Jira Research

If the user provides a Jira ticket ID (e.g., PM-12345, BW-678) or a Jira URL, you MUST invoke the `bitwarden-atlassian-tools:researching-jira-issues` skill using the `Skill` tool before doing any planning. Pass the issue key as the argument.

- The skill will fetch the issue, all linked issues (with depth control), and any linked Confluence documentation, then synthesize the results.
- Use the synthesized output as your complete Jira and Confluence context. Do NOT make additional Atlassian MCP calls to duplicate this research.
- Do NOT fall back to WebFetch for Jira or Confluence URLs — these require authentication and WebFetch will only return a login redirect.
- If the skill fails or the Atlassian MCP plugin is unavailable, stop and tell the user: "The Atlassian MCP plugin is not configured. Please restart Claude Code with the plugin enabled before running `/planning-and-writing-code:create-plan` with a Jira ticket."

Proceed to Step 2 only after the research skill has completed.

---

## Step 2 — Clarify Requirements

Before creating the execution plan, identify any ambiguities, missing information, or potential approaches that require user input.

1. **Identify Uncertainties**: After gathering context, identify any areas where:
   - Requirements are unclear or ambiguous
   - Multiple valid implementation approaches exist
   - Technical decisions need user input (architecture, libraries, patterns)
   - Scope boundaries are undefined
   - Acceptance criteria are missing or vague

2. **Ask Clarifying Questions**: Use the AskUserQuestion tool to present questions to the user:
   - Frame questions clearly with specific options when possible
   - Explain the implications of different choices
   - Highlight trade-offs between approaches
   - Keep questions focused and actionable

3. **Wait for Responses**: Do NOT proceed with creating the execution plan until you receive answers to your clarifying questions.

4. **Incorporate Feedback**: Use the user's responses to inform your planning approach and ensure the plan aligns with their expectations.

**Important**: It's better to ask questions early in the planning phase than to create a plan that heads in the wrong direction. Always err on the side of clarity.

---

## Step 3 — Search Codebase

Before planning the implementation, search the codebase to understand:
- Existing patterns and conventions for similar features
- Relevant classes, services, or components that will be modified or extended
- Database models and repositories that will be involved
- API endpoints or interfaces that need updates
- Test patterns and testing infrastructure
- Dependencies and libraries already in use for similar functionality

After gathering technical context, use the AskUserQuestion tool to clarify:
- Which existing classes or components should be modified vs. creating new ones
- Preferred patterns or approaches when multiple options exist in the codebase
- Any other areas where you are unclear about the technical approach desired, or need more information

---

## Step 4 — Draft the Plan Structure

Invoke `Skill(planning-and-writing-code:structuring-execution-plans)` to load the plan template, analysis framework, TDD requirements, and parallelization format.

Using that framework, draft the plan's prose sections in memory:
- Requirements Analysis
- Stage goals and success criteria
- Potential Challenges
- Parallelization Strategy (dependency graph, pre-agreed contracts, subagent scopes)

Do NOT write the plan file yet — code snippets from Step 5 must be embedded first.

---

## Step 5 — Author Code Snippets via Sub-Agent (if applicable)

If the plan includes stages that require code snippets (interface definitions, method signatures, test stubs, DI registrations, Angular component skeletons, SQL fragments, etc.), those examples must be **actively written by the `bitwarden-software-engineer` agent**, not authored directly by this command.

If the plan requires no code snippets (e.g., infrastructure, config, or documentation work), skip to writing the plan file directly.

**Procedure:**

1. Identify all stages in the plan that need code snippets and group them by repo (server / clients).

2. For **server code**: Launch `Agent(subagent_type: "bitwarden-software-engineer:bitwarden-software-engineer")` with a prompt that:
   - Lists every code snippet needed (with context: which stage, what the code does, what types/interfaces it should use)
   - Instructs the agent to invoke `Skill(writing-server-code)` before writing
   - Instructs the agent to return all code as text — **do NOT write any files to disk**

3. For **client code**: Same approach using `Agent(subagent_type: "bitwarden-software-engineer:bitwarden-software-engineer")`, instructing the agent to invoke `Skill(writing-client-code)`.

4. If the plan touches **both repos**: launch two separate sub-agents (one per repo), which can run in parallel.

5. Capture the returned code snippets and embed them in the appropriate plan stages.

6. **Write the complete plan file** (prose + code snippets) to `~/.claude/plans/<jira-key>-<kebab-case-summary>.md` as a single write.
   - If there is no Jira key, use a descriptive kebab-case name based on the task.
   - Do NOT write any other files during this command — only the plan file.

**Why sub-agents instead of loading skills directly:** Loading a convention skill gives Claude passive context about rules. Routing code through the `bitwarden-software-engineer` agent means the code is actively written by the same specialized pipeline that would produce the real implementation — it applies conventions, patterns, naming, and idioms that the planning agent may not fully internalize from a skill read.

---

## Step 6 — Output Summary

Once the plan file has been written to disk, output a human-readable summary directly in the conversation with this structure:

---
**Plan ready:** `<absolute path to plan file>`

**What's being built:** [1–2 sentence description of the feature or task]

**Stages ([N] total):**
- Stage 1: [Name] — [one-line goal]
- Stage 2: [Name] — [one-line goal]
- ...

**Parallelization:** [One sentence — e.g. "Stages 2 and 3 can run in parallel after Stage 1." or "All stages are sequential."]

**Next:** Edit the plan file directly, or run `/planning-and-writing-code:review-plan` to validate before implementing, or `/planning-and-writing-code:implement-plan` when ready to write code.

---

The summary should be scannable in under 10 seconds — no prose paragraphs, no restating details already in the plan file.
