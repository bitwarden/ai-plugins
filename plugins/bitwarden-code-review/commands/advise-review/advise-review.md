---
description: Retrieve institutional knowledge for the current repository before starting a code review
---

Load institutional code review knowledge for the current repository. Reference the `recalling-review-knowledge` skill for detailed workflow.

**Instructions:**

1. **Detect repository context**:
   - Run `gh repo view --json nameWithOwner -q .nameWithOwner` to get owner/repo
   - Extract repository name for knowledge skill lookup

2. **Locate knowledge skill**:
   - Search for matching skill: `bitwarden-{repo-name}-review-knowledge`
   - If no matching skill exists: Inform user and suggest running `/retrospective-review` after their next code review

3. **Load knowledge files**:
   - Read `SKILL.md` from the matching knowledge skill
   - Read `references/troubleshooting.md` if present
   - Parse and display the structured knowledge sections

4. **Present knowledge organized by category**:
   - **Failed Detections**: Past review mistakes with detection strategies
   - **Repository Gotchas**: Architectural patterns and conventions specific to this codebase
   - **Methodology Improvements**: Process insights that worked or didn't
   - **Verified Detection Strategies**: Copy-paste ready commands for catching issues

5. **Provide actionable review guidance**:
   - Highlight the most critical patterns to watch for
   - Reference specific detection commands from the knowledge
   - Remind user to run `/retrospective-review` after completing their review to capture new learnings

**Error handling**:
- If repository detection fails: Provide clear error with remediation steps
- If knowledge file is malformed: Display successfully parsed sections, warn about corrupted parts
