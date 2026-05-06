# Example: Triage Workflow

Three representative cases showing how the verdict changes depending on what the code investigation finds.

---

## Case 1: Bug silently fixed by a refactor (No longer relevant)

**User request**: "Is PM-XXXX still relevant?"

**Ticket**: Bug: a cache extension method calls `cache.Get(key)` outside a try/catch, so a cache connection failure throws an unhandled exception instead of returning null.

**Workflow**:

1. Fetch PM-XXXX via `get_issue` → extract the described behavior and identifiers: `TryGetValue`, `DistributedCacheExtensions`, `cache.Get`.
2. Grep in `server/src/` → `DistributedCacheExtensions.cs` exists, `TryGetValue` present.
3. Read the file → the method exists but has **zero callers** in the codebase — the code path described by the ticket is dead.
4. `git log` on the file → confirms no callers were added recently; the extension was made obsolete by a service refactor.

**Verdict**: No longer relevant. `TryGetValue` still has the exception-swallowing bug described in the ticket, but the method has no callers — the code path it describes is unreachable. Safe to close with a note that the method can be deleted.

---

## Case 2: Task implementation gap confirmed (Still relevant)

**User request**: "Is PM-YYYY still relevant?"

**Ticket**: Task: when only one member/group has "Can Manage" permission on a collection, that row should be disabled (greyed out) with a tooltip, rather than allowing removal and showing a validation error on save.

**Workflow**:

1. Fetch PM-YYYY via `get_issue` → identifiers extracted: `validateCanManagePermission`, `managePermissionRequired`, `AccessItemView`, `readonly`.
2. Grep in `clients/apps/web/src/` → `validateCanManagePermission` found in `collection-dialog.component.ts:564` and wired into the form at lines 331–333. The i18n key `managePermissionRequired` resolves to "At least one member or group must have can manage permission."
3. Read `collection-dialog.component.html` → an error div shows the `managePermissionRequired` message when the validator fires — the error-on-submit path is what's there.
4. Check `AccessItemView` model → has a `readonly` flag that disables the permission editor and keeps the row selected, but no logic in the component or template computes "this is the last Manage-permission row → set `readonly: true`."
5. `git log --since` on both files → no recent commits touching the disabled-row behavior.

**Verdict**: Still relevant. The current implementation is the error-on-submit model: `validateCanManagePermission` blocks save when no Manage permission exists, showing an error at `collection-dialog.component.html:91-96`. The required behavior — proactively disabling the last Manage row with a tooltip — has not been implemented. `AccessItemView.readonly` could support it, but the reactive logic that sets it has never been written.

---

## Case 3: Spike obsoleted by later architectural work (No longer relevant)

**User request**: "Is PM-ZZZZ still relevant?"

**Ticket**: Spike from 2022: ~7,000 users have `Premium = false` but a future `PremiumExpirationDate`. The referenced code in `UserService.cs` sets `Premium = false` while preserving the expiration date. Investigate whether this is broken or intentional.

**Workflow**:

1. Fetch PM-ZZZZ via `get_issue` → identifiers extracted: `DisablePremiumAsync`, `PremiumExpirationDate`, `Premium = false`.
2. Grep in `server/src/` → `DisablePremiumAsync` still present at `UserService.cs:894`; sets `user.Premium = false` with `user.PremiumExpirationDate = expirationDate` — same as described.
3. Search how `Premium` is used for access control → `ValidateUserPremiumAsync` in `LicensingService.cs` returns `user.Premium` directly for cloud users. No check on `PremiumExpirationDate`.
4. Find a more recent `UserPremiumAccessView` SQL view → `PersonalPremium` mapped directly from `U.[Premium]`; expiration date not consulted.

**Verdict**: No longer relevant as an open investigation. The inconsistency (`Premium = false` with a future `PremiumExpirationDate`) still exists in the data, but later billing system work answered the spike's question in code: `PremiumExpirationDate` is billing lifecycle metadata and plays no role in access gating on cloud — `user.Premium` is the sole gate. The data inconsistency has no user-facing impact. Safe to close with a note documenting this as intentional design.
