# Jira Link Types and Relationships

This document explains common Jira link types and their meanings to help understand issue relationships.

## Standard Link Types

### Hierarchical Relationships
- **Parent/Child**: Hierarchical relationship between issues (e.g., Epic -> Story -> Sub-task)
- **Sub-task**: A sub-task is a piece of work that is required to complete a task
- **Epic Link**: Links an issue to an epic (a large body of work)

### Blocking Relationships
- **Blocks/Blocked by**: Indicates that one issue prevents progress on another
- **Depends on/Dependency**: One issue relies on another to be completed first

### Related Work
- **Relates to**: General relationship indicating issues are connected
- **Duplicates/Duplicated by**: Indicates issues are duplicates of each other
- **Clones/Cloned by**: One issue is a copy of another
- **Supersedes/Superseded by**: One issue replaces another

### Cause-Effect
- **Causes/Caused by**: One issue is the root cause of another
- **Problem/Incident**: Relates problems to their incidents

### Testing
- **Tests/Tested by**: Links issues to their test cases
- **Discovered in**: Links a bug to the version where it was found

## Remote Links

Remote links connect Jira issues to external resources:
- **Confluence Pages**: Documentation, requirements, design docs
- **GitHub/Bitbucket**: Pull requests, commits, branches
- **Other Tools**: External tracking systems, wikis, etc.

## Understanding Context

When reading an issue thoroughly, consider:

1. **Upstream Dependencies**: What blocks this issue? (Blocked by, Depends on)
2. **Downstream Impact**: What does this issue block? (Blocks)
3. **Related Context**: What provides background? (Relates to, Confluence links)
4. **Hierarchy**: What's the bigger picture? (Parent, Epic)
5. **Implementation Details**: What are the sub-components? (Sub-tasks)
6. **Historical Context**: What led to this? (Clones, Duplicates, Supersedes)

## Priority of Reading

When following links to understand an issue:

1. **High Priority**: Blocks, Depends on, Parent, Epic Link, Confluence documentation
2. **Medium Priority**: Sub-tasks, Related issues
3. **Low Priority**: Clones, Duplicates, Historical superseded issues

Consider stopping the traversal at 2 levels beyond the main issue unless specific links indicate critical context.
