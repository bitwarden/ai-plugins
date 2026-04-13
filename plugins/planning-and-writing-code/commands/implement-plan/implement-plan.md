---
argument-hint: [plan-file-path]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill
description: Implement code based on a validated execution plan. Loads repo-specific conventions and follows the plan stage by stage.
---

You will be given a detailed markdown plan that describes code you need to write and implement. Your task is to carefully read through this plan and write the actual code that fulfills all the requirements specified.

## Inputs
- Markdown plan detailing the code to be written (path provided by user, or if not provided, scan `~/.claude/plans/` for the most recently modified `.md` file that is not a review file)

---

## Step 1 — Load Repo Conventions

Read the plan to determine which repositories are involved, then load conventions using the **Skill tool**:

- If the plan touches the `server` repo: invoke `bitwarden-software-engineer:writing-server-code` using the **Skill tool**.
- If the plan touches the `clients` repo: invoke `bitwarden-software-engineer:writing-client-code` using the **Skill tool**.
- If the plan touches **both repos**: invoke **both skills sequentially** — `writing-server-code` first, then `writing-client-code` — before writing any code.
- If in neither: proceed with general best practices.

> **Important**: These are **skills**, not agents. Always invoke them with the `Skill` tool — **never** with the `Agent` tool, `Task` tool, or as a `subagent_type`. Do not guess the agent type name; use the Skill tool exclusively.

---

## Step 2 — Implement

Read the plan thoroughly to understand all requirements and specifications.

Follow the structure and guidelines provided in the plan to implement the code:
- Implement all features, functions, and requirements mentioned in the plan
- Use appropriate programming constructs, data types, and patterns as specified
- Include error handling and edge case management unless the plan specifically states otherwise
- Add comments only where the logic isn't self-evident — do NOT add comments that simply explain what the code does
- As each stage is completed, update its `**Status**` field in the plan file from `🔴 Not Started` to `✅ Complete`

If any part of the plan is ambiguous, check in with the user and ask for clarification before proceeding.

---

## Step 3 — Format

After all code is written and tests pass, run formatters for each repo touched by the plan:
- `server` repo: run `dotnet format` from the `server` directory.
- `clients` repo: run `npm run lint` from the `clients` directory.
- If both repos were modified, run both formatters.
