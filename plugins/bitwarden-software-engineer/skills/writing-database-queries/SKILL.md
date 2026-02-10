---
name: writing-database-queries
description: Bitwarden database architecture, migrations, and dual-ORM strategy. Use when working with .sql files, stored procedures, EF migrations, or database schema changes.
---

## Dual-ORM Architecture

Bitwarden maintains two parallel data access implementations:

- **MSSQL:** Dapper with stored procedures
- **PostgreSQL, MySQL, SQLite:** Entity Framework Core

Every database change requires both implementations. Repository interfaces abstract both — when a stored procedure performs specific operations, the EF implementation must replicate identical behavior.

## Evolutionary Database Design (EDD)

Bitwarden Cloud uses zero-downtime deployments with a multi-phase migration strategy:

- **Phase 1 — Initial** (`util/Migrator/DbScripts`): Runs before code deployment. Must be backwards-compatible.
- **Phase 2 — Transition** (`util/Migrator/DbScripts_transition`): Runs after deployment. Handles batched data migrations only — no schema changes.
- **Phase 3 — Finalization** (`util/Migrator/DbScripts_finalization`): Runs at the next release. Removes backwards-compatibility scaffolding.

Simple additive changes (new nullable column, new table, new stored procedure) only need Phase 1.

**Always defer to the developer on migration phasing.** The multi-phase approach is complex and context-dependent. When a database change is needed, write the migration script for Phase 1 and ask the developer whether additional phases are required.

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
