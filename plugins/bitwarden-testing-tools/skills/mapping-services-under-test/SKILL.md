---
name: mapping-services-under-test
description: "Determine which Bitwarden local development services are required for a given set of routes and the current branch diff. Use this skill when given the routes the tests will navigate to (extracted from an Application Context's ## States section), or when asked 'which services do I need running' or 'what should I start for these tests'. The skill runs its own `git -C <repo-path> diff --name-only origin/main...HEAD`, consults references/services.md, and returns the union of services required by route-based dependencies and file-path-based dependencies. Returns service names with their URLs and ports."
allowed-tools: "Read, Grep, Glob, Bash(git -C * diff:*)"
---

Given the routes the tests will navigate to AND the affected repos, determine which local services are required to run web tests. The skill runs its own `git -C <repo-path> diff --name-only origin/main...HEAD` against each affected repo to obtain the changed file list, then consults `${CLAUDE_SKILL_DIR}/references/services.md` for the dependency map.

Paths written `references/...` in this skill resolve relative to the skill directory (`${CLAUDE_SKILL_DIR}`).

## Inputs

- **Routes:** list of URLs the tests will navigate to (typically extracted from an Application Context's `## States` section by the calling agent).
- **Affected repos:** the same repos passed to `scoping-playwright-application-context` — used as scope for `git diff`.

## Procedure

1. For each affected repo, run `git -C <repo-path> diff --name-only origin/main...HEAD` and collect the resulting file paths. If the command fails — the repo path does not resolve, or `origin/main` is not present locally — stop and report that the diff base could not be resolved, rather than proceeding on routes alone (which would silently under-report path-based services).
2. For each file path, match against the `Required by:` clauses in `${CLAUDE_SKILL_DIR}/references/services.md` to determine which services that file's change requires.
3. For each route, match against the route-based `Required by:` clauses in `${CLAUDE_SKILL_DIR}/references/services.md` to determine which services that route requires. A route that matches no route-based clause contributes nothing on its own — do not guess a service for it; it is backstopped by the step 5 fallback only when the union is otherwise empty.
4. Take the union of services from steps 2 and 3.
5. If the union is empty (e.g., repo-root tooling or CI-config changes with no routes and no service-mapped paths), fall back to the `Web` + `Api` + `Identity` baseline.
6. Identify the primary test URL — the web vault (`https://localhost:8080`) when any web vault route is present, otherwise the Bitwarden Portal (`http://localhost:62911`) when only Admin routes are present.

## Output

Return the output as a markdown block whose first non-empty line is the literal heading `## Required Services`. Below that heading, list each required service as a bullet with name, URL, and port. Clearly note the **primary test URL** since it drives the render verification step.

The leading token of each bullet MUST be the entry's **Health-check name** from `${CLAUDE_SKILL_DIR}/references/services.md`, not its heading. The downstream health-check step consumes that token verbatim and accepts exactly this closed set, rejecting anything else:

`Api`, `Identity`, `Billing`, `billing-pricing`, `Web`, `Admin`, `Notifications`, `Events`, `Icons`

So an Admin-scoped run emits `- Admin — http://localhost:62911 (port 62911)`, never `- Bitwarden Portal — ...`.

If a change or route resolves to a service that has no entry in `${CLAUDE_SKILL_DIR}/references/services.md` — no Health-check name, URL, or port to cite — do not invent one. Stop and report the unmapped service so the reference can be extended, rather than emitting a guessed URL or a token outside the closed set above.

Example:

```markdown
## Required Services

- Api — `http://localhost:4000` (port 4000)
- Identity — `http://localhost:33656` (port 33656)
- Web — `https://localhost:8080` (port 8080) **(primary test URL)**
```
