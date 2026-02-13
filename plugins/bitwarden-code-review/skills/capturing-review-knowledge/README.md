# capturing-review-knowledge

Autonomously extracts actionable learnings from completed code reviews and stores them as institutional knowledge in SKILL files.

## Overview

This skill analyzes code review comments, PR metadata, and discussion threads to identify high-value learnings that should be preserved for future reviews. It operates autonomously with minimal user interaction.

## Usage

```bash
# After completing a code review
/retrospective-review

# Or analyze specific PR
/retrospective-review 12345
```

## What It Does

The skill autonomously:

1. **Loads review context** from local files or GitHub PR data
2. **Assesses actionability** - exits early if only trivial findings
3. **Categorizes findings** - captures both valid issues AND false positives as learnings
4. **Extracts failed detections** - specific review mistakes to learn from
5. **Extracts repository gotchas** - ongoing architectural patterns
6. **Extracts methodology insights** - what worked and what didn't
7. **Presents knowledge for approval** before persistence

## Implementation Details

For detailed workflow steps, finding categorization logic, examples, and template formats, see [SKILL.md](SKILL.md).

## Requirements

- Claude Code with plugin support
- `gh` CLI authenticated (for GitHub PR analysis)
- Git repository with GitHub remote

## Example Workflow

```bash
# Complete code review
/code-review-local

# Capture knowledge autonomously
/retrospective-review

# Review what was extracted
git diff plugins/bitwarden-code-review/skills/

# Commit when ready
git add plugins/bitwarden-code-review/skills/
git commit -m "feat(knowledge): extraction from PR #12345"
```

## See Also

- [SKILL.md](SKILL.md) - Detailed implementation and workflow
- [recalling-review-knowledge](../recalling-review-knowledge/README.md) - Retrieve institutional knowledge before reviews
- [Main Plugin README](../../README.md) - Overview and examples
