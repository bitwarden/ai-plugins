# Review Troubleshooting: bitwarden/ios

## Error → Solution Mappings

### iOS Version Guard Logic Contradiction

**Symptom**: Test uses `#available(iOS 26, *)` guard but skip message says "requires iOS 18.6 or earlier"

**Cause**: Issue mentioned in summary comment only, not placed inline on specific line

**Solution**: Always place inline comments for CRITICAL findings. Verify guard direction matches skip message:
- `#available(iOS X, *)` → "requires iOS X or later"
- `#unavailable(iOS X)` → "requires earlier than iOS X"

**Detection Command**:
```bash
# Find contradictory patterns
grep -B 2 "#available(iOS" **/*Tests.swift | grep -A 1 "XCTSkip.*earlier"
grep -B 2 "#unavailable(iOS" **/*Tests.swift | grep -A 1 "XCTSkip.*later"
```

**References**: PR [#2168](https://github.com/bitwarden/ios/pull/2168)

---

### Test Setup Ordering Violation in Async Swift Tests

**Symptom**: Mock repositories configured AFTER `await subject.perform()` call, causing tests to run with uninitialized data

**Cause**: Developer copied structure from existing tests without verifying async timing

**Solution**: Enforce strict Arrange-Act-Assert ordering. ALL mock setup must occur BEFORE test action execution.

**Detection Command**:
```bash
# Detect setup after action
grep -A 5 "await subject\.\(perform\|receive\)" **/*Tests.swift | \
  grep -E "(repository|mock)\.\w+\s*=" && \
  echo "❌ CRITICAL: Mock setup after test action detected"
```

**References**: PR [#2168](https://github.com/bitwarden/ios/pull/2168)

---

### Documentation Inaccuracy - Mock Placement Conventions

**Symptom**: Documentation stated mocks go in `Mocks` folders universally, but only applies to BitwardenKit and AuthenticatorBridgeKit

**Cause**: Claude focused on wording consistency without verifying against actual project structure

**Solution**: When reviewing documentation about conventions, cross-reference against actual codebase structure.

**Detection Command**:
```bash
# Verify mock locations by target
find BitwardenKit -name "*Mock*"
find BitwardenShared -name "*Mock*"
find . -name "*Mock*.swift" | xargs dirname | sort | uniq -c
```

**References**: PR [#2130](https://github.com/bitwarden/ios/pull/2130)

---

### Outdated Type References in Documentation After Refactoring

**Symptom**: Documentation referenced old type `KeychainItem` instead of new `KeychainStorageKeyPossessing` protocol after migration

**Cause**: Claude focused on structural patterns but didn't verify documentation text accuracy against renamed types

**Solution**: When reviewing migrations/refactorings, grep for old type names in documentation comments.

**Detection Command**:
```bash
# Find stale type references (replace OLD_TYPE with actual old name)
OLD_TYPE="KeychainItem"
grep -r "//" **/*.swift | grep "$OLD_TYPE"
```

**References**: PR [#2202](https://github.com/bitwarden/ios/pull/2202)

---

### False Positive: Missing DocC on Protocol Conformance Extension

**Symptom**: Claude flagged missing DocC on protocol conformance extension

**Cause**: Applied general documentation guidelines without checking iOS-specific conventions

**Solution**: Before flagging missing docs on extension, check if it declares protocol conformance. Extensions that only provide conformance don't need DocC if protocol is documented.

**Detection Command**:
```bash
# Find protocol conformance extensions
grep -n "extension.*:.*{" **/*.swift | grep -v "Tests.swift"
```

**References**: PR [#2202](https://github.com/bitwarden/ios/pull/2202)

---

## Repository-Specific Patterns

### SPM Dependency Management Pattern

**Key Principle**: `Package.resolved` is gitignored. Xcodegen project files (`project-*.yml`) are source of truth.

**Detection**:
```bash
# Verify dependency updates target correct files
git diff --name-only | grep -E "project-(bwk|bwa|pm)\.yml"
git ls-files | grep "Package.resolved" && echo "❌ Should be gitignored"
```

### GitHub API Pattern

**Preference**: Use `gh` CLI instead of curl for GitHub API calls

**Detection**:
```bash
grep -r "curl.*api\.github\.com" .github/workflows Scripts/
```

### Automation Scripts

**Preference**: Python with classes for scripts >100 lines, bash for simple tasks

### iOS Version Guard Test Pairing

**Pattern**: iOS 26 features require paired tests:
- `test_feature()` - pre-iOS 26 behavior with `#unavailable(iOS 26)`
- `test_feature_iOS26()` - iOS 26+ behavior with `#available(iOS 26, *)`

### Async Test Pattern

**Critical**: ALL mocks configured BEFORE `await subject.perform()`. No exceptions.

### iOS 26 Profile Switcher

**Pattern**: iOS 26+ tests MUST verify `.dismiss` route (sheet-based UI). Pre-iOS 26 tests do NOT check dismiss (modal-based).
