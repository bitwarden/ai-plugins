---
argument-hint: [PR#]
description: Analyze completed code review and capture institutional knowledge if actionable learnings are found
---

Analyze a completed code review to extract institutional knowledge for the repository. Load the `capturing-review-knowledge` skill for detailed workflow guidance.

**Instructions:**

1. **Determine review source**:
   - If `$ARGUMENTS` contains a PR number: Fetch PR data using `gh pr view $ARGUMENTS` and review comments via `gh api`
   - If no arguments: Check for local files `review-summary.md` and `review-inline-comments.md` in current directory
   - If neither exists: Exit with error explaining usage options

2. **Detect repository context**:
   - Run `gh repo view --json nameWithOwner -q .nameWithOwner` to get owner/repo
   - Identify the corresponding knowledge skill: `skills/bitwarden-{repo-name}-review-knowledge/`

3. **Assess actionability** before extracting:
   - Scan for failed detections (issues missed or caught late)
   - Look for repository-specific gotchas discovered
   - Identify methodology insights (what worked, what didn't)
   - If only trivial findings or routine comments exist, report "No actionable learnings detected" and exit

4. **Categorize findings** using resolution status:
   - **VALID_ISSUE**: Comment resolved AND code changed → real problem fixed
   - **FALSE_POSITIVE**: Comment resolved WITHOUT code change → reviewer mistake to learn from
   - **NOISE**: Trivial comments, style nitpicks, questions → exclude

5. **Extract knowledge** in standard format:
   - **Failed Detections**: Issue, Why Missed, Detection Strategy, Type (VALID_ISSUE/FALSE_POSITIVE)
   - **Repository Gotchas**: Pattern, Common Mistake, Detection Strategy, Impact
   - **Methodology Insights**: What Worked, What Didn't, Lesson, Applicability

6. **Present to user for approval**:
   - Format extracted knowledge using the template structure from the skill
   - Show repository, PR number, finding count
   - List each extraction with actionable details
   - Ask user to confirm accuracy before any persistence

**Quality threshold**: Only capture learnings that would prevent future review failures or significantly improve review effectiveness.
