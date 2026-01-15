# Review Troubleshooting: bitwarden/server

## Error → Solution Mappings

### Missing Return Statement After Async Validation

**Symptom**: Validation method called with `await Validate...Async()` but result not checked or returned, allowing execution to continue even on validation failure.

**Cause**: Validation methods return boolean but caller doesn't check return value or return early on false.

**Solution**: Always check validation return values and return early on failure:
```csharp
var isValid = await ValidateClientVersionAsync(context, validatorContext);
if (!isValid)
{
    return;
}
```

**Detection Command**:
```bash
# Find validation calls that might not be checked
rg "await Validate.*Async\(" --type cs -A 2 | grep -v "var.*=" | grep -v "if.*(" | grep -v "return"
```

**References**: PR #6588 - Fixed in commit [91af02b](https://github.com/bitwarden/server/pull/6588/commits/91af02b9d28381430b1d617b94498a9e7d8d3ff1)
