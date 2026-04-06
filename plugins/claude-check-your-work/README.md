# Claude, Check Your Work! Plugin

Subagents that help Claude self-evaluate its work, apply iterative edits, and label emerging concerns.

> [!WARNING]
> **Use of this plugin to check hand-written code is not recommended.**
>
> The subagents are hairsplitting. Claude's ok with that; you might find it excruciating.

## Overview

This plugin provides focused evaluation agents designed to be invoked as subagents. Each agent examines a specific dimension of code quality — documentation, structural health, or test design — and produces a structured report with actionable findings.

The primary workflow is described by the `check-your-work` skill: after completing a task, an orchestrating agent launches the appropriate evaluator(s), reviews findings, applies edits, and lists any deferred concerns.

## Installation

Available through the Bitwarden AI plugins marketplace:

```
/install claude-check-your-work@bitwarden-marketplace
```

## Usage

| Component | Type | Description |
|-----------|------|-------------|
| [`check-your-work`](./skills/check-your-work/SKILL.md) | skill | Workflow guide for launching evaluator subagents after completing a task |
| [`documentation-evaluator`](./agents/documentation-evaluator/AGENT.md) | agent | Reviews documentation for clarity, accuracy, and audience fit |
| [`health-evaluator`](./agents/health-evaluator/AGENT.md) | agent | Assesses structural health, tech debt, coupling, and reversibility |
| [`unit-test-evaluator`](./agents/unit-test-evaluator/AGENT.md) | agent | Reviews test design for meaningful behavior coverage and anti-patterns |
| [`guide-on-situational-awareness`](./skills/guide-on-situational-awareness/SKILL.md) | skill\* | Loaded into context automatically; traces data flow, message passing, localized text, and recurring patterns |

\* Guide skills consume context but are not user-invocable.

### Checking your work

The `check-your-work` skill orchestrates the evaluators. It contains a workflow guide that launches evaluator subagents based on the kind of work Claude performed. Concerns that are not addressed are documented as FIXME comments and surfaced for your review with files and line numbers.

```
# This skill is self-contained; it does not accept input
/check-your-work
```

Add the following rule to your user `CLAUDE.md` if you want Claude to check its work automatically:

```markdown
**IMPORTANT:** Every time you change code, be sure to use `Skill(claude-check-your-work:check-your-work)` to ensure that your work adheres to the proper standards. Your work is not complete until you have checked your code.
```

## Agents

### Documentation Evaluator

General-purpose documentation evaluator. Reviews any software documentation for clarity, accuracy, audience fit, and alignment with the code it describes. Operates in-place — it evaluates what exists now, not what changed.

```
# DO NOT use `@` notation for files
Use the documentation-evaluator agent to review the documentation in src/services/auth.ts
```

> [!NOTE]
> **Want to help?** 🤝
>
> The documentation evaluator's criteria currently focus on code-level documentation (JSDoc, inline comments, method contracts). Its coverage of architectural docs, READMEs, and other specialized files could use some TLC. Contributions to its `evaluate-documentation` skill are welcome.

### Health Evaluator

Structural health evaluator. Assesses the environment a change will land in (or has landed in), characterizing tech debt, coupling, and reversibility so that downstream decisions about investment are grounded in observation rather than intuition. Supports both prospective and retrospective review.

```
Use the health-evaluator agent to perform a retrospective review of the auth module changes
```

### Unit Test Evaluator

Unit test design evaluator. Assesses whether tests verify meaningful behaviors, catches common anti-patterns, and identifies opportunities for consolidation. Runs the tests first to confirm they pass before reviewing.

```
# DO NOT use `@` notation for files
Use the unit-test-evaluator agent to review the tests in src/services/auth.spec.ts
```

## See Also

* [Changelog](./CHANGELOG.md)
* [Deep dive](./DEEP_DIVE.md) - explains the structure of the plugin and the "why" of its design
