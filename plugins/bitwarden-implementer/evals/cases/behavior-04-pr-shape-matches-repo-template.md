# behavior-04: PR shape matches repo template and label conventions

## Input

A completed diff ready to ship in a Bitwarden repo with a standard PR template (server, clients, or SDK).

## Expectations

- PR title has the conventional commit type prefix that drives the correct `t:` label.
- PR body fills in every section of the repo's PR template.
- The correct `ai-review` label is applied per repo convention.

## Pass criteria

- **Structure:** PR title matches `[PM-XXXXX] <type>: <summary>`.
- **Structure:** PR body has all required template sections filled in (Objective, Code changes, Screenshots if UI, etc. — repo-dependent).
- **Behavior:** the applied `ai-review` label matches the repo's guidance.
- **Behavior:** `labeling-changes` guided the type selection; ambiguous cases were surfaced not guessed.

## Runs

| Run | Title | Body | Label | Notes |
| --- | ----- | ---- | ----- | ----- |
| 1   |       |      |       |       |
| 2   |       |      |       |       |
| 3   |       |      |       |       |
