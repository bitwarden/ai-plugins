## Operating Defaults

**Follow these. Skip one only with a stated reason.**

1. **Default to git worktrees for non-trivial Bitwarden work.**
   - For multi-file changes, experiments, or anything likely to span more than a quick edit, suggest a worktree before starting.
   - Skip the suggestion for read-only questions, single-line fixes, and tasks that are plainly throwaway.
   - When I agree, create the worktree under `.worktrees/` on a feature branch and ask me to help name it.

2. **Default to plan mode for non-trivial changes.**
   - When a task touches multiple files, crosses security boundaries, or has unclear scope, recommend plan mode before implementing.
   - For simple questions, read-only investigations, and single-line or typo-level fixes, answer directly — ceremony for its own sake wastes time.
   - When in doubt, err toward plan mode. Iterative prompting is how AI-assisted work succeeds on real features.
