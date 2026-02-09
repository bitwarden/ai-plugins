---
name: writing-database-queries
description: Bitwarden database architecture, migrations, and dual-ORM strategy. Use when working with .sql files, stored procedures, EF migrations, or database schema changes.
---

## Dual-ORM Architecture

Bitwarden maintains two parallel data access implementations:

- **MSSQL:** Dapper with stored procedures
- **PostgreSQL, MySQL, SQLite:** Entity Framework Core

Every database change requires both implementations. Repository interfaces abstract both — when a stored procedure performs specific operations, the EF implementation must replicate identical behavior.

### Why two ORMs?

MSSQL was the original database. Dapper + stored procedures gave fine-grained control over query performance for the self-hosted product. When cloud-hosted Bitwarden added PostgreSQL/MySQL/SQLite support, EF Core was the pragmatic choice for multi-database targeting — rewriting all stored procedures for each dialect wasn't feasible. The dual approach persists because migrating MSSQL off Dapper would be a massive effort with risk and no clear benefit.

## Evolutionary Database Design (EDD)

Zero-downtime deployments require three-phase migrations:

**Phase 1 — Initial** (`util/Migrator/DbScripts`): Runs before code deployment. Must be fast and backwards-compatible. Adds support for new features without breaking the currently running release.

**Phase 2 — Transition** (`util/Migrator/DbScripts_transition`): Runs after deployment as a background task. Handles slow data migrations that must be batched. NO schema changes — only data movement.

**Phase 3 — Finalization** (`util/Migrator/DbScripts_finalization`): Runs at the next release. Removes backwards-compatibility scaffolding from Phase 1.

### Why three phases?

Bitwarden Cloud deploys without downtime. If a migration adds a NOT NULL column, the currently running code (which doesn't know about that column) would break on INSERT. Phase 1 adds the column as nullable with a default. Phase 2 backfills existing rows. Phase 3 (next release, when all code knows about the column) adds the NOT NULL constraint. This pattern applies to any schema change that could break the previous release.

### When you only need Phase 1

Simple additive changes (new nullable column, new table, new stored procedure) that don't break existing code can skip Phases 2 and 3. Only use multi-phase when the change would break the currently deployed release if applied immediately.

## Key locations

- `src/Sql/dbo` — Master schema source of truth
- `src/Sql/dbo_finalization` — Future schema state
- `util/Migrator/DbScripts_manual` — Exceptional cases (index rebuilds)

## ORM-Specific Implementation

When implementing Dapper repository methods, stored procedures, or MSSQL migration scripts, activate the `implementing-dapper-queries` skill.

When implementing EF Core repositories, generating EF migrations, or working with PostgreSQL/MySQL/SQLite, activate the `implementing-ef-core` skill.

## Critical Rules

These are the most frequently violated conventions. Claude cannot fetch the linked docs at runtime, so these are inlined here:

- **Migration file naming:** `YYYY-MM-DD_##_Description.sql` (e.g., `2025-06-15_00_AddVaultColumn.sql`)
- **All schema objects use `dbo` schema** — never create objects in other schemas
- **Constraint naming:** `PK_TableName` (primary key), `FK_Child_Parent` (foreign key), `IX_Table_Column` (index), `DF_Table_Column` (default)
- **Idempotent scripts:** Use `IF NOT EXISTS` / `IF COL_LENGTH(...)` guards before schema changes in migration scripts
- **Every database change requires both Dapper and EF Core implementations** — never ship one without the other
- **Integration tests use `[DatabaseData]` attribute** — this runs the test against all configured database providers

## Further Reading

- [SQL code style](https://contributing.bitwarden.com/contributing/code-style/sql/)
- [Database migrations (MSSQL)](https://contributing.bitwarden.com/contributing/database-migrations/mssql)
- [Database migrations (EF)](https://contributing.bitwarden.com/contributing/database-migrations/ef)
- [Evolutionary Database Design](https://contributing.bitwarden.com/contributing/database-migrations/edd)
