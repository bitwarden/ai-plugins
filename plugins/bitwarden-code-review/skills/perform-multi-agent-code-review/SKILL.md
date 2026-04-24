---
name: perform-multi-agent-code-review
description: Perform a rigorous, multi-agent Bitwarden code review with architecture-compliance, parallel quality/security analysis, finding validation, and severity audit. Use whenever the user asks for a structured, deep, thorough, multi-pass, or multi-agent code review — or a review that includes architecture/pattern compliance, confidence-scored findings, or a severity audit — even if they don't say the exact phrase "multi-agent". Prefer this over a single-agent review when the user wants high-signal findings with validation.
allowed-tools: "Bash(gh pr diff:*), Bash(gh pr view:*), Bash(git diff:*), Bash(git status:*), Bash(git rev-parse:*), Bash(git check-ignore:*), Read, Write, Grep, Glob, Task, Skill"
---

# Overview

The purpose of the skill is to execute a structured, multi-agent code review process on a set of code changes.
The process below **MUST** be followed precisely to ensure consistency and accuracy of code reviews.

## Prerequisites

This skill depends on the following sibling plugins. If any are not installed, **abort the review with a clear error message** identifying the missing plugin — do not attempt to proceed with a degraded pipeline.

- **`bitwarden-architect`** — provides the `bitwarden-architect` subagent type used in Step 2.
- **`bitwarden-security-engineer`** — provides the `bitwarden-security-context` skill (invoked by every Step 2–5 subagent preamble) and the `analyzing-code-security`, `detecting-secrets`, and `reviewing-dependencies` skills referenced by Step 3 security evaluators.
  Before Step 1, verify each prerequisite is resolvable. If a prerequisite is missing, print:

> Prerequisite plugin `<name>` is not installed. Install it and retry. Review aborted.

…and stop.

## Mode

Determine review mode from the invocation:

1. **Argument provided** → **PR mode**. Fetch title/description with `gh pr view`, diff with `gh pr diff`.
2. **No argument** → run `git status --porcelain`.
   - **Non-empty output** → **Local changes mode**. Fetch diff with `git diff`.
   - **Empty output** → **Branch comparison mode**. Capture the current branch with `git rev-parse --abbrev-ref HEAD` (needed for the Step 9 filename), resolve the base with `git rev-parse --abbrev-ref origin/HEAD` (yields e.g. `origin/main`), then diff with `git diff origin/HEAD`.

## Operating Rules

Applies to all agents and subagents.

- Model: Default to the opus model unless `--model` is specified.
- **ALWAYS** tell the user which model is being used before starting the review.
- **NEVER** write to GitHub. All findings go to a local markdown file.
- Tool discipline (see Orchestration → Tool Discipline) applies to the main agent and is propagated verbatim to every subagent. Rationale for the WebFetch/WebSearch ban: bypasses `gh` auth, skips audit trails, can return stale cached pages.

## Orchestration

Applied when launching subagents.

### Project Preamble Propagation

Subagents do not inherit the main agent's CLAUDE.md context. Every subagent prompt in Steps 2–5 MUST open with the two required blocks below, in order, followed by the conditional block if it applies.

**Required — Bitwarden security context.** Include this directive verbatim:

> At the start of your analysis, invoke `Skill(bitwarden-security-engineer:bitwarden-security-context)`. Use its principles, vocabulary, and requirement categories verbatim when classifying findings — do not paraphrase.

**Required — zero-knowledge and threat-model preamble.** Include this block verbatim in the subagent prompt:

> **Zero-knowledge invariant.** Bitwarden servers only store and synchronize encrypted vault data. The server, Bitwarden employees, and third parties must never be able to access unencrypted vault data. Encryption and decryption happen client-side only. The Master Key and Stretched Master Key are never stored on or transmitted to Bitwarden servers.
>
> **Threat-model directive.** Evaluate every change against P01–P06 and the requirements under VD/EK/AT/SC/TC (loaded via the `bitwarden-security-context` skill per the preceding block). For each finding that touches vault data, keys, auth tokens, or user authenticity, name the principle or category it implicates.

**Conditional — repo-specific forwarding.** A repo's checked-in `CLAUDE.md` may contain a section that explicitly instructs you to forward it to subagents (e.g., _"when spawning subagents, include..."_ or _"propagate this to subagents"_). If so, paste that section verbatim. If not, the two required blocks alone suffice.

### Tool Discipline

Include this block verbatim in every Step 2–5 subagent prompt, immediately after the Preamble Propagation blocks:

> **Tool discipline.**
>
> - Use Bash for all `gh`/`git` commands. Never use WebFetch or WebSearch.
> - Assume tools work. Do not probe — no `ls`, `pwd`, `which`, `--version`, `--help`, or pre-read existence checks.
> - The diff, file paths, and PR metadata are in this prompt. Do not re-fetch.
> - On tool failure: note in output and continue. Do not probe to diagnose.

### Context Partitioning

Feature context — issue descriptions, Jira tickets, PR history, removed-predecessor rationale, product framing — sharpens adversarial thinking but biases baseline diff reading. Classify each subagent before launch:

- **Context-allowed** (Step 2 architecture agent; Step 3 Agent 4 security & logic): pass full feature context. These agents think adversarially from intent.
- **Context-forbidden** (Step 3 Agent 1 code quality; Step 3 Agent 2 simplification; Step 3 Agent 3 bug analysis): **ONLY** pass the diff and the Review Rules. **DO NOT** paste issue summaries, Jira tickets, or PR description prose into these prompts.
- **Style-matching requirement.** The main agent's tone and framing across parallel agents leaks — a rich-context prompt for Agent 4 alongside a bare prompt for Agent 3 still implicitly biases Agent 3 through the shared authored reality. When drafting context-forbidden prompts, match the terse style of the diff-only sibling prompts; do not echo the framing of the context-allowed siblings.

## Discovery Standards

### Hygiene Sweep

Agent 1 (code quality) performs a hygiene sweep of the diff before submitting findings; the Step 2 architect performs an analogous doc/code consistency pass per its own directive. When referenced, look specifically for:

- **Dead code added by this PR** — allowlist/registry/lookup-table entries added for features that don't flow through the validated entry point; unused imports; unreachable branches.
- **Stale references** — documentation, comments, error messages, or assertions in this diff that contradict the same diff's implementation.
- **Cross-site inconsistency** — a new call site that differs from established sibling sites in a way not explained by the change (e.g., four platform dialogs where three carry a title and the fourth silently drops it).

This is not an exhaustive checklist — surface anything diff-visible that a senior engineer would flag in a real review.

### Line Number Accuracy

Cite **actual file line numbers**, not positions within the diff. Derive them from the hunk header:

- Parse `@@ -A,B +C,D @@` — `+C` is the starting file line for the hunk. New files use `@@ -0,0 +1,N @@`, so C=1.
- From `+C`, count `+` lines and context lines (no prefix) up to your target. Skip `-` lines, `@@` lines, and `---`/`+++` lines.

**Never guess. Always derive from the hunk header.**

## Evaluation Standards

Applied after a finding exists.

### Severity Levels

Every finding must be assigned one of the following. Do not guess — apply these definitions literally.

- 🛑 **Blocker** — Will cause a production failure, data loss, or security breach.
- ⚠️ **Important** — A real bug or significant risk that is likely to be hit in practice.
- ♻️ **Refactor** — True technical debt being created that will cost more to maintain over time, even if it doesn't cause immediate problems.
- 💡 **Suggestion** — Code structure or quality issue that makes the code harder to maintain or understand than necessary.

### Confidence Scoring

Rate each potential finding on a 0–100 scale:

- **0**: Not confident — false positive or pre-existing issue.
- **25**: Somewhat confident — might be real, might be a false positive. Stylistic issues not called out in project guidelines land here.
- **50**: Moderately confident — real issue, but a nitpick, unlikely to hit in practice, or is a stylistic preference without project-rule backing.
- **80**: Highly confident — verified; very likely to hit in practice. Directly impacts functionality or violates a project guideline.
- **100**: Certain — evidence directly confirms it will happen frequently.

**Only report findings with confidence ≥ 80.** Findings rated 50–79 are dismissed silently; do not re-rate upward to clear the threshold. Every finding must carry both a confidence score and a severity level. Quality over quantity.

### Finding Shape

Every finding and every Step 4/5 return object follows the JSON schema in `references/finding-shape.md`. The main orchestrator loads that file in Step 1 and propagates its contents verbatim to every subagent.

## Code Review Process

Execute these steps in order. Do not skip, reorder, or combine steps.

Every subagent prompt in Steps 2–5 must include the Project Preamble Propagation blocks, the Tool Discipline block, AND the Finding Shape block (from `references/finding-shape.md`) verbatim.

1. Gather context (no subagents):
   - Determine the mode (see the Mode section). Fetch the list of changed files with the mode's command: `gh pr diff {number} --name-only` (PR), `git diff --name-only` (local), or `git diff origin/HEAD --name-only` (branch comparison). In PR mode, also fetch the title and description with `gh pr view`.
   - **READ** the content of CLAUDE.md, README.md, and any other relevant .md files in or near the directories containing modified files.
   - **READ** `references/report-template.md` (path resolved relative to this skill's directory — do NOT search elsewhere) for formatting the final report in Step 7.
   - **READ** `references/finding-shape.md` (path resolved relative to this skill's directory — do NOT search elsewhere). Its contents are pasted verbatim into every Step 2–5 subagent prompt.

2. Launch a single architecture & pattern compliance agent using the `bitwarden-architect` subagent type (from the sibling `bitwarden-architect` plugin — see Prerequisites). Give it the diff fetched with the mode's diff command from Step 1, the list of changed file paths, and — in PR mode only — the PR title and description.

   Unlike the diff agents in Step 3, this agent reads BEYOND the diff to check whether changes fit the codebase.

   Responsibilities:
   - Read the full files being modified (not just diff hunks) to understand surrounding context.
   - Read CLAUDE.md, README.md, and other relevant .md files in or near the modified directories; verify each change complies with explicit project rules.
   - Use Glob and Grep to find how similar code is structured elsewhere in the codebase.
   - **Doc/code consistency pass** — flag contradictions this diff creates between the code and same-repo documentation, configuration, or agent-facing files (e.g., a `CLAUDE.md` entry describing handler behavior the diff now changes; a README example that no longer matches the new signature; `.claude/` agent instructions referencing behavior the PR removes). Only flag divergence this change creates or worsens — do not audit pre-existing drift.

   **Scope.** Raise pattern inconsistencies, architectural boundary violations, duplicated abstractions, and new conventions introduced where an established one applies. Do NOT raise correctness bugs, security issues, code style, or simplification — those belong to Step 3.

   Apply the Severity Levels and Confidence Scoring from Evaluation Standards. Threshold ≥ 80. Emit findings as a JSON array per the Finding Shape schema.

3. Launch 4 agents to independently review the changes. Each agent MUST be given the diff fetched with the mode's diff command from Step 1, and the full review rules included in this prompt — including the Severity Levels, Confidence Scoring, Line Number Accuracy, and Finding Shape sections. Each agent emits findings as a JSON array per the Finding Shape schema. In PR mode, pass the PR title and description **only** to Agent 4, per the Context Partitioning rule; Agents 1, 2, and 3 receive diff + rules only. Send all 4 Agent tool calls in a single message (do NOT use run_in_background).

   **Agent 1: Code quality agent**
   Evaluate the introduced code for significant quality issues: code duplication, missing critical error handling, accessibility problems, and inadequate test coverage. Focus on issues that a senior engineer would flag in a real review.

   Before submitting findings, perform the **Hygiene Sweep** defined in Discovery Standards.

   **Agent 2: Code simplification agent**
   Analyze the introduced code for clarity, consistency, and maintainability. Look for overly complex logic that could be simplified, unclear naming, inconsistent patterns, and opportunities to improve readability — without changing behavior. Prioritize readable, explicit code over compact solutions.

   **Agent 3: Bug analysis agent**
   Scan for obvious bugs. Focus only on the diff itself without reading extra context. Flag only significant bugs; ignore nitpicks and likely false positives. Do not flag issues that you cannot validate without looking at context outside of the git diff.

   **Agent 4: Security & logic agent**
   Look for problems that exist in the introduced code. This could be security findings, incorrect logic, etc. Only look for findings that fall within the changed code.

   Classic application-security items are covered by the `bitwarden-security-engineer` plugin — specifically `analyzing-code-security`, `detecting-secrets`, and `reviewing-dependencies`. **MUST** invoke those skills.

   In addition to attacker-as-LLM and attacker-as-server threat models, evaluate the **user-side threat surface**. Apply the **Trusted Channel** concept from the loaded security context — ask whether the user-facing surface qualifies:
   - **Authenticity of prompts shown to the user** — can the user tell which application is requesting sensitive input? Dialog titles, branding, and prompt strings should allow the user to resist spoofed-dialog phishing.
   - **Consent gates** — is every action requiring user authorization clearly labeled, with sufficient context for the user to make an informed decision?
   - **Output authenticity** — are success/failure messages returned to the user distinguishable from messages an attacker could forge through the same channel?

   This vector is distinct from preventing secrets from reaching the LLM. Both must be evaluated.

   Apply the Severity Levels and Confidence Scoring from Evaluation Standards. Threshold ≥ 80.

4. Launch a validation subagent for each finding from steps 2 and 3. Each subagent receives the diff fetched with the mode's diff command from Step 1, the finding object, the Review Rules, and — in PR mode only — the PR title and description. Send all validation Agent tool calls in a single message (do NOT use run_in_background). Each subagent returns a Step 4 object per the Finding Shape schema.

   A finding is **dismissed** if ANY of the following are true:
   - It is a pre-existing finding, not introduced by this change
   - **Bugs**: The problem does not actually exist in the code (e.g., the variable is not truly undefined, the logic error does not actually produce wrong results)
   - It is a nitpick that a senior engineer would not flag in a real code review
   - It would be caught by a linter (**do not run** the linter to verify)
   - It is a general code quality concern that wouldn't be flagged in a real code review. In other words, do not state generics. All findings **MUST** be specific and actionable.

   **Collateral-change check.** When a finding is about to be dismissed as "deliberate divergence from an established pattern" or "documented exception," before dismissing it check whether supporting code was updated _consistent with_ the divergence. Specifically, scan the diff for:
   - Allowlist, registry, or lookup-table entries that assume the old pattern and are now stale or dead.
   - Schema, type, or interface definitions that still describe the pre-divergence contract.
   - Documentation, comments, or error messages that reference the abandoned path.

   If the divergence is deliberate but its collateral was not updated, the collateral is a new finding (typically ♻️ Refactor or 💡 Suggestion) — do not dismiss the original finding silently; route the collateral problem as its own finding instead.

5. Launch a single severity-audit agent. Give it all validated findings from step 4, the diff, and the full review rules included in this prompt. For each finding, the agent must:
   - Confirm the severity assigned by the review agent, or
   - Downgrade it to a lower severity if the evidence doesn't support the original rating, or
   - Dismiss it entirely if it does not meet the bar for any severity level (even 💡 Suggestion).

   The agent returns a Step 5 object per the Finding Shape schema for each input finding.

6. Merge all Step 4 and Step 5 returns by `id` into the master finding map. Partition by final status: validated (Step 5 `confirmed` or `downgraded`) becomes the main Findings section; dismissed (Step 4 `dismissed` or Step 5 `dismissed`) preserves original severity, original confidence, dismissal stage, and dismissal reason for rendering in the Dismissed block.

7. Format the report using the template in `references/report-template.md` (path resolved relative to this skill's directory — do NOT search elsewhere). Cite every validated AND dismissed finding with full file path and line: `file/path.ext:{line}` (or `:{start}-{end}` for ranges). Omit any severity section with zero findings. If zero findings total, replace the Findings section with: "No findings found."

8. Print the full formatted report to the terminal.

9. Write the formatted report to the repository root in a markdown file with the following naming convention:

- File name: `code-review-PR-{number}.md` (PR mode), `code-review-{YYYY-MM-DD}.md` (local mode), or `code-review-{branch}-{YYYY-MM-DD}.md` (branch comparison mode).
