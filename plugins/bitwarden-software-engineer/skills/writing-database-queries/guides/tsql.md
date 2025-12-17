# T-SQL Guide

## Stored Procedure Naming

Use `{Entity}_{Action}[_Descriptor]` pattern:

| Operation        | Pattern                       | Example                        |
| ---------------- | ----------------------------- | ------------------------------ |
| Create           | `Entity_Create`               | `User_Create`                  |
| Read single      | `Entity_ReadById`             | `Organization_ReadById`        |
| Read by criteria | `Entity_ReadBy{Criteria}`     | `User_ReadByEmail`             |
| Read many        | `Entity_ReadManyBy{Criteria}` | `Cipher_ReadManyByUserId`      |
| Update           | `Entity_Update`               | `User_Update`                  |
| Delete           | `Entity_DeleteById`           | `Cipher_Delete`                |
| Soft delete      | `Entity_SoftDelete`           | `Cipher_SoftDelete`            |
| Special          | `Entity_{ActionDescription}`  | `User_BumpAccountRevisionDate` |

## Procedure Structure

```sql
CREATE OR ALTER PROCEDURE [dbo].[Entity_Action]
    @Id UNIQUEIDENTIFIER,
    @OptionalParam NVARCHAR(50) = NULL  -- Nullable default for backwards compatibility
AS
BEGIN
    SET NOCOUNT ON
    -- Logic here
END
GO
```

## Code Style

- Keywords: `UPPERCASE`
- Objects: Square brackets — `[dbo].[TableName]`, `[ColumnName]`
- Tables/Columns: PascalCase
- Parameters: `@PascalCase`
- Constraints: `PK_{Table}`, `FK_{Table}_{RefTable}`, `DF_{Table}_{Column}`, `IX_{Table}_{Columns}`

Standard columns:

```sql
[Id]            UNIQUEIDENTIFIER NOT NULL
[CreationDate]  DATETIME2(7)     NOT NULL
[RevisionDate]  DATETIME2(7)     NOT NULL
```

## Anti-Patterns to Avoid

### Index creation on large tables

Creating indexes on `dbo.Cipher`, `dbo.OrganizationUser`, or other large tables can cause outages. Never specify `ONLINE = ON` in scripts — production handles this automatically, and the option fails on unsupported SQL Server editions.

### NOT NULL columns done wrong

```sql
-- BAD: Full table scan
ALTER TABLE [dbo].[Table] ADD [Column] INT NULL
UPDATE [dbo].[Table] SET [Column] = 0
ALTER TABLE [dbo].[Table] ALTER COLUMN [Column] INT NOT NULL

-- GOOD: Metadata-only operation
ALTER TABLE [dbo].[Table]
    ADD [Column] INT NOT NULL CONSTRAINT DF_Table_Column DEFAULT 0
```

### Defaults on string types

Use defaults only for numeric types (`BIT`, `TINYINT`, `INT`, `BIGINT`). Never use defaults for `VARCHAR`, `NVARCHAR`, or MAX types.

### Missing view metadata refresh

After modifying tables, refresh views:

```sql
EXECUTE sp_refreshview N'[dbo].[ViewName]'
GO
```

After altering views, refresh dependent procedures:

```sql
IF OBJECT_ID('[dbo].[ProcName]') IS NOT NULL
    EXECUTE sp_refreshsqlmodule N'[dbo].[ProcName]'
GO
```

## Backwards Compatibility

New parameters must have nullable defaults:

```sql
@NewParameter DATATYPE = NULL
```

When renaming columns during EDD transition:

```sql
SET @FirstName = COALESCE(@FirstName, @FName);
```
