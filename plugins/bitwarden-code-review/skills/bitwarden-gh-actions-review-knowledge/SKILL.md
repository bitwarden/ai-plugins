---
name: bitwarden-gh-actions-review-knowledge
description: Institutional knowledge for bitwarden/gh-actions code reviews. Use BEFORE reviewing gh-actions PRs to understand repository-specific patterns, architectural constraints, and avoid false positives.
---

# bitwarden/gh-actions - Code Review Knowledge

## Experiment Overview

| Item | Details |
|------|---------|
| **Repository** | [bitwarden/gh-actions](https://github.com/bitwarden/gh-actions) |
| **Technology Stack** | GitHub Actions, Bash scripting, YAML configuration, Claude Code integration |
| **Primary Languages** | YAML, Bash |
| **Common Issue Categories** | Security patterns (template injection, credential persistence), Bot behavior patterns, Severity calibration, Workflow configuration |

## Verified Detection Strategies

_Copy-paste ready commands for catching common issues._

### Template Injection Detection
```bash
# Find GitHub Actions template expressions directly in shell commands (security risk)
grep -rn '\${{' .github/workflows/ | grep 'run:' | grep -v 'env:'
# Expected: No results (all template expressions should use env vars)

# Verify all template expressions pass through environment variables
awk '/run:/ {in_run=1} in_run && /\${{/ {print FILENAME":"NR":"$0; exit 1}' .github/workflows/*.yml
```

### Checkout Security Validation
```bash
# Find actions/checkout usages missing persist-credentials: false
grep -A5 "uses: actions/checkout" .github/workflows/*.yml | \
  grep -B5 "uses: actions/checkout" | \
  grep -v "persist-credentials: false" | \
  grep "uses: actions/checkout"
```

### Temporary Directory Cleanup Check
```bash
# Find temporary directory creation without cleanup
for file in .github/workflows/*.yml; do
  if grep -q 'mkdir.*temp\|TEMP_DIR=' "$file"; then
    if ! grep -q 'rm -rf.*temp\|rm -rf.*TEMP_DIR' "$file"; then
      echo "Missing cleanup in: $file"
    fi
  fi
done
```

### Documentation-Test Synchronization
```bash
# Verify documented features have corresponding tests
# Extract feature claims from README
grep -i "feature\|support\|handle" */README.md | while read -r claim; do
  feature=$(echo "$claim" | awk '{print tolower($0)}' | sed 's/[^a-z0-9]//g')
  if ! grep -qi "$feature" .github/workflows/test-*.yml; then
    echo "Untested feature: $claim"
  fi
done
```

### Workflow Tool Permission Alignment
```bash
# Compare AGENT.md tool declarations with workflow allowedTools
# Extract tools from AGENT.md
agent_tools=$(grep -A50 "tools:" .claude/agents/*/AGENT.md | grep -E "^\s*-\s" | sed 's/^[^-]*- //' | sort)

# Extract allowedTools from workflow
workflow_tools=$(grep -A20 "allowedTools:" .github/workflows/_review-code.yml | grep -E "^\s+-\s" | sed 's/^[^-]*- //' | sort)

# Show differences
diff <(echo "$agent_tools") <(echo "$workflow_tools")
```

## Failed Attempts (Critical Learnings)

| Issue | Why Missed | Detection Strategy | Review Date | PR Link | Severity |
|-------|------------|-------------------|-------------|---------|----------|
| False positive: Marketplace alias configuration flagged as broken despite correct syntax | Assumed marketplace naming worked like git remotes without consulting Claude Code Action docs | Before flagging config syntax as CRITICAL, verify against official documentation; check merged code for historical usage patterns | 2025-11-14 | [#487](https://github.com/bitwarden/gh-actions/pull/487) | ❌ CRITICAL |
| False positive: Command injection via echo marked CRITICAL when GitHub Actions env vars prevent it | Applied generic shell injection heuristic without understanding GitHub Actions execution model | Distinguish template interpolation ($\{\{ \}\}) from env var expansion; verify attack vector works in execution context before marking CRITICAL | 2025-12-17 | [#525](https://github.com/bitwarden/gh-actions/pull/525) | ❌ CRITICAL |
| False positive: Newline injection defense suggested when sanitization already prevents it | Focused on injection pattern without tracing variable through transformation pipeline | Trace variables through all transformations (tr, sed); verify if flagged character class can survive whitelist patterns | 2025-12-17 | [#525](https://github.com/bitwarden/gh-actions/pull/525) | ⚠️ IMPORTANT |
| Claude duplicated Copilot's grammar findings, violating own Rule 10 about checking existing threads | Did not check for existing review comments before posting | Scan ALL existing review threads before posting; check semantic similarity, not just exact matches | 2025-11-07 | [#473](https://github.com/bitwarden/gh-actions/pull/473) | 🎨 SUGGESTED |
| Unnecessary documentation comment suggested when git history already provided context | Assumed documentation gaps without checking git commit messages and PR descriptions | Check git history/PR description before suggesting inline comments; only suggest for non-obvious logic | 2025-12-12 | [#518](https://github.com/bitwarden/gh-actions/pull/518) | 🎨 SUGGESTED |
| Questioned why workflows differed without understanding their distinct purposes | Assumed consistency requirement across similar-looking files | Read workflow names/descriptions carefully; verify consistency is desirable before flagging differences | 2025-12-12 | [#518](https://github.com/bitwarden/gh-actions/pull/518) | 💭 QUESTION |
| Validation comments posted 3 minutes after PR already merged | No merge status check before posting review | Check PR state before posting comments; suppress or redirect output if already merged | 2025-12-12 | [#518](https://github.com/bitwarden/gh-actions/pull/518) | 🎨 SUGGESTED |
| Redundant validation of author's correct decision already explained with documentation citation | Provided lengthy confirmation when author already demonstrated correct understanding | Distinguish corrections from value-add validation; skip or briefly acknowledge when author cites correct sources | 2025-12-15 | [#520](https://github.com/bitwarden/gh-actions/pull/520) | 🎨 SUGGESTED |

**For detailed error scenarios, root causes, and copy-paste detection commands, see [troubleshooting.md](./references/troubleshooting.md).**

## Repository Gotchas

_Architectural patterns and conventions specific to this repository._

### GitHub Actions Security: Template Expressions Must Use Environment Variables

**Pattern**: ALL GitHub Actions template expressions (`${{ }}`) used in shell commands MUST be passed through environment variables, never directly interpolated in `run:` blocks.

**Common Mistake**: Direct interpolation creates template injection vulnerability
```yaml
# WRONG - Template injection vulnerability
run: echo "User: ${{ github.triggering_actor }}"

# CORRECT - Indirect through environment variable
env:
  ACTOR: ${{ github.triggering_actor }}
run: echo "User: $ACTOR"
```

**Impact**: CRITICAL security vulnerability; CI failures if not followed

_See [troubleshooting.md](./references/troubleshooting.md#false-positive-command-injection-via-echo-with-github-actions-env-vars) for GitHub Actions security model details and detection commands._

**References**: PR [#493](https://github.com/bitwarden/gh-actions/pull/493)

---

### Checkout Security: Always Include persist-credentials: false

**Pattern**: ALL usages of `actions/checkout` MUST include `persist-credentials: false` in the `with:` block to prevent credential leakage.

**Common Mistake**: Omitting persist-credentials parameter
```yaml
# WRONG - Missing credential protection
- uses: actions/checkout@v6.0.0

# CORRECT - Explicit credential protection
- uses: actions/checkout@v6.0.0
  with:
    persist-credentials: false
```

**Impact**: Security vulnerability; required for all checkout actions

**References**: PR [#493](https://github.com/bitwarden/gh-actions/pull/493)

---

### Temporary Directory Cleanup Pattern

**Pattern**: GitHub Actions workflows that create temporary directories MUST explicitly clean them up before job completion to prevent workspace pollution.

**Common Mistake**: Creating temp directories without cleanup handlers

**Impact**: Leftover files accumulate in runner workspaces causing disk issues

**References**: PR [#471](https://github.com/bitwarden/gh-actions/pull/471)

---

### Claude Code SKILL.md Formatting Rules

**Pattern**: Bitwarden enforces specific formatting for Claude Code review skills to prevent GitHub issue link conflicts.

**Required Conventions**:
1. Use "Finding" not "Issue" to avoid GitHub issue link conflicts
2. Never emit bare "#" followed by digits (e.g., "#123")
3. Findings must use single-line format with emoji prefixes
4. Brevity is mandatory - use `<details>` for long explanations
5. Allowed emojis: ❌ ⚠️ ♻️ 🎨 💭

**Impact**: Inconsistent formatting causes false GitHub issue links and parsing difficulty

**References**: PR [#471](https://github.com/bitwarden/gh-actions/pull/471)

---

### Review Timing: Author-Controlled Checkpoint Reviews

**Pattern**: PR authors may dismiss bot review comments mid-stream to get clean, focused reviews at specific checkpoints rather than continuous feedback.

**Guideline**: Don't duplicate previous findings unless explicitly re-requested; when author dismisses comments, assume batch-fix workflow.

**Impact**: Respecting workflow improves author satisfaction and reduces review fatigue

_See [troubleshooting.md](./references/troubleshooting.md#author-controlled-checkpoint-reviews) for detailed workflow patterns._

**References**: PR [#471](https://github.com/bitwarden/gh-actions/pull/471)

---

### Intentional Tool Restrictions Control Agent Behavior

**Pattern**: The repository carefully controls which tools Claude can access, intentionally restricting permissions to prevent hallucinated workarounds when blocked operations are attempted.

**Guideline**: Workflow `allowedTools` must exactly match AGENT.md tool declarations. Don't suggest expanding tool access without understanding rationale.

**Impact**: Tool misalignment causes Claude to generate hallucinated workarounds, degrading review quality

_See [troubleshooting.md](./references/troubleshooting.md#workflow-agent-tool-permission-alignment) for bidirectional verification commands._

**References**: PR [#518](https://github.com/bitwarden/gh-actions/pull/518)

---

### Strategic Removal of Comment Read Access

**Pattern**: The repository intentionally limits Claude's ability to read PR comments via `gh api` commands to keep focus on code analysis rather than prior discussions.

**Rationale**: Prevents distraction by prior suggestions, reduces token consumption, allows dismissal without re-flagging.

**Guideline**: Don't automatically suggest adding `gh api` access for comment reading; strategic information restriction can improve agent behavior.

**Trade-off**: Claude may re-flag issues already discussed and dismissed

**References**: PR [#518](https://github.com/bitwarden/gh-actions/pull/518)

---

### Claude Code Action Marketplace Naming Convention

**Pattern**: Marketplace plugin references use the marketplace name from the repository's manifest file, not from explicit alias assignment in workflow configuration.

**Correct Configuration**:
```yaml
plugin_marketplaces: |
  https://github.com/bitwarden/ai-plugins.git
plugins: |
  claude-config-validator@bitwarden-marketplace
  bitwarden-code-review@bitwarden-marketplace
```

**Guideline**: Check merged code for usage patterns and consult official documentation before flagging configuration as broken.

_See [troubleshooting.md](./references/troubleshooting.md#false-positive-marketplace-alias-configuration-flagged-as-broken) for detailed troubleshooting._

**References**: PR [#487](https://github.com/bitwarden/gh-actions/pull/487)

---

### Consistency Over Latest-Version for New Code

**Pattern**: This repository prefers consistency with existing patterns over using latest versions in isolation. New code should match existing versions even if outdated.

**Guideline**: Check existing workflow versions before recommending updates; suggest repository-wide version updates as separate follow-up work.

**Impact**: Prevents patchwork versioning; maintains consistency across workflows

_See [troubleshooting.md](./references/troubleshooting.md#consistency-over-latest-version-principle) for detailed rationale._

**References**: PR [#493](https://github.com/bitwarden/gh-actions/pull/493)

---

### Validation Scope for Internal Tools

**Pattern**: Internal Bitwarden actions don't need to support every theoretical GitHub edge case; simplified validation is acceptable when it covers actual organizational usage.

**Guideline**: Before flagging validation patterns, consider scope (internal vs public-facing); only flag if evidence suggests real users will be affected.

**Impact**: Overly pedantic validation suggestions waste time on non-issues

_See [troubleshooting.md](./references/troubleshooting.md#validation-scope-for-internal-tools) for examples._

**References**: PR [#493](https://github.com/bitwarden/gh-actions/pull/493)

## Methodology Improvements

_What worked and what didn't in review approaches._

### Bot-to-Bot Review Dynamics

**Lesson**: Always review HEAD commit of PR branch, not historical commits. Before posting findings, scan ALL existing review threads for semantic duplicates. Bot reviewers should acknowledge and reference other bot findings when relevant.

**Applicability**: All PRs with multiple automated reviewers (Copilot + Claude)

_See [troubleshooting.md](./references/troubleshooting.md#claude-duplicated-copilots-findings-in-violation-of-rule-10) for detection commands._

**References**: PR [#471](https://github.com/bitwarden/gh-actions/pull/471), [#473](https://github.com/bitwarden/gh-actions/pull/473)

---

### Iterative Review Rounds at Author's Discretion

**Lesson**: PR authors may want "checkpoint reviews" rather than continuous feedback. Dismissal of bot comments is workflow management, not rejection. Respect author preferences for clean, staged reviews at specific checkpoints.

**Applicability**: All Bitwarden PRs using Claude Code bot reviews

**References**: PR [#471](https://github.com/bitwarden/gh-actions/pull/471)

---

### Inquiry Comments (💭) Have High Value on Architectural Changes

**Lesson**: Inquiry findings (💭) are valuable for behavior-defining files (prompts, configs, rules). Question removals more aggressively than additions. When bot asks "Was this removal intentional?", treat as high-priority.

**Applicability**: PRs modifying behavior-defining files (prompts, configs, documentation)

**References**: PR [#473](https://github.com/bitwarden/gh-actions/pull/473)

---

### Prompt File Review Requires Architectural Focus

**Lesson**: For .claude/prompts/*.md files, prioritize architectural review over grammar. Question removals more aggressively than additions. Consider: "Does this change alter bot behavior in unintended ways?" Meta-rule: When reviewing prompt files, verify your review follows the prompt's rules.

**Applicability**: All repositories using Claude Code with custom prompts

**References**: PR [#473](https://github.com/bitwarden/gh-actions/pull/473)

---

### Multi-Round Review with Persistent False Positive

**Lesson**: When CRITICAL finding persists unaddressed for 2+ weeks, consider false positive. Before repeating finding, check if new evidence should change assessment. When humans challenge with "show documentation," verify seriously. Use 💭 QUESTION for configuration uncertainty rather than ❌ CRITICAL.

**Applicability**: PRs where configuration syntax is flagged as broken

**References**: PR [#487](https://github.com/bitwarden/gh-actions/pull/487)

---

### Security-First Review High Precision on Real Issues

**Lesson**: Security pattern detection should be PRIMARY focus for gh-actions. Validation logic requires more context about internal vs external tooling. Documentation/code consistency needs commit history analysis first. Check commit history before re-flagging resolved issues.

**Statistics**: Valid Issues 4/4 (100%), False Positives 3/3 (100%), Overall Precision 57%, Security Precision 100%

**Applicability**: All bitwarden/gh-actions security reviews

**References**: PR [#493](https://github.com/bitwarden/gh-actions/pull/493)

---

### Context Awareness: Git History Before Documentation Suggestions

**Lesson**: Before suggesting documentation improvements, check git history/PR description. Only suggest inline comments for non-obvious logic or complex algorithms. Configuration values with clear, descriptive names don't require inline explanation.

_See [troubleshooting.md](./references/troubleshooting.md#unnecessary-documentation-comment-suggested-without-checking-git-history) for git history verification commands._

**Applicability**: Documentation review for all repositories

**References**: PR [#518](https://github.com/bitwarden/gh-actions/pull/518)

---

### Bidirectional Configuration Alignment Verification

**Lesson**: When aligning configurations between two sources, verify both directions: (1) Are all workflow tools declared in AGENT.md? (2) Are all AGENT.md tools present in workflow? Discrepancies warrant investigation to determine if intentional or errors. Ask clarifying questions: "Is X missing intentionally?"

**Applicability**: Configuration synchronization, security policy alignment, feature parity checks

**References**: PR [#518](https://github.com/bitwarden/gh-actions/pull/518)

---

### Post-Merge Review Comments Provide No Value

**Lesson**: Automated review systems should check PR merge status before posting. If PR already merged, suppress review output or redirect to logs/metrics.

_See [troubleshooting.md](./references/troubleshooting.md#review-comments-posted-after-pr-already-merged) for implementation example._

**Applicability**: All automated review workflows using AI agents

**References**: PR [#518](https://github.com/bitwarden/gh-actions/pull/518)

---

### Comment Discipline: Distinguish Corrections from Validation

**Lesson**: Distinguish between: (1) **Corrections** (author wrong → must comment), (2) **Value-add validation** (author uncertain → helpful to confirm), (3) **Redundant validation** (author already proved correctness → skip or brief acknowledgment). When author cites correct reasoning with documentation, acknowledge briefly or skip. Reserve detailed comments for corrections, suggestions, or non-obvious insights.

_See [troubleshooting.md](./references/troubleshooting.md#redundant-validation-when-author-already-demonstrated-correct-understanding) for examples._

**Applicability**: All bot review workflows

**References**: PR [#520](https://github.com/bitwarden/gh-actions/pull/520)

---

### Silent Suggestion Adoption Signals Reviewer Uncertainty

**Lesson**: Severity calibration matters - marking false positives as CRITICAL erodes trust. Justify findings: For security issues, explain attack vector and verify it's possible. Distinguish defense-in-depth from required fixes with clear labels. Expect pushback: 100% silent adoption may indicate insufficient challenge; 100% ignored indicates excessive noise.

**Applicability**: All GitHub Actions reviews, especially security-focused

**References**: PR [#525](https://github.com/bitwarden/gh-actions/pull/525)

---

### CRITICAL Severity Requires Confirmed Exploit Path

**Lesson**: Before assigning CRITICAL, verify: (1) Can you construct a working exploit? (2) Does execution environment permit the attack? (3) Are there existing controls that mitigate? If answers are No/No/Yes, downgrade to OPTIONAL with defense-in-depth framing.

**Correct Severity Usage**:
- **❌ CRITICAL**: Active vulnerability with confirmed exploit path
- **⚠️ IMPORTANT**: Significant issue requiring discussion
- **🎨 SUGGESTED**: Improvement opportunity
- **💭 QUESTION**: Seeking clarification
- **(Implied) OPTIONAL**: Defense-in-depth when controls already exist

_See [troubleshooting.md](./references/troubleshooting.md#severity-calibration-guidelines) for detailed calibration guidelines._

**Applicability**: All code reviews, especially security-focused

**References**: PR [#525](https://github.com/bitwarden/gh-actions/pull/525)

---

### Trace Variable Transformations Before Flagging Injection

**Lesson**: Before flagging injection risks, trace variable through ALL transformations. For regex whitelists `[^...]`, verify if flagged character class is excluded. For evidence-based recommendations, acknowledge if existing controls prevent issue. If suggesting defense-in-depth for already-mitigated risk, use OPTIONAL/INFO severity.

_See [troubleshooting.md](./references/troubleshooting.md#false-positive-newline-injection-when-whitelist-sanitization-already-prevents-it) for transformation analysis examples._

**Applicability**: All injection vulnerability analysis

**References**: PR [#525](https://github.com/bitwarden/gh-actions/pull/525)

---

### GitHub Actions Security Model Understanding Required

**Critical Knowledge**: GitHub Actions template expressions (`${{ }}`) are expanded by Actions runtime BEFORE shell sees them. The shell receives literal string values, not templates.

**Correct Assessment**:
- **❌ CRITICAL**: `run: echo ${{ inputs.ref }}` (direct interpolation)
- **✅ SAFE**: `env: REF: ${{ inputs.ref }}` then `run: echo "${REF}"` (env var)
- **OPTIONAL**: Using heredoc for defense-in-depth when env vars already protect

_See [troubleshooting.md](./references/troubleshooting.md#false-positive-command-injection-via-echo-with-github-actions-env-vars) for detailed security model explanation and attack vector analysis._

**References**: PR [#525](https://github.com/bitwarden/gh-actions/pull/525)

---

### Documentation-Test Synchronization Validation

**Lesson**: When reviewing README claims, grep test files for corresponding test case names. For each claimed behavior in documentation, verify at least one test exercises it.

_See [troubleshooting.md](./references/troubleshooting.md#detection-strategy-templates) for documentation-test synchronization commands._

**Applicability**: All repositories with documented features

**References**: PR [#525](https://github.com/bitwarden/gh-actions/pull/525)
