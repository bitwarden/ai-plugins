---
name: performing-multi-agent-code-review
description: Perform a rigorous, multi-agent code review with architecture-compliance, parallel quality/security analysis, finding validation, and severity audit. Use whenever the user asks for a structured, deep, thorough, multi-pass, or multi-agent code review — or a review that includes architecture/pattern compliance, confidence-scored findings, or a severity audit — even if they don't say the exact phrase "multi-agent". Prefer this over a single-agent review when the user wants high-signal findings with validation. Also use whenever the user asks for a code review across a commit range, time window, or N most recent commits in a locally checked-out repo (e.g. "review the last week of commits in bitwarden/server", "review the last 20 commits", "review changes since 2026-04-23") — these route to the commit-range mode below.
allowed-tools: "Bash(gh pr diff:*), Bash(gh pr view:*), Bash(git diff:*), Bash(git status:*), Bash(git rev-parse:*), Bash(git check-ignore:*), Bash(git log:*), Bash(git rev-list:*), Read, Write, Grep, Glob, Task, Skill"
---

# Overview

Execute a structured, multi-agent code review on a set of code changes. Follow the process below precisely — skipping steps degrades consistency and accuracy.

## Prerequisites

This skill depends on the following sibling plugins. If any are not installed, **abort the review with a clear error message** identifying the missing plugin — do not attempt to proceed with a degraded pipeline.

- **`bitwarden-tech-lead`** — provides the architecture review subagent.
- **`bitwarden-security-engineer`** — provides security context and analysis skills.
  Before Step 1, verify each prerequisite is resolvable. If a prerequisite is missing, print:

> Prerequisite plugin `<name>` is not installed. Install it and retry. Review aborted.

…and stop.

## Mode

Read `references/modes.md`. Loaded in Step 1; the orchestrator determines the mode from the invocation, runs the resolution sequence (commit-range mode only), and uses the matching diff-source commands to populate Step 1's gathered context. Modes are orchestrator-only and not propagated to subagents.

## Operating Rules

Applies to all agents and subagents.

- Model: Default to the opus model unless `--model` is specified.
- Announce which model is being used before starting the review.
- Don't write to GitHub. All findings go to a local markdown file.
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

- **Context-allowed** (Step 2 architecture agent; Step 3 Agent 3 security & logic): pass full feature context. These agents think adversarially from intent.
- **Context-forbidden** (Step 3 Agent 1 code quality; Step 3 Agent 2 bug analysis): **ONLY** pass the diff and the Review Rules. **DO NOT** paste issue summaries, Jira tickets, or PR description prose into these prompts.
- **Style-matching requirement.** The main agent's tone and framing across parallel agents leaks — a rich-context prompt for the security agent alongside a bare prompt for the bug agent still implicitly biases the bug agent through the shared authored reality. When drafting context-forbidden prompts, match the terse style of the diff-only sibling prompts; do not echo the framing of the context-allowed siblings.

## Discovery Standards

Read `references/discovery-standards.md`. Referenced by Step 2 (architect doc/code consistency pass) and Step 3 Agent 1 (Hygiene Sweep). The Line Number Accuracy rule is propagated verbatim into every Step 2–5 subagent prompt.

## Evaluation Standards

Read `references/evaluation-standards.md`. Severity Levels, Do Not Flag, and Confidence Scoring are propagated verbatim into every Step 2–5 subagent prompt; the Finding Shape schema lives in `references/finding-shape.md` and is also propagated verbatim.

## Code Review Process

Execute these steps in order. Do not skip, reorder, or combine steps.

Every subagent prompt in Steps 2–5 must include the Project Preamble Propagation blocks, the Tool Discipline block, AND the Finding Shape block (from `references/finding-shape.md`) verbatim.

1. Gather context (no subagents). All `references/...` paths below resolve relative to this skill's directory — do not search elsewhere.
   - **READ** `references/modes.md`. The orchestrator follows it to determine the review mode and the matching diff-source commands.
   - Determine the mode per `references/modes.md`. Fetch the list of changed files with the mode's command: `gh pr diff {number} --name-only` (PR), `git diff --name-only` (local), `git diff origin/HEAD --name-only` (branch comparison), or `git diff <from>..<to> --name-only` (commit range). In PR mode, also fetch the title and description with `gh pr view`.
   - **READ** CLAUDE.md, README.md, and any other relevant .md files in or near the directories containing modified files.
   - **READ** `references/report-template.md` for formatting the final report in Step 7.
   - **READ** `references/finding-shape.md`. Its contents are pasted verbatim into every Step 2–5 subagent prompt.
   - **READ** `references/discovery-standards.md`. The Hygiene Sweep is referenced by name in the Step 3 Agent 1 prompt; Line Number Accuracy is propagated verbatim into every Step 2–5 subagent prompt.
   - **READ** `references/evaluation-standards.md`. Severity Levels, Do Not Flag, and Confidence Scoring are propagated verbatim into every Step 2–5 subagent prompt.

2. Launch a single architecture & pattern compliance agent using the `bitwarden-tech-lead` subagent type. Give it the diff, the list of changed file paths, and — in PR mode only — the PR title and description.

   Unlike the diff agents in Step 3, this agent reads BEYOND the diff to check whether changes fit the codebase.

   Responsibilities:
   - Read the full files being modified (not just diff hunks) to understand surrounding context.
   - Read CLAUDE.md, README.md, and other relevant .md files in or near the modified directories; verify each change complies with explicit project rules.
   - Use Glob and Grep to find how similar code is structured elsewhere in the codebase.
   - **Doc/code consistency pass** — flag contradictions this diff creates between the code and same-repo documentation, configuration, or agent-facing files (e.g., a `CLAUDE.md` entry describing handler behavior the diff now changes; a README example that no longer matches the new signature; `.claude/` agent instructions referencing behavior the PR removes). Only flag divergence this change creates or worsens — do not audit pre-existing drift.

   **Scope.** Raise pattern inconsistencies, architectural boundary violations, duplicated abstractions, and new conventions introduced where an established one applies. Do NOT raise correctness bugs, security issues, or code-quality concerns — those belong to Step 3.

   Apply the Severity Levels and Confidence Scoring from Evaluation Standards. Threshold ≥ 80. Emit findings as a JSON array per the Finding Shape schema.

3. Launch 3 agents to independently review the changes. Each receives the diff and the review rules; each emits findings as a JSON array per the Finding Shape schema. In PR mode, pass the PR title and description only to Agent 3 per Context Partitioning — Agents 1 and 2 receive diff + rules only. Send all 3 Agent tool calls in a single message (do NOT use run_in_background).

   **Agent 1: Code quality agent**
   Read the introduced code as a senior engineer reviewing it for the first time. Surface anything that hurts correctness, clarity, or long-term maintainability — code duplication, missing critical error handling, accessibility gaps, inadequate test coverage, overly complex logic, unclear naming, inconsistent patterns. Prefer readable, explicit code over compact solutions; flag readability problems alongside correctness ones rather than treating them as separate categories.

   Before submitting findings, perform the **Hygiene Sweep** defined in `references/discovery-standards.md`.

   **Agent 2: Bug analysis agent**
   Scan the diff for significant bugs visible without outside context. Skip nitpicks, likely false positives, and anything you'd need to read other files to confirm.

   **Agent 3: Security & logic agent**
   Find security flaws and logic errors in the introduced code. Stay scoped to changed lines.

   Invoke `analyzing-code-security`, `detecting-secrets`, and `reviewing-dependencies` from the `bitwarden-security-engineer` plugin to cover classic application-security items.

   In addition to attacker-as-LLM and attacker-as-server threat models, evaluate the **user-side threat surface**. Apply the **Trusted Channel** concept from the loaded security context — ask whether the user-facing surface qualifies:
   - **Authenticity of prompts shown to the user** — can the user tell which application is requesting sensitive input? Dialog titles, branding, and prompt strings should allow the user to resist spoofed-dialog phishing.
   - **Consent gates** — is every action requiring user authorization clearly labeled, with sufficient context for the user to make an informed decision?
   - **Output authenticity** — are success/failure messages returned to the user distinguishable from messages an attacker could forge through the same channel?

   This vector is distinct from preventing secrets from reaching the LLM. Both must be evaluated.

   Apply the Severity Levels and Confidence Scoring from Evaluation Standards. Threshold ≥ 80.

4. Launch a single validation subagent for all findings from Steps 2 and 3. The subagent receives the diff fetched with the mode's diff command from Step 1, the full array of finding objects, the Review Rules, and — in PR mode only — the PR title and description. The subagent returns an array of Step 4 objects (one per input finding) per the Finding Shape schema.

   **Chunking escape hatch.** If raw findings from Steps 2 and 3 number more than 25, partition them into chunks of ≤ 15 (preserving collateral context within each chunk; do not split a `source_agent` group across chunks if it would put related findings on opposite sides) and launch one validation subagent per chunk in a single message (do NOT use run_in_background).

   A finding is **dismissed** if ANY of the following are true:
   - It is a pre-existing finding, not introduced by this change. In commit-range mode, treat the cumulative diff of `<from>..<to>` as "this change" and the parent of `<from>` as the pre-existing baseline.
   - **Bugs**: The problem does not actually exist in the code (e.g., the variable is not truly undefined, the logic error does not actually produce wrong results)
   - It is a nitpick that a senior engineer would not flag in a real code review
   - It would be caught by a linter (**do not run** the linter to verify)
   - It is a general code quality concern that wouldn't be flagged in a real code review. In other words, do not state generics. All findings **MUST** be specific and actionable.

   **Collateral-change check.** When a finding is about to be dismissed as "deliberate divergence from an established pattern" or "documented exception," before dismissing it check whether supporting code was updated _consistent with_ the divergence. Specifically, scan the diff for:
   - Allowlist, registry, or lookup-table entries that assume the old pattern and are now stale or dead.
   - Schema, type, or interface definitions that still describe the pre-divergence contract.
   - Documentation, comments, or error messages that reference the abandoned path.

   If the divergence is deliberate but its collateral was not updated, the collateral is a new finding (typically ♻️ Refactor) — do not dismiss the original finding silently; route the collateral problem as its own finding instead.

5. Launch a single severity-audit agent. Give it all validated findings from step 4, the diff, and the full review rules included in this prompt. For each finding, the agent must:
   - Confirm the severity assigned by the review agent, or
   - Downgrade it to a lower severity if the evidence doesn't support the original rating, or
   - Dismiss it entirely if it does not meet the bar for any severity level.

   The agent returns a Step 5 object per the Finding Shape schema for each input finding.

6. Merge all Step 4 and Step 5 returns by `id` into the master finding map. Creation-time fields are immutable (see `references/finding-shape.md`). For dismissed findings, set `dismissal_stage` to `"Step 4 validation"` or `"Step 5 severity audit"` based on which step set the dismissal status — it renders as `**Dismissed at:**`. Partition by final status: validated (Step 5 `confirmed` or `downgraded`) becomes the main Findings section; dismissed (Step 4 `dismissed` or Step 5 `dismissed`) preserves original severity, original confidence, dismissal stage, and dismissal reason for rendering in the Dismissed block.

7. Format the report using the template in `references/report-template.md`. Cite every validated AND dismissed finding with full file path and line: `file/path.ext:{line}` (or `:{start}-{end}` for ranges). Omit any severity section with zero findings. If zero findings total, replace the Findings section with: "No findings found." For every rendered finding (validated and dismissed), populate the `**Caught by:**` line from the finding's `source_agent` field, translated to the friendly label per the table in `references/report-template.md`. Dismissed findings additionally render `**Original severity:**`, `**Original confidence:**`, `**Dismissed at:**`, and `**Dismissed because:**` per the template — past runs have silently dropped these, so do not omit any of them; per-finding traceability requires the full set.

8. Print the full formatted report to the terminal.

9. Write the formatted report to the repository root in a markdown file with the following naming convention:

- File name: `code-review-PR-{number}.md` (PR mode), `code-review-{YYYY-MM-DD}.md` (local mode), `code-review-{branch}-{YYYY-MM-DD}.md` (branch comparison mode), or `code-review-{from-short}..{to-short}.md` (commit-range mode, where `{from-short}`/`{to-short}` are 7-char SHAs or shorter ref names).
