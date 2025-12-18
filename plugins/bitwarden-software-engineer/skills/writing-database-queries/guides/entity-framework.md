# Entity Framework Guide

EF is used for PostgreSQL, MySQL, MariaDB, and SQLite. MSSQL uses Dapper in production.

## Generating Migrations

```powershell
pwsh ef_migrate.ps1 <MigrationName>
```

Creates migrations for all EF targets simultaneously.

## Key Differences from MSSQL

- Queries working against MySQL may fail against Postgres (e.g., Postgres doesn't support `Min` on boolean values)
- Always run integration tests with `[DatabaseData]` rather than manually testing each database
- EF implementation must replicate exact behavior of corresponding stored procedures

## Testing

```csharp
[Theory, DatabaseData]
public async Task TestMethod(IOrganizationRepository repo)
{
    // Automatically runs against all configured EF databases
}
```
