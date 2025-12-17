---
name: writing-client-code
description: Bitwarden client code conventions for Angular and TypeScript. Use when working in the clients mono-repo, creating components, services, or modifying web/browser/desktop apps.
tools: Read, Write, Edit, Bash, Glob, Grep
---

## Repository Structure

The `clients` mono-repo contains:

- `apps/web`, `apps/browser`, `apps/desktop`, `apps/cli` — client applications
- `libs/common` — shared code for ALL clients including CLI (no Angular dependencies)
- `libs/angular` — Angular-specific code for visual clients only
- `libs/components` — Angular Component Library

Install dependencies from repo root only. Build with Nx: `npx nx serve web`.

## Angular Requirements

**New components** must use:

- OnPush change detection
- New control flow syntax (`@if`, `@for`, `@switch`)
- Standalone components
- `inject()` function for dependency injection
- Reactive Forms

**Existing components:** Follow the patterns already in the file. Don't migrate `*ngIf` → `@if`, `@Input()` decorators → `input()` signals, or other modernizations unless explicitly asked. Keep changes focused on the task.

**If asked to refactor/migrate:** Then apply modern patterns to the files in scope — but don't expand to "while we're here" refactors in other files.

## Component Patterns

**Thin components:** Components contain only view logic. Business logic belongs in services.

**Composition over inheritance:** Avoid extending components across clients. Compose using shared child components.

**Cross-client services** (in `libs/common`): Use abstract classes as interfaces — CLI uses Node, not Angular DI. Implementation prefixes: `Default*`, `Web*`, `Browser*`, `Desktop*`, `Cli*`.

## File Naming

Dashes for words, dots for types:

- `folder.service.ts` → `FolderService`
- `folder-list.component.ts` → `FolderListComponent`
- `folder.view.ts` → `FolderView`
- `cipher-type.enum.ts` → `CipherType` (const object, not enum)

## TypeScript Rules

**No enums.** Use frozen const objects with `Object.freeze()` and `as const`. Always explicitly type variables using the derived type.

**Imports:**

- Within same package (`@bitwarden/common`): relative imports
- Across packages: absolute imports (`@bitwarden/common/platform/...`)

## State Management

| Context                             | Use     |
| ----------------------------------- | ------- |
| Component local state               | Signals |
| Angular-only services               | Signals |
| Cross-client services (libs/common) | RxJS    |

**Avoid manual subscriptions.** Prefer `| async` pipe. When subscriptions are necessary, pipe through `takeUntilDestroyed()` — enforced by `prefer-takeUntil` lint rule.

## Styling

All Tailwind classes require **`tw-` prefix**:

```html
<div class="tw-bg-background-alt2 tw-p-4">
    <!-- ✅ -->
    <div class="bg-background-alt2 p-4"><!-- ❌ --></div>
</div>
```

Use Component Library (`libs/components/`) for common UI patterns.

## Testing

Use Jest with `jest-mock-extended`.
