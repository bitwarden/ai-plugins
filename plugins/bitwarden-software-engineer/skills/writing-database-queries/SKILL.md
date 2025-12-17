---
name: writing-database-queries
description: Bitwarden database queries, stored procedures, and migrations. Use when working with .sql files, stored procedures, EF migrations, or database schema changes.
tools: Read, Write, Edit, Bash, Glob, Grep
---

## Repository Architecture

MSSQL uses Dapper with stored procedures. All other databases (PostgreSQL, MySQL, SQLite) use Entity Framework Core. Every database change requires both implementations.

- Dapper: `Repository Method → Stored Procedure → View (for reads)`
- EF: `Repository Method → DbContext → Generated SQL`

Repository interfaces abstract both. When a stored procedure performs specific operations, the EF implementation must replicate identical behavior.

## Migration Workflow (Evolutionary Database Design)

Zero-downtime deployments require three-phase migrations:

**Phase 1 — Initial** (`util/Migrator/DbScripts`): Runs before code deployment. Must be fast, backwards-compatible. Adds support for new features without breaking current release.

**Phase 2 — Transition** (`util/Migrator/DbScripts_transition`): Runs after deployment as background task. Handles slow data migrations. Must be batched. NO schema changes.

**Phase 3 — Finalization** (`util/Migrator/DbScripts_finalization`): Runs at next release. Removes backwards-compatibility scaffolding.

Other locations:
- `src/Sql/dbo` — Master schema source of truth
- `src/Sql/dbo_finalization` — Future schema state
- `util/Migrator/DbScripts_manual` — Exceptional cases (index rebuilds)

## Migration Naming

MSSQL: `YYYY-MM-DD_##_MigrationName.sql` (e.g., `2024-01-15_00_AddUserColumn.sql`)

Finalization: `YYYY-0M-FinalizationMigration.sql`

EF migration class names must exactly match the MSSQL migration name portion.

Generate EF migrations: `pwsh ef_migrate.ps1 <MigrationName>`

Apply migrations: `pwsh migrate.ps1 -all` (all databases) or `pwsh migrate.ps1` (MSSQL only)

## All Migrations Must Be Idempotent

```sql
-- Tables
IF OBJECT_ID('[dbo].[TableName]') IS NULL
BEGIN
    CREATE TABLE [dbo].[TableName] (...)
END
GO

-- Columns
IF COL_LENGTH('[dbo].[TableName]', 'ColumnName') IS NULL
BEGIN
    ALTER TABLE [dbo].[TableName]
        ADD [ColumnName] INT NOT NULL CONSTRAINT DF_Table_Column DEFAULT 0
END
GO

-- Procedures: always use CREATE OR ALTER
CREATE OR ALTER PROCEDURE [dbo].[Entity_Action]
```

## Testing

Use `[DatabaseData]` attribute to run tests against all configured databases:

```csharp
[Theory, DatabaseData]
public async Task TestMethod(IOrganizationRepository repo)
{
    // Runs for MSSQL/Dapper, Postgres/EF, MySQL/EF, SQLite/EF
}
```

For migration testing, use `MigrationName` parameter matching both SQL file suffix and EF class name.

Use separate test databases (`vault_test`) from development (`vault_dev`).

## Database-Specific Guidance

For T-SQL patterns (MSSQL, stored procedures, Dapper), see [guides/tsql.md](guides/tsql.md).

For Entity Framework patterns (PostgreSQL, MySQL, SQLite, EF migrations), see [guides/entity-framework.md](guides/entity-framework.md).
