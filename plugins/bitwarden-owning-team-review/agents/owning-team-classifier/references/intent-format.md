# INTENT.md

An owning team writes an `INTENT.md` for a module to say what the module is for and where it is going. Authors, authoring agents, and the classifier all read it.

`INTENT.md` does not say who owns the module. `CODEOWNERS` does that for every file. It also does not define routine work. The change kinds in [`change-kinds.md`](./change-kinds.md) do that, the same way for every file. A module without an `INTENT.md` gets the global defaults.

## Scope

An `INTENT.md` covers the directory that holds it and every directory below it. When more than one `INTENT.md` sits above a changed file, the nearest one applies.

A repository ruleset requires the owning team for every change to an `INTENT.md`, and the classifier reads it from the pull request's base commit only. A pull request cannot change the intent it is judged by.

## Shape

```markdown
# Intent: <module name>

## Purpose

<What the module is for, and what it is not for.>

## Direction

<Where the module is going: migrations in progress, what is deprecated, what replaces it.>

## Boundaries

<What may depend on the module, and what the module may depend on.>

## How things are done here

<The module's patterns: how new state, services, endpoints, or tests are added.>

## Review exceptions

### Domain critical paths

- <glob, relative to the repository root>

### Change kind defaults

- <change kind>: <owning team | any engineer>

### Change triggers

- <an observable change that needs the owning team>

### Changes that do not need the owning team

- <an observable change that any engineer can approve>
```

| Heading                                        | Required | Meaning                                                                                                                      |
| ---------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `## Purpose`                                   | Yes      | What the module is for. The classifier checks changes against it.                                                            |
| `## Direction`                                 | No       | Migrations and deprecations. New code that moves against the direction conflicts with intent.                                |
| `## Boundaries`                                | No       | Allowed dependencies in both directions. A change that crosses a stated boundary conflicts with intent.                      |
| `## How things are done here`                  | No       | The module's patterns. The classifier uses them to tell pattern-following from pattern-breaking changes.                     |
| `## Review exceptions`                         | No       | Where the module differs from the global policy. Every subsection is optional.                                               |
| `### Domain critical paths`                    | No       | Globs where every change needs the owning team. A repository ruleset is generated from this list. The classifier ignores it. |
| `### Change kind defaults`                     | No       | Overrides of a change kind's global default for this module, one line per kind, using the kind's exact name.                 |
| `### Change triggers`                          | No       | Specific changes that always need the owning team.                                                                           |
| `### Changes that do not need the owning team` | No       | Specific changes that any engineer can approve. They never override an intent conflict.                                      |

## How the classifier uses it

Intent can only raise a change to "owning team required." It never lowers one. A change that seems to fit the intent is not evidence that the change is routine.

The classifier applies these rules in order. The first rule that applies decides.

1. A change trigger that matches needs the owning team.
2. A change that contradicts a specific statement in `## Purpose`, `## Direction`, `## Boundaries`, or `## How things are done here` needs the owning team. The classifier quotes the statement.
3. An entry in the "do not need" list that describes the change exactly needs any engineer.
4. Otherwise, the change kind's default decides: the module's `### Change kind defaults` line when there is one, and the global default when there is not.

Domain critical paths sit outside this order. The ruleset requires the owning team for them whatever the classifier decides.

## How teams write intent

- **Write statements a reader can check against a diff.** "This module never depends on feature code" is checkable. "This module should stay clean" is not.
- **Name the old way and the new way.** A direction statement such as "`getSync` is deprecated; new code uses `get$`" lets the classifier spot debt-extending changes.
- **Name routine additions to exported lists.** In a module with a barrel file, such as an `index.ts` with `export *`, every new definition is public, so it meets the `api-additive` indicator and needs the owning team by default. When the module grows by routine additions, such as new key or state definitions, list them under "Changes that do not need the owning team."
- **Write exceptions as triggers, not prohibitions.** Each trigger completes the sentence "when this happens, involve the owner." A rule that says "don't" teaches an agent to find another way around it.
- **Keep it current.** Stale intent enforces the old direction. A run of "Didn't need us" labels from the feedback loop is the usual sign that an `INTENT.md` has drifted.
- **Import it from the module's `CLAUDE.md`** with a line containing `@INTENT.md`, so Claude Code loads it whenever an agent works in the module.

## Example

```markdown
# Intent: platform state

## Purpose

Typed, observable state for every client. Not a general cache.

## Direction

All reads are moving to observables. `getSync` is deprecated and will be removed. New code uses `get$`.

## Boundaries

Feature code depends on this module. This module never depends on feature code, and never carries behavior that exists for one feature.

## How things are done here

New state uses a `StateDefinition` in `state-definitions.ts` and a `KeyDefinition` in `key-definitions.ts`.

## Review exceptions

### Domain critical paths

- libs/platform/state/state-definitions.ts

### Change triggers

- Adds or changes a state migration.

### Changes that do not need the owning team

- New `KeyDefinition` entries in `key-definitions.ts` that follow the existing pattern.
```
