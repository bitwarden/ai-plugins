---
name: capturing-review-knowledge
description: Autonomously captures actionable learnings from completed code reviews by analyzing review comments, PR data, and detected issues. Extracts failed detections, repository gotchas, and methodology improvements. Presents structured knowledge for user approval before persistence.
---

# Capturing Review Knowledge

Autonomously extract actionable learnings from completed code reviews. Present structured knowledge to user for approval.

See [REFERENCE.md](REFERENCE.md) for knowledge formats and examples.

---

## Workflow

### 1. Load Review Context

**Sources** (in priority order):

1. **Local files**:
   - Check for `review-summary.md` and `review-inline-comments.md` in current directory
   - If found: Read and parse content

2. **GitHub PR** (if argument provided):
   - If PR number provided: Fetch PR data and comments from GitHub
   - Requires GitHub access (gh CLI or API)

3. **Fallback**:
   - If no local files and no PR number: Exit with error

**Extract**:
- Repository information (owner/repo)
- PR number, title, description
- All review comments with severity markers
- Commit history relevant to the PR

### 2. Assess Actionability

Scan review comments for patterns worth learning from. Trust your judgment to identify:
- Issues that were missed or caught late
- Patterns that caused confusion or mistakes
- Architectural concerns repeatedly flagged
- False positives worth documenting

**Decision**:
- **Proceed if**: Review contains actionable learnings
- **Exit if**: Only trivial findings or routine comments

Output: `"No actionable learnings detected."`

### 3. Categorize Findings

**Purpose**: Categorize review findings to capture BOTH valid issues AND false positives as learnings, while excluding low-value noise.

**For each finding that seems actionable**:

1. **Check if comment thread is resolved**
2. **Check if corresponding code was changed** (look for commits after comment timestamp that touch the flagged file/line)
3. **Categorize**:
   - Resolved + Code Changed = **VALID ISSUE** → CAPTURE (real problem that was fixed)
   - Resolved + No Code Change + Actionable Finding = **FALSE POSITIVE** → CAPTURE (reviewer mistake to learn from)
   - Resolved + No Code Change + Trivial Comment = **NOISE** → EXCLUDE (not actionable)

**CAPTURE Category 1: Valid Issues** (real problems that were fixed):
- ✅ Comment resolved AND code changed after comment
- ✅ Comment acknowledged in subsequent commit message
- ✅ Multiple review rounds addressing the issue
- ✅ Unresolved significant concerns at merge time (escalate!)

**CAPTURE Category 2: False Positives** (reviewer mistakes - learn from them):
- ✅ Comment marked as resolved/dismissed WITHOUT code changes
- ✅ Discussion shows reviewer was incorrect ("this is actually fine because...")
- ✅ Silent dismissal of significant concern (user disagreed but didn't engage)
- ✅ PR merged without addressing flagged issue (wasn't actually a problem)

**EXCLUDE Category: Low-Value Noise**:
- ❌ Style nitpicks and minor suggestions
- ❌ Questions (💭 QUESTION) rather than findings
- ❌ Suggestions without measurable benefit
- ❌ Compliments or non-actionable comments

---

### 4. Extract Failed Detections

**Purpose**: Document SPECIFIC REVIEW MISTAKES made on individual PRs.

**Criteria for inclusion**:
- ✅ **Valid issues**: Caught in 2nd+ review round (should have been earlier), near-misses
- ✅ **False positives**: Reviewer flagged something incorrectly (learn what NOT to flag)
- ✅ Either category teaches future reviewers an actionable lesson
- ❌ NOT for general architectural patterns (those go in repository-gotchas)
- ❌ NOT for ongoing validation philosophies (those go in repository-gotchas)
- ❌ NOT for low-value noise (trivial comments)

**Key distinction**: If you would check for this pattern in EVERY future PR, it's a **repository gotcha**, not a failed detection. Failed detections are one-time mistakes that teach us how to avoid similar errors.

**Search for**:
- Issues that seem significant and actionable
- Text containing: "missed", "didn't catch", "should have checked", "nearly missed"
- Issues in 2nd+ review rounds
- Cross-reference with resolution status from step 3

**For each failed detection, extract**:
- **Issue**: Brief description from comment
- **Why Missed**: Infer from context ("focused on X", "didn't notice Y", "pattern not obvious")
- **Detection Strategy**: Extract from reviewer suggestions ("should check for", "search for", "always verify", "grep for")
- **Type**: VALID_ISSUE or FALSE_POSITIVE
- **Resolution Verification**: Confirm code was changed to address issue

**Example 1: Valid Issue (CAPTURE)**:
```
Comment: "❌ CRITICAL: Auth bypass in vault unlock. Should verify permission checks."
Resolution Status: RESOLVED (commit abc123 added permission check)
Code Changed: YES (AuthViewModel.kt modified after comment)
Finding Type: VALID_ISSUE

Extract to Failed Detections:
Issue: Auth bypass in vault unlock flow
Why Missed: Focused on UI changes, didn't trace authorization logic
Detection: Always verify permission checks when auth code changes; search for checkPermission() calls
Type: VALID_ISSUE
```

**Example 2: False Positive (CAPTURE as learning)**:
```
Comment: "❌ CRITICAL: Script needs executable permissions (+x)"
Resolution Status: RESOLVED
Code Changed: NO
Discussion: "Claude SDK uses Bash tool - no +x needed"
Reply Count: 1
Finding Type: FALSE_POSITIVE

Extract to Failed Detections:
Issue: Script flagged for +x permissions when SDK uses Bash tool
Why Missed: Didn't understand Claude SDK execution model
Detection: Check AGENT.md tools: section for bash: references before flagging permissions
Type: FALSE_POSITIVE
```

**Example 3: False Positive with Silent Dismissal (CAPTURE)**:
```
Comment: "⚠️ IMPORTANT: Missing null check on user.email"
Resolution Status: RESOLVED
Code Changed: NO
Discussion: NONE (silent dismissal)
Reply Count: 0
Finding Type: FALSE_POSITIVE

Extract to Failed Detections:
Issue: Null check suggested for field guaranteed non-null by API contract
Why Missed: Didn't verify API contract nullability guarantees
Detection: Check API interface for @NonNull annotations or validation logic before flagging null checks
Type: FALSE_POSITIVE
```

**Example 4: Low-Value Noise (EXCLUDE)**:
```
Comment: "💭 QUESTION: Why use const here instead of let?"
Resolution Status: RESOLVED
Discussion: "Const prevents reassignment"
Finding Type: NOISE

Result: EXCLUDED - Question, not a finding; no actionable learning
```

### 5. Extract Repository Gotchas

**Purpose**: Document ONGOING ARCHITECTURAL PATTERNS and validation philosophies.

**Criteria for inclusion**:
- ✅ Architectural conventions specific to this repository
- ✅ Security/validation philosophies that differ from defaults
- ✅ Technology-specific patterns that apply to all PRs
- ✅ Common mistakes developers make repeatedly
- ❌ NOT for one-time review mistakes (those go in failed-detections)

**Key distinction**: If this is something to check in EVERY future PR, it's a **repository gotcha**. If it was a specific mistake on ONE PR, it's a failed detection.

**Search for architectural/pattern discussions**:
- "violates [pattern]"
- "should follow [convention]"
- "this breaks [architecture]"
- Security warnings
- Common mistake patterns

**Extract**:
- **Pattern**: Name and description from discussion
- **Common Mistake**: What went wrong
- **Detection Strategy**: How to check for violations
- **Impact**: Consequences from comments

### 6. Extract Methodology Insights

**Infer from review metadata**:
- Large PR (>500 lines) with multiple rounds → Suggest "Architecture-first review"
- Tests caught logic errors → Note "Test-first review effective"
- Security issue in late round → Flag "Security path tracing needed"

### 7. Present Extracted Knowledge to User

**Format knowledge for user approval** before persistence.

**Use templates as presentation format**:
- Read `templates/repository-knowledge.md.template` for structure
- Read `templates/troubleshooting.md.template` for error mapping format
- Substitute extracted data into template structure

**Presentation Structure**:

```markdown
## ✅ Code Review Knowledge Extracted

**Repository**: {owner}/{repo}
**PR**: #{pr_number} - {title}
**Review Date**: {date}
**Findings**: {finding_count} actionable learnings identified

---

### Failed Detections Identified ({count})

{For each failed detection}:
**{n}. {Issue Description}**
- **Why Missed**: {reasoning}
- **Detection Strategy**: {how to catch this}
- **Type**: {VALID_ISSUE or FALSE_POSITIVE}

---

### Repository Gotchas Identified ({count})

{For each gotcha}:
**{Pattern Name}**
- **Pattern**: {description}
- **Common Mistake**: {what goes wrong}
- **Detection Strategy**: {how to check}
- **Impact**: {consequences}

---

### Methodology Insights ({count})

{For each insight}:
**{Strategy Name}**
- **What Worked**: {effective approaches}
- **What Didn't Work**: {ineffective approaches}
- **Lesson**: {key takeaway}
- **Applicability**: {when to use}

---

### Next Steps

This knowledge is ready to be added to the `{owner}-{repo}-review-knowledge` skill.

**To persist** (future enhancement):
- Knowledge will be formatted as SKILL.md with YAML frontmatter
- Submitted as PR to knowledge repository
- Available via `/advise-review` after merge

**For now**: Review the extracted knowledge above and approve if accurate.
```

---

## Error Handling

**No review context**:
- If no local files AND no PR data available:
  - Output: `"❌ No review context found. Usage: /retrospective-review [PR#]\n    Or ensure review-summary.md and review-inline-comments.md exist in current directory."`
  - Exit with error code

**GitHub access required but unavailable**:
- If PR number provided but cannot access GitHub:
  - Output: `"❌ Cannot fetch PR data. Ensure gh CLI is installed and authenticated, or provide local review files."`
  - Exit with error code

**Secret detection** (before presenting):
- Scan extracted content for patterns: `(api[_-]?key|password|token|secret|credential)`
- Warn: `"⚠️ Warning: Potential secret detected in extracted knowledge. Review carefully before persistence."`

---

## Tools

- **Read**: Load review files, templates for presentation format
- **Bash**: Repository detection, GitHub API access, file operations
