# Claude Check Your Work Plugin

Evaluation subagents that help agents self-evaluate their work, apply iterative edits, and label emerging concerns.

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
| `check-your-work` | skill | Workflow guide for launching evaluator subagents after completing a task |
| `documentation-evaluator` | agent | Reviews documentation for clarity, accuracy, and audience fit |
| `health-evaluator` | agent | Assesses structural health, tech debt, coupling, and reversibility |
| `unit-test-evaluator` | agent | Reviews test design for meaningful behavior coverage and anti-patterns |

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
Use the documentation-evaluator agent to review the documentation in src/services/auth.ts
```

> [!NOTE]
> **Want to help?** The documentation evaluator's criteria currently focus on code-level documentation (JSDoc, inline comments, method contracts). Its coverage of architectural docs, READMEs, and other specialized files could use some TLC. Contributions to its `evaluate-documentation` skill are welcome.

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

## Information Architecture

This plugin is written with a strict information architecture to ensure that the system under evaluation is isolated from implementation knowledge. It uses Claude Code's subagent and skill gating features to enforce this.

Subagents are given a specific set of directions through skill injection, which inserts the evaluator's skills directly into its system prompt. Guidance from the main agent is fed in as a user prompt. Since interactivity isn't possible and the main agent cannot read the evaluator skills, the evaluation criteria should reliably override agent input.

The subagent returns its data to the main agent. Feedback directly relevant to the agent task is typically accepted, after which the agent returns control to its operator.

### The FIXME feedback loop

The main agent tends to act on findings that align with its current task and discard the rest. FIXME instructions in the check-your-work skill capture deferred feedback so it isn't lost.

The health-evaluator subagent looks for `FIXME` comments as a strong signal for health hazards. Technical debt in one evaluation can, thus, compound in the next.

> [!NOTE]
> **Want to help?** Skills for followup passes are not yet defined. Try using Claude to identify good candidates for tech debt cleanup using these FIXMEs and contribute a new skill!

### Evaluator subagent design

The subagents are intentionally concise. Each configures a persona and establishes high-level objectives. The bulk of their instructions are in skill definitions. Subagents with skill imports are used to control the criteria and capabilities available to the agent.

Forked skills are avoided in evaluators because guide skills are expected to have general utility spanning evaluator boundaries. Injecting these skills directly into the subagent's system prompt ensures efficacy can be measured reliably.

> [!NOTE]
> **Want to help?** Using subagents is expensive, since they need to rediscover context. If you make a subagent with better token efficiency, please submit a PR!

### Skill design

| Skill | Invocation | Description |
|-------|------------|-------------|
| `evaluate-documentation` | subagent import | Criteria and report template for documentation quality review |
| `evaluate-health` | subagent import | Criteria and report template for structural health review |
| `evaluate-unit-tests` | subagent import | Criteria and report template for unit test design review |
| `guide-on-situational-awareness` | automatic | Guide for tracing data flow, message passing, localized text, and recurring patterns |

> [!NOTE]
> **Want to help?** The `guide-on-situational-awareness` skill includes tracing methodologies for localized text and message passing in the Bitwarden `clients` repository. If you develop a new tracing methodology for a different area of the codebase, consider contributing it as a resource under this skill.

#### `evaluate-*` Skills

These skills form a skill library for subagents. Importing into a subagent is the only supported invocation method — both user invocation and model invocation are disabled. An agent implementing a change must never invoke an `evaluate-*` skill directly, because that agent is prone to rationalize away the skill's advice. The import requirement ensures the subagent has the skill text and provides isolation from the implementing agent's context.

Evaluate skills never reference subagents.

#### `guide-*` Skills

Guide skills are excluded from the user-invocable list. They are designed for Claude to read automatically and may be used by subagents or the main agent.

Guide skills never reference subagents.
