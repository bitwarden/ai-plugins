# capturing-review-knowledge

Autonomously extracts actionable learnings from completed code reviews and stores them as institutional knowledge in SKILL files.

## Overview

This skill analyzes code review comments, PR metadata, and discussion threads to identify high-value learnings that should be preserved for future reviews. It operates autonomously with minimal user interaction, making it suitable for CI/CD integration.

## Usage

```bash
# After completing a code review
/retrospective-review

# Or analyze specific PR
/retrospective-review 12345
```

## What It Does Autonomously

The skill performs the following steps without user prompting:

### 1. Load Review Context

- Reads local review files (`review-summary.md`, `review-inline-comments.md`)
- OR fetches GitHub PR data if PR number provided
- Detects repository owner/name from git remote

### 2. Parse Review Comments

Extracts severity markers from review comments:
- `❌ CRITICAL` - Security issues, data loss risks, broken functionality
- `⚠️ IMPORTANT` - Logic errors, incorrect behavior, significant technical debt
- `🎨 SUGGESTED` - Code style, minor improvements
- `💭 QUESTION` - Clarifications, discussions

### 3. Apply Actionability Gate

**Proceeds if**: `CRITICAL_COUNT > 0 OR IMPORTANT_COUNT > 0`

**Exits if**: Only trivial findings (🎨 SUGGESTED, 💭 QUESTION) or routine code style issues

Output: `"No significant learnings detected. Knowledge base unchanged."`

### 4. Categorize Findings (Capture Valid Issues AND False Positives)

**Purpose**: Categorize review findings to capture BOTH valid issues AND false positives as learnings, while excluding only low-value noise.

**Using gh CLI**:
```bash
# Get review comments with thread IDs
gh api "repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}/comments" \
  --jq '.[] | {id, body, path, line, isResolved: .pull_request_review_id}'
```

**Finding Categorization Logic**:

For each comment marked as ❌ CRITICAL or ⚠️ IMPORTANT:

1. **Check if comment thread is resolved** → `isResolved: true`
2. **Check if corresponding code was changed** → Look for commits after comment timestamp
3. **Categorize based on resolution + code changes**:
   - Resolved + Code Changed = **VALID ISSUE** → CAPTURE
   - Resolved + No Code Change + High Severity = **FALSE POSITIVE** → CAPTURE as learning
   - Resolved + No Code Change + Low/No Severity = **NOISE** → EXCLUDE

**Finding Categories**:

**Type 1: Valid Issue (CAPTURE)**
```
Comment: "❌ CRITICAL: Auth bypass in vault unlock"
Resolution: RESOLVED (commit abc123 added check)
Code Changed: YES

Result: VALID ISSUE - CAPTURED
Learning: Always verify permission checks in auth code
```

**Type 2: False Positive (CAPTURE as learning)**
```
Comment: "❌ CRITICAL: Missing null check on user.email"
Resolution: RESOLVED
Code Changed: NO
Discussion: "Email is guaranteed non-null by API contract"
Reply Count: 2

Result: FALSE POSITIVE - CAPTURED as learning
Learning: Check API contracts before flagging null checks
```

**Type 3: Silent Dismissal False Positive (CAPTURE)**
```
Comment: "⚠️ IMPORTANT: Consider adding retry logic"
Resolution: RESOLVED
Code Changed: NO
Discussion: NONE
Reply Count: 0

Result: FALSE POSITIVE - CAPTURED as learning
Learning: User disagreed but didn't engage; check if retry logic already exists
```

**Type 4: Low-Value Noise (EXCLUDE)**
```
Comment: "💭 QUESTION: Why use const instead of let?"
Resolution: RESOLVED
Discussion: "Const prevents reassignment"

Result: NOISE - EXCLUDED
Reason: Question, not a finding; no actionable learning
```

### 5. Extract Failed Detections

**Purpose**: Document SPECIFIC REVIEW MISTAKES made on individual PRs.

**Criteria for inclusion**:
- ✅ **Valid issues**: Caught in 2nd+ review round, near-misses
- ✅ **False positives**: Reviewer incorrectly flagged something (learn what NOT to flag)
- ✅ Either category teaches an actionable lesson
- ❌ NOT for general architectural patterns (→ repository-gotchas)
- ❌ NOT for low-value noise (trivial comments)

**Key distinction**: If you would check for this pattern in EVERY future PR, it's a **repository gotcha**, not a failed detection.

**For each failed detection, extract**:
- **Issue**: Brief description from comment
- **Why Missed**: Inferred from context
- **Detection Strategy**: Extract from reviewer suggestions
- **Severity**: `❌ CRITICAL` or `⚠️ IMPORTANT`
- **Resolution Verification**: Confirm code was changed

### 6. Extract Repository Gotchas

**Purpose**: Document ONGOING ARCHITECTURAL PATTERNS and validation philosophies.

**Criteria**:
- ✅ Architectural conventions specific to this repository
- ✅ Security/validation philosophies that differ from defaults
- ✅ Technology-specific patterns that apply to all PRs
- ✅ Common mistakes developers make repeatedly

### 7. Extract Methodology Improvements

**Purpose**: Document what worked and what didn't in the review approach.

**Examples**:
- Test-first review strategy effectiveness
- Iterative review with self-correction
- Tool usage patterns that improved efficiency

### 8. Update or Create SKILL File

If first review for this repository:
- Creates `skills/{owner}-{repo}-review-knowledge/` directory
- Initializes SKILL.md from template with metadata substitution
- Creates `references/troubleshooting.md` file

If repository SKILL exists:
- Appends new learnings to existing sections
- Updates metadata (review count, date range, last updated)

### 9. Present Extraction Summary

Shows what was captured and where it was stored.

---

## Finding Categorization

### Why Capture False Positives?

False positives ARE valuable learnings:
- **Learn what NOT to flag**: Future reviewers avoid same mistakes
- **Understand context**: Build repository-specific knowledge
- **Improve accuracy**: Reduce noise in future reviews

**Example**: Claude flagged script permissions, but SDK uses Bash tool (no +x needed) → Future reviews won't repeat this error

### What We EXCLUDE

Only low-value noise:
- ❌ Style nitpicks without severity markers
- ❌ Questions rather than findings
- ❌ Trivial suggestions
- ❌ Compliments/non-actionable comments

### Detection Command

```bash
# For each ❌ CRITICAL or ⚠️ IMPORTANT comment:
IS_RESOLVED=$(gh api "repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}/comments/${COMMENT_ID}" \
  --jq '.pull_request_review_id as $review |
        if $review then
          (gh api "repos/${OWNER}/${REPO}/pulls/reviews/${review}" --jq ".state")
        else
          "PENDING"
        end')

# Check if file changed after comment
COMMITS_AFTER=$(git log --since="$COMMENT_TIME" --format="%H" -- "$COMMENT_FILE")

# Check if there are any replies
REPLY_COUNT=$(gh api "repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}/comments/${COMMENT_ID}/replies" \
  --jq 'length')

# Strong false positive: Resolved + No code changes + No discussion
if [ "$IS_RESOLVED" = "APPROVED" ] && [ -z "$COMMITS_AFTER" ] && [ "$REPLY_COUNT" -eq 0 ]; then
  echo "⚠️  STRONG FALSE POSITIVE: Excluding from knowledge capture"
  exit 0
fi
```

---

## Template-Based SKILL Generation

When capturing knowledge for a **new repository** (first review), the system automatically:

1. **Creates repository-specific skill directory**: `skills/{owner}-{repo}-review-knowledge/`
2. **Initializes SKILL.md from template** with metadata substitution
3. **Fetches repository metadata** from GitHub API (languages, tech stack)
4. **Generates trigger-rich description** with usage scenarios
5. **Creates references/ subdirectory** for troubleshooting documentation

### Template Variables

Automatically populated from repository metadata:

```bash
{{OWNER}}         # Repository owner (e.g., "bitwarden")
{{REPO}}          # Repository name (e.g., "clients")
{{LANGUAGES}}     # Primary languages (e.g., "TypeScript, Kotlin, Swift")
{{TECH_STACK}}    # Technology description (inferred from languages)
{{DATE}}          # Current date (YYYY-MM-DD)
{{AUTHOR}}        # Author from git config
```

### Template Location

`skills/capturing-review-knowledge/templates/repository-knowledge.md.template`

### Example Generation

```bash
# First review of bitwarden/server
/retrospective-review

# System automatically:
# 1. Detects no existing SKILL for bitwarden/server
# 2. Fetches repo metadata: gh api repos/bitwarden/server/languages → "C#, SQL, PowerShell"
# 3. Creates skills/bitwarden-server-review-knowledge/SKILL.md from template
# 4. Substitutes: {{OWNER}}=bitwarden, {{REPO}}=server, {{LANGUAGES}}=C#, SQL, PowerShell
# 5. Extracts knowledge from current review
# 6. Appends to newly created SKILL.md
```

---

## Knowledge Storage Format

Each repository gets a **SKILL file** with YAML frontmatter:

```markdown
---
name: bitwarden-ai-plugins-review-knowledge
description: "Code review knowledge for bitwarden/ai-plugins (TypeScript, YAML, Bash). Usage scenarios: (1) When reviewing PRs in bitwarden/ai-plugins, (2) When encountering Claude SDK execution model questions, (3) When checking input validation patterns. Verified on TypeScript, YAML, Bash."
author: Bitwarden Code Review Team
date: 2025-12-17
---

# bitwarden/ai-plugins - Code Review Knowledge

## Repository Overview

| Item | Details |
|------|---------|
| **Repository** | [bitwarden/ai-plugins](https://github.com/bitwarden/ai-plugins) |
| **Technology Stack** | Claude Code plugins, YAML configurations, Bash scripts |
| **Primary Languages** | TypeScript, YAML, Bash |
| **Review Count** | 1 |
| **Date Range** | 2025-12-17 to 2025-12-17 |
| **Common Issue Categories** | SDK execution models, input validation philosophy |
| **Last Updated** | 2025-12-17 |

## Verified Detection Strategies

_Copy-paste ready commands for catching common issues._

## Failed Attempts (Critical Learnings)

| Issue | Why Missed | Detection Strategy | Review Date | PR Link | Severity |
|-------|------------|-------------------|-------------|---------|----------|

## Repository Gotchas

_Architectural patterns and conventions specific to this repository._

## Methodology Improvements

_What worked and what didn't in review approaches._
```

---

## Requirements

- Claude Code with plugin support
- `gh` CLI authenticated (for GitHub PR analysis)
- `jq` command-line tool (for JSON parsing)
- Git repository with GitHub remote

---

## Configuration

No special configuration required. The skill works out of the box.

---

## Example Workflow

```bash
# Complete code review
/code-review-local

# Capture knowledge autonomously
/retrospective-review

# Skill automatically:
# - Analyzes review-summary.md and review-inline-comments.md
# - Filters false positives (resolved without code changes)
# - Extracts failed detections from ❌/⚠️ comments
# - Identifies patterns from reviewer discussions
# - Updates SKILL.md file (or creates if first review)
# - Presents extraction summary

# Review what was extracted
cd .claude/plugins/claude-retrospective
git diff skills/bitwarden-clients-review-knowledge/

# Commit locally
git add skills/bitwarden-clients-review-knowledge/
git commit -m "feat(bitwarden/clients): knowledge extraction from PR #12345"

# Push or create PR when ready
```

---

## See Also

- [recalling-review-knowledge](../recalling-review-knowledge/README.md) - Retrieve institutional knowledge before reviews
- [Main Plugin README](../../README.md) - Overview and examples
