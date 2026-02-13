---
name: bitwarden-ios-review-knowledge
description: Institutional knowledge for bitwarden/ios code reviews. Use BEFORE reviewing ios PRs to understand repository-specific patterns, architectural constraints, and avoid false positives.
---

# bitwarden/ios - Code Review Knowledge

## Repository Overview

| Item | Details |
|------|---------|
| **Repository** | [bitwarden/ios](https://github.com/bitwarden/ios) |
| **Technology Stack** | iOS, Swift, Swift Package Manager, Xcodegen, Python (automation), XCTest |
| **Primary Languages** | Swift, Python, Bash |

## Verified Detection Strategies

_Copy-paste ready commands for catching common issues._

### Dependency Management Source of Truth Check
```bash
# Verify dependency updates target xcodegen project files, not Package.resolved
git diff --name-only | grep -E "project-(bwk|bwa|pm)\.yml" || \
  echo "⚠️  Dependency update should modify xcodegen project files"

# Check if Package.resolved is being tracked (should not be)
git ls-files | grep "Package.resolved" && \
  echo "❌ Package.resolved should be untracked (in .gitignore)"
```

### GitHub API Pattern Check (gh vs curl)
```bash
# Find raw curl calls to GitHub API (should use gh CLI instead)
grep -r "curl.*api\.github\.com" .github/workflows Scripts/ && \
  echo "⚠️  Consider using 'gh' CLI instead of curl for GitHub API calls"

# Verify gh CLI usage pattern
grep -r "GH_TOKEN" .github/workflows/ | head -5
```

### Swift Test Setup Ordering Validation
```bash
# Detect potential test setup ordering violations in async tests
# Find await perform/receive followed by mock assignments within 5 lines
grep -A 5 "await subject\.\(perform\|receive\)" **/*Tests.swift | \
  grep -E "(repository|mock)\.\w+\s*=" && \
  echo "❌ CRITICAL: Mock setup after test action execution detected"
```

### iOS Version Guard Logic Verification
```bash
# Find contradictory iOS version guard patterns
# Pattern 1: #available with "earlier" in skip message (contradiction)
grep -B 2 "#available(iOS" **/*Tests.swift | \
  grep -A 1 "XCTSkip.*earlier" && \
  echo "❌ Logic error: #available guard with 'earlier' skip message"

# Pattern 2: #unavailable with "later" in skip message (contradiction)
grep -B 2 "#unavailable(iOS" **/*Tests.swift | \
  grep -A 1 "XCTSkip.*later" && \
  echo "❌ Logic error: #unavailable guard with 'later' skip message"
```

### Swift Extension Documentation Pattern
```bash
# Check for protocol conformance extensions (typically don't need DocC)
grep -n "extension.*:.*{" **/*.swift | \
  grep -v "Tests.swift" | \
  head -10
# Note: Protocol conformance extensions don't require DocC if protocol is documented
```

### Old Type References in Documentation After Migration
```bash
# Find stale type references in docs after refactoring
# Usage: Replace OLD_TYPE with the renamed/removed type name
OLD_TYPE="KeychainItem"
grep -r "//" **/*.swift | grep "$OLD_TYPE" && \
  echo "⚠️  Found old type name '$OLD_TYPE' in documentation"
```

## Failed Attempts (Critical Learnings)

| Issue | Why Missed | Detection Strategy | Review Date | PR Link | Severity |
|-------|------------|-------------------|-------------|---------|----------|
| iOS version guard logic contradiction: `#available(iOS 26, *)` guard with skip message "requires iOS 18.6 or earlier" | Issue mentioned in summary comment only, not placed inline on specific line; developer fixed inline comments but missed summary-only findings | Always place inline comments for CRITICAL findings. Search pattern: `grep -B2 "#available(iOS" \| grep -A1 "earlier"` to find contradictions. Verify guard direction matches skip message intent. | 2025-11-28 | [#2168](https://github.com/bitwarden/ios/pull/2168) | ❌ CRITICAL |
| Test setup ordering violation: Mock repositories configured AFTER `await subject.perform()` call, causing tests to run with uninitialized data | Developer copied structure from existing tests without verifying async timing; no lint rule enforces Arrange-Act-Assert ordering in async Swift tests | Search for `await subject\.(perform\|receive)` followed by repository assignments in next 5 lines. Flag any pattern: `await subject.perform(...)` then `repository.property = ...` | 2025-11-28 | [#2168](https://github.com/bitwarden/ios/pull/2168) | ❌ CRITICAL |
| Documentation incorrectly stated mocks go in `Mocks` folders universally, but only applies to `BitwardenKit` and `AuthenticatorBridgeKit`; other targets use `TestHelpers` | Claude bot focused on wording consistency without verifying against actual project structure; didn't cross-reference documentation claims with codebase | When reviewing documentation about conventions, cross-reference against actual structure. For iOS: Check `project.yml` for target configs. Search: `find . -name "*Mock*.swift"` and verify folder patterns by target. | 2025-11-12 | [#2130](https://github.com/bitwarden/ios/pull/2130) | ⚠️ IMPORTANT |
| Outdated documentation in `KeychainServiceError.swift` referenced old type `KeychainItem` instead of new `KeychainStorageKeyPossessing` protocol after migration | Claude focused on structural patterns (DocC presence) but didn't verify documentation text accuracy against renamed types during refactoring | When reviewing migrations/refactorings: `grep -r "OldTypeName" **/*.swift \| grep "//"` to find stale references. Verify terminology matches new abstraction level. | 2025-12-17 | [#2202](https://github.com/bitwarden/ios/pull/2202) | ⚠️ IMPORTANT |
| Claude flagged missing DocC on protocol conformance extension, but iOS team convention is that such extensions don't need docs when protocol is documented | Applied general documentation guidelines without checking iOS-specific conventions; didn't recognize idiomatic Swift pattern | Before flagging missing docs on extension, check if it declares protocol conformance (`: ProtocolName`). Verify protocol itself has DocC. Check `.claude/CLAUDE.md` for conventions. | 2025-12-17 | [#2202](https://github.com/bitwarden/ios/pull/2202) | 🎨 FALSE_POSITIVE |

**For detailed error scenarios, code examples, and step-by-step solutions, see [troubleshooting.md](./references/troubleshooting.md).**

## Repository Gotchas

_Architectural patterns and conventions. See [troubleshooting.md](./references/troubleshooting.md#repository-specific-patterns) for detection commands._

### SPM Dependency Management: Xcodegen is Source of Truth
`Package.resolved` is gitignored. Xcodegen project files (`project-*.yml`) are the canonical source for dependency versions used in caching. **PR** [#1753](https://github.com/bitwarden/ios/pull/1753)

### GitHub API: Prefer gh CLI
Use `gh` CLI instead of curl for GitHub API calls in CI/CD workflows. Better auth, errors, and maintainability. **PR** [#1753](https://github.com/bitwarden/ios/pull/1753)

### Automation Scripts: Python Over Bash
Python with classes preferred for scripts >100 lines. Team uses `uv` for environment management. Bash only for simple tasks. **PR** [#1753](https://github.com/bitwarden/ios/pull/1753)

### Dependency Pinning: Revision + Context
Pin to `revision:` hashes for reproducibility. Add comments with tag names for human readability or use `exactVersion:` field. **PR** [#1753](https://github.com/bitwarden/ios/pull/1753)

### Mock Placement: Target-Specific
`BitwardenKit`/`AuthenticatorBridgeKit` use `Mocks/` folders. `BitwardenShared`/`AuthenticatorShared` use `TestHelpers/`. Sourcery `AutoMockable` preferred. **PR** [#2130](https://github.com/bitwarden/ios/pull/2130)

### iOS Version Guard: Test Pairing
Tests require BOTH `#available(iOS 26, *)` (new behavior) and `#unavailable(iOS 26)` (legacy) versions. Guard direction must match skip message. **PR** [#2168](https://github.com/bitwarden/ios/pull/2168)

### Arrange-Act-Assert in Async Tests
**CRITICAL**: ALL mocks must be configured BEFORE `await subject.perform()`. No exceptions. Tests with setup after action appear to pass but don't actually test anything. **PR** [#2168](https://github.com/bitwarden/ios/pull/2168)

### iOS 26 Profile Switcher
iOS 26+ tests MUST verify `.dismiss` route (sheet-based). Pre-iOS 26 tests do NOT check dismiss (modal-based). **PR** [#2168](https://github.com/bitwarden/ios/pull/2168)

### Extension Documentation
Protocol conformance extensions don't need DocC if protocol itself is documented. MARK comments acceptable. **PR** [#2202](https://github.com/bitwarden/ios/pull/2202)

### Fido2 Performance
Sync conditionally, not automatically. Only sync when `counter > 0`. Use `isPeriodic: true` flag. Local checks (`onlyCheckLocalData: true`) before expensive ops. **PR** [#2201](https://github.com/bitwarden/ios/pull/2201)

### Recursive Functions
Use boolean flag parameter to prevent infinite loops when async operations can trigger re-entry. Document loop prevention explicitly. **PR** [#2201](https://github.com/bitwarden/ios/pull/2201)

## Methodology Improvements

### Proactive Architectural Guidance
Front-load comprehensive guidance in first review for automation/CI/CD PRs. Consolidate conventions, offer implementation help, link examples. Reduces review cycles. **PR** [#1753](https://github.com/bitwarden/ios/pull/1753)

### Severity Escalation for Repeated Issues
When same issue appears in 2+ files, escalate severity in subsequent reviews to emphasize importance. **PR** [#2168](https://github.com/bitwarden/ios/pull/2168)

### Inline > Summary Comments
CRITICAL/IMPORTANT findings MUST have inline comments on specific lines. Summary-only mentions get missed. **PR** [#2168](https://github.com/bitwarden/ios/pull/2168)

### Non-Blocking Observations After Approval
Can suggest improvements after approval if clearly marked non-blocking. Improves consistency without blocking progress. **PR** [#2168](https://github.com/bitwarden/ios/pull/2168)

### Paired Test Verification
iOS version-gated features require test pairs: `test_feature()` (pre-iOS 26) + `test_feature_iOS26()` (iOS 26+). Verify both exist. **PR** [#2168](https://github.com/bitwarden/ios/pull/2168)

### Conditional Logic Coverage
For conditional optimizations: verify tests for ALL condition combinations, error paths, side effects (call counts), and no-op cases. **PR** [#2201](https://github.com/bitwarden/ios/pull/2201)

### Recursive Parameter Documentation
Boolean flags like `shouldCheckSync` in recursive async functions MUST be documented with explicit mention of "infinite loop" or "re-entry". **PR** [#2201](https://github.com/bitwarden/ios/pull/2201)

### Human Review for Semantic Accuracy
Automated reviews catch structure, humans catch semantic issues. In refactorings, verify documentation text matches new terminology (e.g., old type names). **PR** [#2202](https://github.com/bitwarden/ios/pull/2202)

## Statistics

**Review Coverage**:
- Total PRs analyzed: 5
- Date range: 2025-07-16 to 2025-12-19
- Critical issues found: 2
- Important issues found: 2
- False positives identified: 1
- Repository gotchas extracted: 11
- Methodology insights: 9

**Technology Focus**:
- Primary: Swift, XCTest, iOS SDK
- Secondary: Python (automation), Bash (scripts)
- Build tools: Xcodegen, Swift Package Manager
- Testing: XCTest, async/await patterns
