---
name: determining-required-services
description: Determine which Bitwarden local development services are required for a given set of routes and the current branch diff. Use this skill when given the routes the tests will navigate to (extracted from an Application Context's ## States section). The skill runs its own `git diff --name-only`, consults references/services.md, and returns the union of services required by route-based dependencies and file-path-based dependencies. Returns service names with their URLs and ports.
---
Given the routes the tests will navigate to AND the affected repos, determine which local services are required to run web tests. The skill runs its own `git diff --name-only origin/main...HEAD -- <repo-path>` against each affected repo to obtain the changed file list, then consults `${CLAUDE_SKILL_DIR}/references/services.md` for the dependency map.

## Inputs

- **Routes:** list of URLs the tests will navigate to (typically extracted from an Application Context's `## States` section by the calling agent).
- **Affected repos:** the same repos passed to `exploring-application-context` — used as scope for `git diff`.

## Procedure

1. For each affected repo, run `git diff --name-only origin/main...HEAD -- <repo-path>` and collect the resulting file paths.
2. For each file path, match against the `Required by:` clauses in `references/services.md` to determine which services that file's change requires.
3. For each route, match against the route-based `Required by:` clauses in `references/services.md` to determine which services that route requires.
4. Take the union of services from steps 2 and 3.
5. If the union is empty (e.g., only `clients/apps/web/**` template-only changes with no routes), fall back to the Web vault frontend + Api + Identity baseline.
6. Identify the primary test URL — the web vault (`https://localhost:8080`) when any web vault route is present, otherwise the Bitwarden Portal (`http://localhost:62911`) when only Admin routes are present.

## Output

Return the output as a markdown block whose first non-empty line is the literal heading `## Required Services`. Below that heading, list each required service as a bullet with name, URL, and port. Clearly note the **primary test URL** since it drives the render verification step.

Example:

```markdown
## Required Services

- Api — `http://localhost:4000` (port 4000)
- Identity — `http://localhost:33656` (port 33656)
- Web — `https://localhost:8080` (port 8080) **(primary test URL)**
```
