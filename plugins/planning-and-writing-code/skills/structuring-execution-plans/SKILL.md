---
name: structuring-execution-plans
description: Use when creating an implementation or execution plan for a software task. Provides the standard plan template with stage format, TDD ordering, parallelization analysis, and dependency graph notation. Apply when structuring a plan into stages with success criteria, test cases, and parallel workstream definitions.
---

# Structuring Execution Plans

## Analysis Framework

Every plan must address the following before writing stages:

1. **Requirements Analysis**: Identify the core functionality, constraints, and acceptance criteria
2. **Technical Approach**: Determine the appropriate technologies, frameworks, or approaches needed
3. **Implementation Steps**: Break down the work into logical, sequential steps
4. **File Structure**: Specify what files need to be created or modified
5. **Key Functions/Components**: Identify the main functions, classes, or components that need to be built
6. **Testing Considerations**: Outline how the implementation should be tested
7. **Potential Challenges**: Anticipate possible issues and suggest approaches to handle them

<thinking>
Before mapping parallelization opportunities, explicitly reason through the actual data dependencies between every stage pair:
- What does each stage produce (types, files, contracts, registered services)?
- Which subsequent stages consume those outputs?
- Are there stages that share no state and could fan out from a common predecessor?
- What contracts (type names, route prefixes, interface signatures) would parallel workstreams need pre-agreed?
Only after mapping these dependencies should you assess which stages can truly run concurrently.
</thinking>

8. **Parallelization Analysis**: For every stage, map its dependencies and identify opportunities for concurrent subagent execution:
   - Which stages have no blockers and can start immediately
   - Which stages share a common prerequisite and can fan out in parallel once that prerequisite is done
   - What contracts (type names, file paths, route names, interface signatures) must be pre-agreed so parallel workstreams don't need to wait on each other
   - Which stages are truly sequential due to hard data dependencies and cannot be parallelized
   - For each parallel workstream, define the exact scope and entry point a subagent would need to work independently

## Quality Guidance

When creating your execution plan:
- Be specific and actionable — each step should be clear enough for a coding agent to execute
- Consider edge cases and error handling
- Think about code organization and maintainability
- Include relevant technical details like data structures, algorithms, or design patterns
- Specify any external dependencies or libraries that might be needed
- Consider user experience and interface requirements if applicable

<thinking>
Before writing stage content, classify each stage:
- Does this stage produce testable behavior (logic, transformations, service calls, API responses)?
- Or is it pure setup with no testable behavior (adding a constant, registering DI, creating a config entry)?
Then apply the TDD Requirement below accordingly.
</thinking>

## TDD Requirement

Every stage that produces testable code MUST have its tests written BEFORE its implementation. Within each stage, order the work as: (1) write failing tests, (2) implement to make them pass, (3) refactor. The `Tests` field in each stage documents what tests to write first. Stages with no testable behavior (e.g., adding a constant, registering DI) do not require a Tests field.

## Plan Template

Strictly follow this markdown template. Strike a good balance between detail and conciseness to ensure clarity and usability.

```markdown
**Jira:** [ISSUE-KEY](https://bitwarden.atlassian.net/browse/ISSUE-KEY)

## Requirements Analysis
[Detailed breakdown of what needs to be built]

## Stage 1: [Name]
**Goal**: [Specific deliverable]
**Success Criteria**: [Testable outcomes that confirm this stage is complete]
**Tests**: [Specific test cases to write FIRST, before implementing — omit if stage has no testable behavior]
**Status**: 🔴 Not Started

[Repeat for each stage. Stages that produce testable code must have tests listed and must write those tests before the implementation within that stage.]

## Potential Challenges
[Anticipated issues and mitigation strategies]

## Parallelization Strategy
[
  Dependency graph showing which stages are sequential vs. parallel, e.g.:

  Stage N (sequential — all other stages depend on this)
      │
      ├─► [Main thread]  Stage X: ...
      │       │
      │       └─► [Main thread]  Stage X tests
      │
      ├─► [Subagent A]   Stage Y: ...
      │
      └─► [Subagent B]   Stage Z: ...
              (uses pre-agreed contracts below)

      ◄── converge ──►

  Stage M (sequential — needs all prior stages complete)

  If all stages are sequential with no parallelization opportunities, state that explicitly
  rather than forcing a parallel structure where none exists.
]

### Pre-agreed contracts
[
  Table of values locked in so subagents can work without waiting on each other, e.g.:
  | Contract          | Value                          |
  |-------------------|-------------------------------|
  | Model type        | `FooModel` in namespace `...` |
  | Route prefix      | `/foo`                        |
  | POST action route | `[HttpPost("{id}")]`           |

  Omit this section if there are no parallel workstreams.
]

### Subagent scopes
[
  One subsection per parallel subagent describing:
  - The exact file(s) to create or modify
  - What to read first for context
  - Specific tasks to complete
  - Any constraints or gotchas

  Omit this section if there are no parallel workstreams.
]
```

<thinking>
Before deciding whether to author code snippets:
- Does this plan require any code examples (interface definitions, method signatures, test stubs, DI registrations, SQL fragments, Angular component skeletons)?
- If yes, which repos are involved — server, clients, or both?
- This determines whether to launch sub-agents (one per repo) or write the plan file directly without them.
If no code snippets are needed, skip sub-agent launching entirely.
</thinking>

## Code Snippet Authoring Requirement

All code examples embedded in a plan (interface definitions, method signatures, test stubs, DI registrations, SQL fragments, Angular component skeletons) MUST follow Bitwarden conventions as actively validated by the appropriate `bitwarden-software-engineer` writing skills (`writing-server-code`, `writing-client-code`). Code snippets must not be authored directly without these conventions applied.
