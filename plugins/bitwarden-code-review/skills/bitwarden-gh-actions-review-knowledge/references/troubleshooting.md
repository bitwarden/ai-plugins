# Review Troubleshooting: bitwarden/gh-actions

## Error → Solution Mappings

### False Positive: Marketplace Alias Configuration Flagged as Broken

**Symptom**: Reviewer flags marketplace plugin reference syntax as CRITICAL error despite correct configuration

**Cause**: Assumed marketplace aliases work like git remotes requiring explicit `name=url` definition without consulting Claude Code Action documentation

**Solution**: Before flagging configuration syntax as broken:
1. Verify against official documentation (Claude Code Action docs)
2. Check merged code for historical usage patterns
3. Understand marketplace names come from manifest files, not workflow alias assignment
4. Use 💭 QUESTION for configuration uncertainty rather than ❌ CRITICAL

**Correct Configuration**:
```yaml
plugin_marketplaces: |
  https://github.com/bitwarden/ai-plugins.git
plugins: |
  claude-config-validator@bitwarden-marketplace
  bitwarden-code-review@bitwarden-marketplace
```

**Detection Command**:
```bash
# Verify marketplace references match manifest naming
grep -A10 "plugin_marketplaces:" .github/workflows/*.yml
grep -A10 "plugins:" .github/workflows/*.yml
```

**References**: PR [#487](https://github.com/bitwarden/gh-actions/pull/487)

---

### False Positive: Command Injection via Echo with GitHub Actions Env Vars

**Symptom**: Reviewer marks CRITICAL command injection vulnerability in `echo "${VAR}"` when variable comes from GitHub Actions environment variables

**Cause**: Applied generic shell injection heuristic without understanding GitHub Actions template expansion execution model

**Solution**: Understand GitHub Actions security model:
- GitHub Actions expands `${{ }}` to literal strings BEFORE shell execution
- Template → env var → shell usage is SAFE
- Direct template in run block (`run: echo ${{ inputs.ref }}`) is DANGEROUS
- Shell receives already-expanded values; command substitution like `$(evil)` becomes literal characters
- Before flagging CRITICAL, verify execution model permits the attack

**Correct Assessment**:
```yaml
# CRITICAL - Direct template interpolation in shell
run: echo "Ref: ${{ inputs.ref }}"

# SAFE - Template expanded to env var, then used in shell
env:
  REF: ${{ inputs.ref }}
run: echo "Ref: ${REF}"

# OPTIONAL - Heredoc for defense-in-depth when env vars already protect
env:
  REF: ${{ inputs.ref }}
run: |
  cat <<EOF
  Ref: ${REF}
  EOF
```

**Detection Command**:
```bash
# Find DANGEROUS direct template interpolation in run blocks
grep -rn '\${{' .github/workflows/ | grep 'run:' | grep -v 'env:'

# Find SAFE env var pattern
awk '/env:/ {in_env=1} /run:/ {in_env=0} in_env && /\${{/ {print FILENAME":"NR":"$0}' .github/workflows/*.yml
```

**References**: PR [#525](https://github.com/bitwarden/gh-actions/pull/525)

---

### False Positive: Newline Injection When Whitelist Sanitization Already Prevents It

**Symptom**: Reviewer flags newline injection risk as IMPORTANT when existing regex whitelist already prevents the attack

**Cause**: Focused on GITHUB_OUTPUT injection pattern without tracing variable through complete transformation pipeline

**Solution**: Before flagging injection vulnerabilities:
1. Trace variable through ALL transformations (tr, sed, awk)
2. For regex whitelists `[^...]`, verify if flagged character class is excluded
3. Mathematically verify if attack characters can survive transformation
4. If existing controls prevent issue, use OPTIONAL severity with "defense-in-depth" framing

**Example Analysis**:
```bash
# Existing code
IMAGE_TAG=$(tr '[:upper:]' '[:lower:]' <<< "$INPUT" | sed -E 's/[^a-z0-9._-]+/-/g')

# Analysis steps:
# 1. tr lowercases all characters
# 2. sed whitelists ONLY [a-z0-9._-]
# 3. Newlines are NOT in whitelist → converted to hyphens
# 4. Conclusion: Newline injection mathematically impossible
```

**Detection Command**:
```bash
# Find whitelist patterns that may already prevent injection
grep -rn "sed -E 's/\[.*\]+/-/g'" .github/workflows/
grep -rn "tr.*<<< \"\$" .github/workflows/
```

**References**: PR [#525](https://github.com/bitwarden/gh-actions/pull/525)

---

### Claude Duplicated Copilot's Findings in Violation of Rule 10

**Symptom**: Bot posts finding semantically identical to another bot's comment from the same PR

**Cause**: Did not check for existing review comments before posting; only checked exact text matches, not semantic similarity

**Solution**: Before posting findings:
1. Scan ALL existing review threads (both bot and human comments)
2. Check for semantic similarity, not just exact text matches
3. If another reviewer already raised the issue, reference their comment instead of duplicating
4. Bot reviewers should acknowledge and cite other bot findings when relevant

**Detection Command**:
```bash
# Review existing PR comments before posting
gh pr view <PR_NUMBER> --json comments --jq '.comments[].body'

# Check for similar topics in comment threads
gh api repos/OWNER/REPO/pulls/<PR_NUMBER>/comments | jq -r '.[].body' | grep -i "keyword"
```

**References**: PR [#473](https://github.com/bitwarden/gh-actions/pull/473)

---

### Unnecessary Documentation Comment Suggested Without Checking Git History

**Symptom**: Reviewer suggests inline documentation comments when git commit messages and PR descriptions already provide adequate context

**Cause**: Assumed documentation gaps without checking git history, commit messages, and PR descriptions for explanatory context

**Solution**: Before suggesting inline documentation:
1. Check `git log -p <file>` for commit messages explaining the logic
2. Review PR description for design rationale
3. Only suggest comments for non-obvious logic or complex algorithms
4. Configuration values with clear, descriptive names don't require inline explanation
5. Consider maintenance overhead of keeping inline comments synchronized

**Detection Command**:
```bash
# Check git history for explanatory context
git log -p --follow <file_path> | grep -A10 -B10 "feature_name"

# Check PR description
gh pr view <PR_NUMBER> --json body --jq '.body'
```

**References**: PR [#518](https://github.com/bitwarden/gh-actions/pull/518)

---

### Questioned Workflow Differences Without Understanding Distinct Purposes

**Symptom**: Reviewer flags inconsistencies between similar-looking workflows without understanding their distinct purposes

**Cause**: Assumed consistency requirement across files with similar naming patterns without reading workflow descriptions

**Solution**: Before flagging differences as inconsistencies:
1. Read workflow names and descriptions carefully
2. Understand if workflows serve different purposes
3. Verify consistency is desirable before flagging
4. Ask clarifying questions: "Are these workflows intended to differ?"

**Detection Command**:
```bash
# Compare workflow purposes
grep -h "^name:" .github/workflows/*.yml
grep -h "^# " .github/workflows/*.yml | head -20
```

**References**: PR [#518](https://github.com/bitwarden/gh-actions/pull/518)

---

### Review Comments Posted After PR Already Merged

**Symptom**: Automated review system posts comments 3+ minutes after PR was already merged

**Cause**: No merge status check before posting review; wasted API tokens and created noise in PR thread

**Solution**: Implement merge status check before posting:
```yaml
- name: Check if PR is still open
  id: pr-status
  run: |
    STATE=$(gh pr view ${{ github.event.pull_request.number }} --json state --jq '.state')
    echo "state=$STATE" >> $GITHUB_OUTPUT

- name: Review with Claude Code
  if: steps.pr-status.outputs.state == 'OPEN'
  # ... rest of review job
```

**Detection Command**:
```bash
# Check PR state before running review logic
gh pr view <PR_NUMBER> --json state --jq '.state'
# Expected: "OPEN" to proceed, "MERGED" or "CLOSED" to skip
```

**References**: PR [#518](https://github.com/bitwarden/gh-actions/pull/518)

---

### Redundant Validation When Author Already Demonstrated Correct Understanding

**Symptom**: Bot posts lengthy validation confirming author's correct decision when author already cited documentation proving correctness

**Cause**: Provided confirmation without distinguishing between corrections (author wrong) vs redundant validation (author already correct with proof)

**Solution**: Distinguish comment types:
- **Corrections**: Author is wrong → must comment
- **Value-add validation**: Author might be uncertain → helpful to confirm
- **Redundant validation**: Author already proved correctness with citations → skip or brief acknowledgment

When author cites correct reasoning with documentation, acknowledge briefly or skip entirely.

**Detection Command**:
```bash
# Check if author provided documentation citations in PR description or comments
gh pr view <PR_NUMBER> --json body,comments --jq '.body, .comments[].body' | grep -i "documentation\|docs\|reference"
```

**References**: PR [#520](https://github.com/bitwarden/gh-actions/pull/520)

---

## Detection Strategy Templates

### Template Injection Security Audit

```bash
# Comprehensive template injection detection
echo "=== Checking for direct template interpolation in run blocks ==="
grep -rn '\${{' .github/workflows/ | grep 'run:' | grep -v 'env:'

echo "=== Verifying all template expressions use env vars ==="
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

### Documentation-Test Synchronization Check

```bash
# Verify documented features have corresponding tests
grep -i "feature\|support\|handle" */README.md | while read -r claim; do
  feature=$(echo "$claim" | awk '{print tolower($0)}' | sed 's/[^a-z0-9]//g')
  if ! grep -qi "$feature" .github/workflows/test-*.yml; then
    echo "Untested feature: $claim"
  fi
done
```

### Workflow-Agent Tool Permission Alignment

```bash
# Compare AGENT.md tool declarations with workflow allowedTools
agent_tools=$(grep -A50 "tools:" .claude/agents/*/AGENT.md | grep -E "^\s*-\s" | sed 's/^[^-]*- //' | sort)
workflow_tools=$(grep -A20 "allowedTools:" .github/workflows/_review-code.yml | grep -E "^\s+-\s" | sed 's/^[^-]*- //' | sort)

# Show differences (both directions)
echo "=== Tools in AGENT.md but not in workflow ==="
comm -23 <(echo "$agent_tools") <(echo "$workflow_tools")

echo "=== Tools in workflow but not in AGENT.md ==="
comm -13 <(echo "$agent_tools") <(echo "$workflow_tools")
```

---

## Severity Calibration Guidelines

### CRITICAL Severity Requirements

Before assigning ❌ CRITICAL severity, verify ALL conditions:

1. **Can you construct a working exploit?** (Yes required)
2. **Does execution environment permit the attack?** (Yes required)
3. **Are there existing controls that mitigate?** (No required)

If answers are No/No/Yes, downgrade to OPTIONAL with defense-in-depth framing.

**Correct Severity Usage**:
- **❌ CRITICAL**: Active vulnerability with confirmed exploit path
- **⚠️ IMPORTANT**: Significant issue requiring discussion, unresolved questions
- **🎨 SUGGESTED**: Improvement opportunity, best practice recommendation
- **💭 QUESTION**: Seeking clarification, configuration uncertainty
- **(Implied) OPTIONAL**: Defense-in-depth when controls already exist

**Reference**: PR [#525](https://github.com/bitwarden/gh-actions/pull/525) - Two CRITICAL false positives on command injection

---

## Context Awareness Patterns

### Check Git History Before Suggesting Documentation

```bash
# Review commit history for explanatory context
git log --oneline --all --decorate -- <file_path>
git log -p --follow <file_path> | grep -C5 "keyword"

# Check PR that introduced the change
gh pr list --search "path:<file_path>" --state merged --json number,title,body
```

### Verify Configuration Against Official Documentation

Before flagging configuration as broken:

1. Search official documentation for syntax examples
2. Check repository's merged code for historical usage patterns
3. Look for tests that validate the configuration
4. Consult maintainers if documentation is ambiguous

**Never assign CRITICAL severity to configuration questions without verified sources.**

### Review HEAD Commit, Not Intermediate History

Bot reviewers should:
- Review the final state of the PR branch (HEAD commit)
- Avoid flagging issues already fixed in later commits
- Check if cleanup/fixes were added after initial implementation

```bash
# Get PR HEAD commit
gh pr view <PR_NUMBER> --json headRefOid --jq '.headRefOid'

# Review only HEAD changes vs base
git diff <base_branch>...<pr_head_commit>
```

---

## Repository-Specific Conventions

### Internal Tool Validation Scope

**Pattern**: Bitwarden's internal GitHub Actions don't need to support every theoretical GitHub edge case.

**Guideline**: Before flagging validation as too strict/loose:
1. Consider scope: internal vs public-facing tool
2. Check if organization actually has edge cases that would fail validation
3. Only flag if evidence suggests real users will be affected
4. Simplified patterns are acceptable for internal tools

**Example**: Single-character username regex flagged as too strict → correctly rejected as unnecessary for internal Bitwarden use.

**Reference**: PR [#493](https://github.com/bitwarden/gh-actions/pull/493)

---

### Consistency Over Latest-Version Principle

**Pattern**: New code should match existing versions even if outdated; version updates happen repository-wide in dedicated PRs.

**Guideline**: Before recommending version updates:
1. Check what versions existing workflows use
2. If new code uses newer version than existing, recommend matching existing pattern
3. Suggest repository-wide version update as separate follow-up work
4. Apply same principle to formatting, naming conventions, and style choices

**Reference**: PR [#493](https://github.com/bitwarden/gh-actions/pull/493)

---

### Author-Controlled Checkpoint Reviews

**Pattern**: PR authors may dismiss bot review comments mid-stream to get clean, focused reviews at specific checkpoints.

**Guideline**:
- Dismissal of bot comments is workflow management, not rejection
- When author requests "fresh review," don't duplicate previous findings unless explicitly re-requested
- Respect batch-fix workflow preferences
- Check for human comments mentioning "removed comments" or "checkpoint review"

**Reference**: PR [#471](https://github.com/bitwarden/gh-actions/pull/471)
