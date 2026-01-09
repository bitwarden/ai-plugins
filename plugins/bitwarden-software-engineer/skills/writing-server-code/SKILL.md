---
name: writing-server-code
description: Bitwarden server code conventions for C# and .NET. Use when working in the server repo, creating commands, queries, services, or API endpoints.
tools: Read, Write, Edit, Bash, Glob, Grep
---

## Repository Structure

The `server` repo contains:

- `src/Api` — REST API endpoints
- `src/Identity` — Authentication/identity service
- `src/Core` — Business logic, commands, queries, services
- `src/Infrastructure` — Data access, repositories

Run with `dotnet run` from service directories. Migrations: `pwsh dev/migrate.ps1`.

## Command Query Separation (CQS)

New features should use the CQS pattern — discrete action classes instead of large entity-focused services [ADR-0008](https://contributing.bitwarden.com/architecture/adr/server-CQRS-pattern).

**Commands** = write operations (e.g., `CreateCipherCommand`). Change state, may return result.

**Queries** = read operations (e.g., `GetOrganizationApiKeyQuery`). Return data, never change state.

Name classes after the action: `RotateOrganizationApiKeyCommand`. Each command/query has single responsibility.

**Existing code:** The codebase includes service-based patterns developed over time. When modifying existing services, follow the patterns already in the file. Don't refactor to CQS unless explicitly asked.

**If asked to refactor to CQS:** Then apply the pattern to the scope requested — but don't expand beyond what was asked.

## Naming Conventions

- Private fields: `_camelCase` with underscore prefix
- Properties: `PascalCase`, spelled out (e.g., `OrganizationConfiguration` not `OrgConfig`)
- Blank line between property groups and methods

## Code Style

- Spaces (not tabs), 4-space indentation
- Always use curly braces for control blocks (even single-line)
- Long conditionals: trailing operators when split across lines
- Constructors with multiple arguments: one argument per line
- `var` for `using` and `foreach` contextual variables

## Dependency Injection

Use `TryAdd*` overloads, not `AddSingleton`/`AddTransient`:

```csharp
// ✅ Correct
services.TryAddSingleton<IMyService, DefaultMyService>();

// ❌ Wrong
services.AddSingleton<IMyService, DefaultMyService>();
```

Consider creating dependency groups for related services.

## GUID Generation

Always use `CoreHelpers.GenerateComb()` for entity IDs — prevents SQL Server index fragmentation:

```csharp
// ✅ Correct
var id = CoreHelpers.GenerateComb();

// ❌ Wrong
var id = Guid.NewGuid();
```

## Controller Actions

- Avoid function overloads — use distinct names (`Get` vs `GetAll`)
- Name after the action (`CreateThing`, `UpdateThing`), not HTTP method (`PostThing`, `PutThing`)
- One route per action — don't expose same function under multiple routes

## Caching

**Don't implement caching unless requested.** If a user describes a performance problem where caching might help, suggest it — but don't implement without confirmation. Caching adds complexity and isn't always the right solution.

When caching is needed, use `IFusionCache` instead of `IDistributedCache` [ADR-0028](https://contributing.bitwarden.com/architecture/adr/adopt-fusion-cache). Register with `AddExtendedCache` and inject via keyed services.

FusionCache provides automatic key prefixing, L1/L2 caching, stampede protection, and backplane sync across nodes.

**Existing code:** Don't migrate existing `IDistributedCache` usage to FusionCache unless explicitly asked.

## Testing

Use xUnit. Run integration tests with `dotnet test` from `test/Infrastructure.IntegrationTest`.
