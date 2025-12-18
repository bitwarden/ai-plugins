# Contributing to Bitwarden Code Review Plugin

## Plugin Updates

**Frequency**: As needed for organizational standard changes

**Process**:

1. Update `agents/bitwarden-code-reviewer/AGENT.md`
2. Test on 3-5 representative PRs from different repositories
3. Create pull request for review
4. Merge and publish to marketplace

## Quality Checks

Before merging changes:

- [ ] Agent follows Claude Code agent conventions
- [ ] YAML frontmatter is valid (name, description, tools, model)
- [ ] Token usage measured
- [ ] Tested on actual PRs from multiple repositories
- [ ] No regression in review quality
