# Change kinds

Every change in a pull request gets exactly one kind. The kind sets the default answer to "does this need the owning team?" The kinds and their defaults are the same for every file in every repository. A module's `INTENT.md` can override a default for that module, add triggers and "do not need" entries, and raise a change to the owning team when the change conflicts with the module's intent.

Size is not a kind. A one-line rename of a public method is API-breaking. A long addition that copies an existing pattern is pattern-following.

## The kinds

The eight kinds fall into three families. The routine family stays inside what the module already is. The shape family changes how the module is built. The contract family changes what code and data outside the module depend on.

The kinds are listed from least to most serious. When a group of files contains several kinds, the most serious kind decides the group.

| Family   | Kind                | Definition                                                                                                               | Default needs the owning team |
| -------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------- |
| Routine  | `fix`               | Restores the intended behavior of existing code. Adds nothing that other code can depend on.                             | No                            |
| Routine  | `pattern-following` | Adds code that copies a pattern the module already has, and that the module's intent does not retire.                    | No                            |
| Shape    | `debt-extending`    | Adds a new use of something the module is moving away from, or weakens a guard the module relies on.                     | Yes                           |
| Shape    | `pattern-breaking`  | Adds a second way to do something the module already does.                                                               | Yes                           |
| Shape    | `special-case`      | Adds behavior to the module that only one consumer needs.                                                                | Yes                           |
| Shape    | `structural`        | Adds a module or an abstraction, adds a dependency between modules, or moves code across a module boundary.              | Yes                           |
| Contract | `api-additive`      | Adds something that code or data outside the module can depend on.                                                       | Yes                           |
| Contract | `api-breaking`      | Changes or removes something that code or data outside the module already depends on, including its observable behavior. | Yes                           |

**The contract includes stored data and released clients.** Persisted state, database schemas, and serialized models are depended on by data already written and by client versions already shipped. A change to them is a contract change even when no code signature changes.

**A test change takes the kind of the production code it changes alongside.** A change that touches only test files is `fix`. Skipping or deleting a test is not a test-only change. It weakens a guard, so it is `debt-extending`.

**Security-sensitive code is not a kind.** Teams protect cryptography, authentication, and key handling with domain critical paths, which need the owning team for every change.

## Check the mechanical indicators first

These indicators need no judgment. To tell whether two paths have different owners, use the owners from the agent's Step 4: the base commit's `CODEOWNERS`, or the PR's own assignment for a file the base gives no owner. If you cannot tell, treat the owners as different. Check the diff for them before you judge anything else. Each indicator sets the minimum kind for the change. Judgment can raise the kind, but never lower it below an indicator.

| Indicator                                                                                                                | Minimum kind     |
| ------------------------------------------------------------------------------------------------------------------------ | ---------------- |
| A removed or renamed export, or a changed signature of an exported or `public` member                                    | `api-breaking`   |
| A removed or changed HTTP route, request model property, or response model property                                      | `api-breaking`   |
| A changed or removed persisted field, state key, storage location, or database column                                    | `api-breaking`   |
| A changed DI lifetime or registration of an existing service                                                             | `api-breaking`   |
| A new export from a library entry point such as `index.ts`, or a new `public` member on a `public` type                  | `api-additive`   |
| A new HTTP route, or a new property on a request or response model                                                       | `api-additive`   |
| A new database table, column, or migration script                                                                        | `api-additive`   |
| A new import from an owner the changed file did not import from on the base commit                                       | `structural`     |
| A new `ProjectReference`, `PackageReference`, or `package.json` dependency, or a major version change of an existing one | `structural`     |
| A new DI registration of a service or an injection token                                                                 | `structural`     |
| A new project, library, or top-level module directory                                                                    | `structural`     |
| A file moved or renamed into a path that `CODEOWNERS` assigns to a different owner                                       | `structural`     |
| A new branch on a caller's identity, type, client type, or feature flag inside the module                                | `special-case`   |
| A new reference to a feature module's types, enums, or constants                                                         | `special-case`   |
| A new optional parameter or option that only the PR's own feature code passes                                            | `special-case`   |
| A new reference to a symbol marked `@deprecated` or `[Obsolete]`                                                         | `debt-extending` |
| A new `eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `#pragma warning disable`, or `[SuppressMessage]`              | `debt-extending` |
| A new `any` type, non-null assertion, or null-forgiving `!` in a module that otherwise avoids them                       | `debt-extending` |
| A skipped, disabled, or deleted test                                                                                     | `debt-extending` |
| A new entry in an exemption list, allow list, or baseline file that a check reads                                        | `debt-extending` |

Compare owners, not paths, for the import indicator. List the owners the changed file imported from on the base commit and on the head commit. The indicator fires only for an owner that is new on the head commit. A swap that replaces one import with another from the same owner, such as moving to a helper the owner now provides elsewhere, does not fire.

A new dependency between packages, such as a library importing a package it never imported before, is a question for the imported package's owner, who decides what may depend on it. When the pull request also changes that owner's files, add the new dependency to the review focus of that owner's entry. Otherwise, the import is `structural` on the importing file.

A new import from another owner's code also matches a `special-case` indicator when the imported thing belongs to a feature. Use the more serious kind, `structural`, and name both in `explanation`.

## Judge the rest

Four judgments remain after the indicators. Make all four for every change.

**Fix or behavior change?** A `fix` restores what the code was meant to do, and adds no new named thing that other code could call. A change that alters behavior the module's consumers rely on is `api-breaking`, even when no signature changes. Examples are a new default value, a different error, a different ordering, or different timing.

The base commit must show that the old behavior was wrong before you call a behavior change a `fix`. Evidence is the old code contradicting its own documentation, name, or type, or a sibling in the module doing the same job the corrected way. A test on the base commit that asserted the old behavior is evidence the behavior was deliberate. You never read the PR description, so the author's word that something is a fix is not evidence. Without evidence, the change is `api-breaking`.

**Pattern-following or pattern-breaking?** Find the existing pattern before you decide. Read the base version of the touched files from the context's `base/` export. List their siblings with `Glob` and read the ones that do the same job.

- It is `pattern-following` when the module already does the same job somewhere else, and the new code does it the same way: same base class, same helper, same registration, same file layout. The pattern must also be one the module's intent keeps. Copying a pattern that `## Direction` retires is `debt-extending`, even when the old pattern is still common in the code.
- It is `pattern-breaking` when the module already does the same job somewhere else, and the new code does it a different way. Examples are its own caching where the module has a cache, or direct storage access where the module has a state provider.
- It is `structural` when the module has no existing way to do the job, and the new code adds one.

**A move to a replacement the same pull request adds is `pattern-following`.** A call site that moves from one helper to its replacement follows a pattern even though the base commit has no other use of the replacement. All three conditions must hold:

1. The old helper and the replacement have the same owner, from the owners rule in the agent's Step 4.
2. The same pull request adds the replacement.
3. The replacement's own files need their owner in this result, so the owner reviews the new API in the same pull request.

The call site's behavior must also stay the same, apart from where the check comes from. If any condition fails, or the behavior changes, judge the call site on its own.

If you cannot find the existing pattern, do not assume one. Choose the more serious kind and use signal `ambiguous`.

**General or for one consumer?** Ask whether another consumer of the module would use the new behavior as written. If not, the change is `special-case`, whatever else it is. A change that names, checks for, or exists only because of one caller belongs to that caller, and the owning team would inherit it. A special case can look like a fix, such as a one-line condition for one client type, so check every change for it.

**Toward the module's direction or away from it?** Look for signs of a migration in the module's `INTENT.md`, especially `## Direction`, and in the touched files: a deprecated symbol, a "legacy" or "v1" name next to a newer one, or a comment that names the replacement. New code that uses the old way is `debt-extending`, even when it copies a pattern that still exists.

`debt-extending`, `pattern-breaking`, and `special-case` all add a second way of doing things inside the module. `debt-extending` grows the way the module is leaving. `pattern-breaking` adds a new mechanism. `special-case` adds a new behavior for one caller.

## Examples

### clients (TypeScript and Angular)

| Kind                | Example                                                                                  | Counter-example                                                                     |
| ------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `fix`               | Corrects an off-by-one error in a private method of an existing service.                 | Adds a new public method to fix the bug. That is `api-additive`.                    |
| `pattern-following` | Adds a new `KeyDefinition` next to the existing ones, with the same shape.               | Adds a new key that reads storage directly. That is `pattern-breaking`.             |
| `debt-extending`    | Adds a new call to a service method marked `@deprecated` in favor of an observable.      | Calls the replacement observable. That is `pattern-following`.                      |
| `pattern-breaking`  | Adds a `BehaviorSubject` cache in a component, where the module uses a state provider.   | Uses the module's existing state provider. That is `pattern-following`.             |
| `special-case`      | Adds `if (clientType === ClientType.Desktop)` inside a platform service for one feature. | Adds a client-type option that every client sets. That is `api-additive`.           |
| `structural`        | Imports a feature team's service into a platform library.                                | Imports a sibling file in the same library. That is not a cross-module dependency.  |
| `api-additive`      | Exports a new type from the library's `index.ts`.                                        | Adds a new type used only inside the library. That is `fix` or `pattern-following`. |
| `api-breaking`      | Changes an exported function's default timeout from 30 seconds to 5 seconds.             | Fixes a timeout that ignored the value the caller passed. That is `fix`.            |

### server (.NET)

| Kind                | Example                                                                                                | Counter-example                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| `fix`               | Corrects a null check inside an existing command's `Run` method.                                       | Adds a new parameter to the command's public interface. That is `api-breaking`.                     |
| `pattern-following` | Adds a new query class shaped like the existing queries, with its own interface and registration.      | Adds query logic directly to a controller. That is `pattern-breaking`.                              |
| `debt-extending`    | Adds a `#pragma warning disable` around a new call to an `[Obsolete]` repository method.               | Calls the method that replaced it. That is `pattern-following`.                                     |
| `pattern-breaking`  | Calls a repository from a controller, where the module routes all access through commands and queries. | Adds a new command that the controller calls. That is `pattern-following`.                          |
| `special-case`      | Adds a check for one organization plan type inside a shared command, for one feature.                  | Adds a policy the command reads for every plan type. That is `api-additive` or `pattern-following`. |
| `structural`        | Adds a `ProjectReference` from `Core` to a feature project.                                            | Adds a class in an existing namespace. That is not a new dependency.                                |
| `api-additive`      | Adds a new endpoint to a controller.                                                                   | Adds a private helper method in the controller. That is `fix`.                                      |
| `api-breaking`      | Removes a property from a response model that clients read.                                            | Adds an optional property to a response model. That is `api-additive`.                              |
