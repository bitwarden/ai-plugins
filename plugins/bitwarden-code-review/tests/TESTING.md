# Bitwarden Code Review Plugin Test Plan

This document contains manual test scenarios for validating the Bitwarden Code Review plugin's functionality.

## Prerequisites

- Ensure your working directory is `ai-plugins/plugins/bitwarden-code-review` prior to running these tests
- Have Claude Code CLI installed and configured
- Have `gh` CLI installed and authenticated for PR-related tests

## Test Categories

1. [Skill Tests](#skills) - Individual skill validation
2. [Agent Integration Tests](#agent-integration-tests) - Full review workflow
3. [Security Tests](#security-tests) - Permission boundary validation
4. [Output Format Tests](#output-format-tests) - Comment formatting validation
5. [Thread Detection Tests](#thread-detection-tests) - Duplicate prevention

---

## Skills

### Overview

The plugin includes two specialized skills that the agent invokes during reviews:

- `classifying-review-findings` - Categorizes findings by severity
- `posting-bitwarden-review-comments` - Formats PR comments

---

### Skill 1: `posting-bitwarden-review-comments`

#### Discovery Test

```bash
claude -p "What Claude Code skill are available in this plugin?"
```

✅ Should list `posting-bitwarden-review-comments`

#### Invocation Tests

| Test                         | Command                                                                                                                                                                       | Expected                                                    |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **Format a finding**         | `claude -p "Using posting-bitwarden-review-comments, format this as a PR comment: null pointer on line 45 of UserService.ts"`                                                 | Uses emoji + severity format                                |
| **Multiple findings**        | `claude -p "Using posting-bitwarden-review-comments, format these findings: 1) SQL injection line 10, 2) missing validation line 25"`                                         | Uses "Finding 1:" and "Finding 2:" - NOT "#1" or "Issue #1" |
| **Long comment formatting**  | `claude -p "Using posting-bitwarden-review-comments, format this detailed comment: [provide 15 line explanation of why a fictional api endpoint is a medium security risk ]"` | Wraps details in `<details>` tags                           |
| **Short comment formatting** | `claude -p "Using posting-bitwarden-review-comments, format this brief comment: Missing null check"`                                                                          | No `<details>` needed for short comments                    |
| **Summary comment**          | `claude -p "Using posting-bitwarden-review-comments, format a summary for a clean review with no issues"`                                                                     | Brief approval, no praise sections                          |
| **Summary with issues**      | `claude -p "Using posting-bitwarden-review-comments, format a summary: 2 critical issues found in auth.ts"`                                                                   | Lists critical issues, references inline comments           |
| **Reject praise request**    | `claude -p "Using posting-bitwarden-review-comments, format this comment: Great job on the test coverage!"`                                                                   | Refuses or warns - praise comments forbidden                |

#### Anti-Pattern Tests

| Test                       | Command            | Should NOT happen                          |
| -------------------------- | ------------------ | ------------------------------------------ |
| **No hashtag numbers**     | Any finding format | Never outputs "#1", "#2", etc.             |
| **No "Issue" terminology** | Any finding format | Never uses "Issue 1", always "Finding 1"   |
| **No Strengths section**   | Summary format     | Never includes "Strengths" or "Highlights" |

---

### Skill 2: `classifying-review-findings`

#### Discovery Test

```bash
claude -p "What skills are available?"
```

✓ Should list `classifying-review-findings`

#### Invocation Tests

| Test                   | Command                                                                                                                    | Expected                                       |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| **Critical severity**  | `claude -p "Using classifying-review-findings, classify: SQL injection where user input concatenated into query"`          | ❌ CRITICAL                                    |
| **Important severity** | `claude -p "Using classifying-review-findings, classify: missing null check before accessing user.email"`                  | ⚠️ IMPORTANT                                   |
| **Debt severity**      | `claude -p "Using classifying-review-findings, classify: copy-pasted validation logic that exists in ValidationUtils"`     | ♻️ DEBT                                        |
| **Suggested severity** | `claude -p "Using classifying-review-findings, classify: extracting this would reduce cyclomatic complexity from 12 to 5"` | 🎨 SUGGESTED                                   |
| **Question severity**  | `claude -p "Using classifying-review-findings, classify: unclear if this conflicts with billing system requirements"`      | ❓ QUESTION                                    |
| **Verification check** | `claude -p "Using classifying-review-findings, classify: possible race condition in React setState"`                       | Asks verification questions before classifying |
| **Reject vague**       | `claude -p "Using classifying-review-findings, classify: function could be shorter"`                                       | Rejects - no measurable improvement            |

#### Rejection Tests

| Test                  | Command                                                                                           | Expected                            |
| --------------------- | ------------------------------------------------------------------------------------------------- | ----------------------------------- |
| **Reject praise**     | `claude -p "Using classifying-review-findings, classify: excellent error handling here"`          | Rejects - not a valid finding       |
| **Reject vague**      | `claude -p "Using classifying-review-findings, classify: code could be cleaner"`                  | Rejects - no measurable improvement |
| **Reject preference** | `claude -p "Using classifying-review-findings, classify: I would name this variable differently"` | Rejects - style preference          |

---

### Skill 3: `posting-review-summary`

#### Discovery Test

```bash
claude -p "What skills are available for posting review summaries?"
```

✅ Should list `posting-review-summary`

#### Invocation Tests

| Test                     | Command                                                                                                                                                                | Expected                                                      |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Context detection**    | `claude -p "Using posting-review-summary, explain how you determine where to post the summary"`                                                                        | Mentions sticky comment tool vs local file                    |
| **Format with findings** | `claude -p "Using posting-review-summary, format a summary with: 1 CRITICAL sql injection in auth.ts:45, 1 SUGGESTED additional covering unit test in api.test.ts:20"` | Uses collapsed `<details>` section, CRITICAL before SUGGESTED |
| **Clean PR format**      | `claude -p "Using posting-review-summary, format a summary for a PR with no issues"`                                                                                   | Brief approval, no `<details>` section                        |
| **Deficient title**      | `claude -p "Using posting-review-summary, format a summary for a PR titled 'fix bug' with no description"`                                                             | Includes ❓ about title in Details section                    |
| **Adequate title**       | `claude -p "Using posting-review-summary, format a summary for a PR titled 'Fix null check in UserService.getProfile' with brief description"`                         | NO metadata comments                                          |
| **Missing screenshots**  | `claude -p "Using posting-review-summary, format a summary for a PR that changes UI components but has no screenshots"`                                                | Includes ❓ requesting screenshots                            |
| **Metadata limit**       | `claude -p "Using posting-review-summary, the PR has: vague title, no description, no test plan, no Jira link, no screenshots. Format the summary."`                   | Max 3 lines of metadata feedback total                        |

#### Anti-Pattern Tests

| Test                   | Command            | Should NOT happen                                         |
| ---------------------- | ------------------ | --------------------------------------------------------- |
| **No gh pr comment**   | Any summary format | Never suggests using `gh pr comment`                      |
| **No praise sections** | Summary format     | Never includes "Strengths" or "Highlights" headers        |
| **No inline metadata** | Any metadata issue | Never suggests posting metadata issues as inline comments |
| **No perfect-seeking** | Adequate PR        | Never comments on "could be better" metadata              |

---

### Skill 4: `detecting-existing-threads`

#### Discovery Test

```bash
claude -p "What skills are available for detecting existing threads?"
```

✅ Should list `detecting-existing-threads`

#### Invocation Tests

| Test                         | Command                                                                                                                                               | Expected                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| **PR number from context**   | `claude -p "Using detecting-existing-threads skill, detect existing threads for PR #123"`                                                             | Determines PR number is 123, fetches threads |
| **PR URL parsing**           | `claude -p "Using detecting-existing-threads skill, detect threads for https://github.com/bitwarden/server/pull/6778"`                                | Extracts PR 456, owner/repo correctly        |
| **Severity detection**       | `claude -p "Using detecting-existing-threads skill, what severities exist in https://github.com/bitwarden/server/pull/6778?"`                         | Detects ❌→CRITICAL, ⚠️→IMPORTANT, etc.      |
| **Thread matching - exact**  | `claude -p "Using detecting-existing-threads skill, check if Program.cs:89 already has a thread in PR https://github.com/bitwarden/server/pull/6778"` | Finds exact match by file + line             |
| **Thread matching - nearby** | `claude -p "Using detecting-existing-threads skill, check if Program.cs:93 has a thread in https://github.com/bitwarden/server/pull/6778"`            | Finds nearby match (within ±5 lines)         |
| **Issue persists**           | `claude -p "Using detecting-existing-threads skill, existing thread has same issue. What should be done by Claude?"`                                  | Respond in existing thread                   |
| **Issue resolved**           | `claude -p "Using detecting-existing-threads skill, existing thread shows issue fixed. What should be done by Claude?"`                               | Note resolution, don't re-raise              |

---

### Integration Test

Run a full review scenario that should invoke multiple skills:

```bash
claude -p "Review this code change for PR #123. Use classifying-review-findings for severity, and posting-bitwarden-review-comments to format output:

File: src/auth/LoginService.ts, Line 45:
const query = 'SELECT * FROM users WHERE id = ' + userId;

File: src/utils/helpers.ts, Line 12:
// This could be cleaner
function processData(items) { ... }
"
```

**Expected behavior:**

1. `classifying-review-findings` - SQL injection → CRITICAL, "could be cleaner" → rejected
2. `posting-bitwarden-review-comments` - Formats output correctly

---

## Troubleshooting

| Symptom                        | Check                                               |
| ------------------------------ | --------------------------------------------------- |
| Skill not found                | Is `Skill` in AGENT.md tools list?                  |
| Skill not invoked              | Does prompt contain trigger words from description? |
| Wrong skill invoked            | Are descriptions distinct enough?                   |
| Skill invoked but wrong output | Check SKILL.md instructions                         |
