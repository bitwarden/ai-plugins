# Planning and Writing Code Plugin

Execution planning workflow for implementing features from Jira tickets using TDD and parallelization-aware plans.

## Overview

This plugin provides a three-command workflow for creating, validating, and implementing technical execution plans. Each command is designed to be run in sequence:

1. **Create Plan** — Fetch Jira context, clarify requirements, and produce a detailed stage-by-stage plan
2. **Review Plan** — Validate all codebase references, check plan quality, and produce a verdict before any code is written
3. **Implement Plan** — Execute the validated plan stage by stage, loading Bitwarden conventions for the target repo

## Installation

```bash
/plugin install planning-and-writing-code@bitwarden-marketplace
```

Restart Claude Code after installation.

## Commands and Usage

### `/planning-and-writing-code:create-plan [Jira-Key | task description]`

Creates a detailed execution plan from a Jira ticket or task description.

- Automatically fetches and synthesizes Jira + linked Confluence documentation
- Asks clarifying questions before writing the plan
- Searches the codebase for existing patterns and conventions to reuse
- Requires TDD: tests are planned before implementation for any testable code
- Produces a dependency graph for parallelizable stages
- Writes the plan to `~/.claude/plans/<key>-<summary>.md`

```bash
/planning-and-writing-code:create-plan PM-1234
/planning-and-writing-code:create-plan "add rate limiting to the API gateway"
```

---

### `/planning-and-writing-code:review-plan [plan-file-path]`

Validates a plan file before implementation begins.

- Auto-locates the most recent plan in `~/.claude/plans/` if no path is given
- Verifies every file path, class, method, and namespace against the actual codebase
- Assesses requirements completeness, TDD coverage, and parallelization correctness
- Returns a verdict: 🔴 Needs Revision | 🟡 Minor Issues | 🟢 Ready to Write
- Writes the review to `<plan-name>-review.md` in the same directory

```bash
/planning-and-writing-code:review-plan
/planning-and-writing-code:review-plan ~/.claude/plans/PM-1234-add-rate-limiting.md
```

---

### `/planning-and-writing-code:implement-plan [plan-file-path]`

Implements a validated plan stage by stage.

- Auto-locates the most recent plan in `~/.claude/plans/` if no path is given
- Loads `bitwarden-software-engineer` conventions for server and/or client repos as needed
- Marks each stage ✅ Complete in the plan file as it finishes
- Runs `dotnet format` / `npm run lint` after all stages complete

```bash
/planning-and-writing-code:implement-plan
/planning-and-writing-code:implement-plan ~/.claude/plans/PM-1234-add-rate-limiting.md
```

## Skills Included

These skills are invoked internally by the commands above. They can also be used directly in conversations.

| Skill | Description |
|-------|-------------|
| `structuring-execution-plans` | Plan template, TDD requirements, and parallelization analysis framework |
| `reviewing-plan-quality` | Anti-hallucination checks and plan quality assessment criteria |
| `validating-codebase-references` | Verifies file paths, classes, methods, and namespaces against the actual codebase |

## Plugin Structure

```
planning-and-writing-code/
├── .claude-plugin/
│   └── plugin.json                           # Plugin metadata
├── commands/
│   ├── create-plan/
│   │   └── create-plan.md                    # Plan creation command
│   ├── review-plan/
│   │   └── review-plan.md                    # Plan review command
│   └── implement-plan/
│       └── implement-plan.md                 # Plan implementation command
├── skills/
│   ├── structuring-execution-plans/
│   │   └── SKILL.md                          # Plan template and TDD framework
│   ├── reviewing-plan-quality/
│   │   └── SKILL.md                          # Plan quality assessment
│   └── validating-codebase-references/
│       └── SKILL.md                          # Codebase reference verification
├── CHANGELOG.md
└── README.md
```

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

See [LICENSE.txt](../../LICENSE.txt).
