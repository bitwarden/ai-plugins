# Claude Check Your Work Plugin

Evaluation subagents that help agents self-evaluate their work, apply iterative edits, and label emerging concerns.

## Overview

This plugin provides focused evaluation agents designed to be invoked as subagents. Each agent examines a specific dimension of code quality — documentation, structural health, or test design — and produces a structured report with actionable findings.

The primary workflow is described by the `check-your-work` skill: after completing a task, an orchestrating agent launches the appropriate evaluator(s), reviews findings, applies edits, and lists any deferred concerns.

## Agents

### Documentation Evaluator

General-purpose documentation evaluator. Reviews any software documentation for clarity, accuracy, audience fit, and alignment with the code it describes. Operates in-place — it evaluates what exists now, not what changed.

> [!NOTE]
> **Want to help?** The documentation evaluator's criteria currently focus on code-level documentation (JSDoc, inline comments, method contracts). Its coverage of architectural docs, READMEs, and other specialized files could use some TLC. Contributions to its `evaluate-documentation` skill are welcome.

### Health Evaluator

Structural health evaluator. Assesses the environment a change will land in (or has landed in), characterizing tech debt, coupling, and reversibility so that downstream decisions about investment are grounded in observation rather than intuition. Supports both prospective and retrospective review.

### Unit Test Evaluator

Unit test design evaluator. Assesses whether tests verify meaningful behaviors, catches common anti-patterns, and identifies opportunities for consolidation. Runs the tests first to confirm they pass before reviewing.

## Skills

| Skill | Invocation | Description |
|-------|------------|-------------|
| `check-your-work` | user or agent | Workflow guide for launching evaluator subagents after completing a task |
| `evaluate-documentation` | subagent import | Criteria and report template for documentation quality review |
| `evaluate-health` | subagent import | Criteria and report template for structural health review |
| `evaluate-unit-tests` | subagent import | Criteria and report template for unit test design review |
| `guide-on-situational-awareness` | automatic | Guide for understanding your work environment, tracing data flow, and locating specific text or symbols in the codebase |

### `evaluate-*` Skills

These skills form a skill library for subagents. Importing into a subagent is the only supported invocation method — both user invocation and model invocation are disabled. An agent implementing a change must never invoke an `evaluate-*` skill directly, because that agent is prone to rationalize away the skill's advice. The import requirement ensures the subagent has the skill text and provides isolation from the implementing agent's context.

Evaluate skills never reference subagents.

> [!NOTE]
> **Want to help?** Using subagents is expensive, since they need to rediscover context. The `evaluate-*` skills are independent so that you can experiment with them. If you make a subagent with better token efficiency, please submit a PR!

### `guide-*` Skills

Guide skills are excluded from the user-invocable list. They are designed for Claude to read automatically and may be used by subagents or the main agent.

Guide skills never reference subagents.

> [!NOTE]
> **Want to help?** The `guide-on-situational-awareness` skill includes tracing methodologies for localized text and message passing in the Bitwarden `clients` repository. If you develop a new tracing methodology for a different area of the codebase, consider contributing it as a resource under this skill.

## Usage

### Via check-your-work

The `check-your-work` skill orchestrates the evaluators. After completing implementation work, it guides the agent through:

1. Launching the appropriate evaluator subagent(s)
2. Reviewing findings
3. Applying recommended edits
4. Documenting deferred concerns as FIXME comments
5. Listing ignored findings with rationale

### Direct invocation

Evaluators can also be invoked directly:

```
# Review documentation for a specific file
Use the documentation-evaluator agent to review the documentation in src/services/auth.ts

# Assess structural health after a change
Use the health-evaluator agent to perform a retrospective review of the auth module changes

# Review unit test design
Use the unit-test-evaluator agent to review the tests in src/services/auth.spec.ts
```

## Installation

Available through the Bitwarden AI plugins marketplace:

```
/install claude-check-your-work@bitwarden-marketplace
```

Once installed, add the following rule to your user `CLAUDE.md`:

```markdown
**IMPORTANT:** Every time you change code, be sure to use `Skill(claude-check-your-work:check-your-work)` to ensure that your work adheres to the proper standards. Your work is not complete until you have checked your code.
```
