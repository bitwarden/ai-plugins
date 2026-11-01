# Intent: platform

## Purpose

Shared infrastructure that every client and every feature team uses: state, sync, storage, configuration, logging, IPC, notifications, and the SDK client lifecycle.

## Boundaries

Feature code depends on platform code. Platform code does not depend on feature code, and does not carry behavior that exists for one feature.

## Review exceptions

### Change triggers

- Changes how stored data is encrypted, or adds or changes a state migration.

### Changes that do not need the owning team

- New StateDefinition entries in state-definitions.ts that follow the existing pattern.
- Documentation and comment-only changes.
- Test-only changes.
