---
name: writing-server-code
description: Bitwarden server code conventions for C# and .NET. Use when working in the server repo, creating commands, queries, services, or API endpoints.
---

## Repository Orientation

The `server` repo contains:

- `src/Api` — REST API endpoints
- `src/Identity` — Authentication/identity service
- `src/Core` — Business logic, commands, queries, services
- `src/Infrastructure` — Data access, repositories

## Architectural Rationale

### Command Query Separation (CQS)

New features should use the CQS pattern — discrete action classes instead of large entity-focused services. See [ADR-0008](https://contributing.bitwarden.com/architecture/adr/server-CQRS-pattern).

**Why CQS matters at Bitwarden:** The codebase historically grew around entity-focused services (e.g., `CipherService`) that accumulated hundreds of methods. CQS breaks these into single-responsibility classes (`CreateCipherCommand`, `GetOrganizationApiKeyQuery`), making code easier to test, reason about, and modify without unintended side effects.

**Commands** = write operations. Change state, may return result. Named after the action: `RotateOrganizationApiKeyCommand`.

**Queries** = read operations. Return data, never change state.

**When NOT to use CQS:** When modifying existing service-based code, follow the patterns already in the file. Don't refactor to CQS unless explicitly asked. If asked to refactor, apply the pattern only to the scope requested.

### FusionCache over IDistributedCache

When caching is needed, use `IFusionCache` instead of `IDistributedCache`. See [ADR-0028](https://contributing.bitwarden.com/architecture/adr/adopt-fusion-cache).

**Why FusionCache:** It provides L1/L2 caching, stampede protection, and backplane sync across nodes — solving problems that `IDistributedCache` leaves to the developer. Register with `AddExtendedCache` and inject via keyed services.

**Don't implement caching unless requested.** If a user describes a performance problem where caching might help, suggest it — but don't implement without confirmation. Caching adds complexity and isn't always the right solution. Don't migrate existing `IDistributedCache` usage unless explicitly asked.

### GUID Generation

Always use `CoreHelpers.GenerateComb()` for entity IDs — never `Guid.NewGuid()`. Sequential COMBs prevent SQL Server index fragmentation that random GUIDs cause on clustered indexes, which is critical for Bitwarden's database performance at scale.

## Critical Rules

These are the most frequently violated conventions. Claude cannot fetch the linked docs at runtime, so these are inlined here:

- **Use `TryAdd*` for DI registration** (`TryAddScoped`, `TryAddTransient`) — prevents duplicate registrations when multiple modules register the same service
- **File-scoped namespaces** — `namespace Bit.Core.Vault;` not `namespace Bit.Core.Vault { ... }`
- **Nullable reference types are enabled** (ADR-0024) — use `!` (null-forgiving) when you know a value isn't null; use `required` modifier for properties that must be set during construction
- **`Async` suffix on all async methods** — `CreateAsync`, not `Create`, when the method returns `Task`
- **Controller actions return `ActionResult<T>`** — not `IActionResult` or bare `T`
- **Testing with xUnit** — use `[Theory, BitAutoData]` (not `[AutoData]`), `SutProvider<T>` for automatic SUT wiring, and `Substitute.For<T>()` from NSubstitute for mocking

## Examples

### GUID generation

```csharp
// CORRECT — sequential COMB prevents index fragmentation
var id = CoreHelpers.GenerateComb();

// WRONG — random GUIDs fragment clustered indexes
var id = Guid.NewGuid();
```

### DI registration

```csharp
// CORRECT — idempotent, won't duplicate
services.TryAddScoped<ICipherService, CipherService>();

// WRONG — silently duplicates registration, last-wins causes subtle bugs
services.AddScoped<ICipherService, CipherService>();
```

### Namespace style

```csharp
// CORRECT — file-scoped
namespace Bit.Core.Vault.Commands;

// WRONG — block-scoped
namespace Bit.Core.Vault.Commands
{
    // ...
}
```

## Further Reading

- [C# code style](https://contributing.bitwarden.com/contributing/code-style/csharp/)
- [Server architecture](https://contributing.bitwarden.com/architecture/server/)
