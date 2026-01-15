---
name: bitwarden-android-review-knowledge
description: Institutional knowledge for bitwarden/android code reviews. Use BEFORE reviewing android PRs to understand repository-specific patterns, architectural constraints, and avoid false positives.
---

# bitwarden/android - Code Review Knowledge

## Experiment Overview

| Item | Details |
|------|---------|
| **Repository** | [bitwarden/android](https://github.com/bitwarden/android) |
| **Technology Stack** | Android, Kotlin, Jetpack Compose, MVVM+UDF, Hilt DI |
| **Primary Languages** | Kotlin, Gradle |
| **Common Issue Categories** | Security patterns, Architecture compliance, Event tracking, Documentation accuracy, Test patterns |

## Verified Detection Strategies

_Copy-paste ready commands for catching common issues._

### Organization Event Type Validation
```bash
# Verify event types have corresponding sealed class implementations
grep -r "@SerialName" network/src/main/kotlin/com/bitwarden/network/model/OrganizationEventType.kt | \
  awk -F'"' '{print $2}' | while read num; do
    grep -q "ORGANIZATION.*$num" app/src/main/kotlin/com/x8bit/bitwarden/data/platform/manager/model/OrganizationEvent.kt || \
      echo "Missing implementation for event type $num"
  done
```

### Package Name Logging Check (Credential Manager)
```bash
# Find potentially sensitive package name logging in credential flows
grep -r "callingAppInfo.packageName" \
  app/src/main/kotlin/com/x8bit/bitwarden/data/credentials/ | \
  grep -E "(Timber|Log)" && \
  echo "⚠️  Package name logging detected in Credential Manager context"
```

### ProGuard Rule Duplication
```bash
# Check for duplicated ProGuard rules across modules
diff -u app/proguard-rules.pro authenticator/proguard-rules.pro | \
  grep -A5 "zxing\|retrofit\|okhttp"
```

### Feature Flag File Consistency
```bash
# Verify feature flags are defined in all 4 required locations
FLAG_NAME="YourFlagDataObjectName"
FILES=(
  "core/src/main/kotlin/com/bitwarden/core/data/manager/model/FlagKey.kt"
  "core/src/test/kotlin/com/bitwarden/core/data/manager/model/FlagKeyTest.kt"
  "ui/src/main/kotlin/com/bitwarden/ui/platform/components/debug/FeatureFlagListItems.kt"
  "ui/src/main/res/values/strings_non_localized.xml"
)
for file in "${FILES[@]}"; do
  grep -q "$FLAG_NAME" "$file" || echo "Missing in: $file"
done
```

### Event Tracking Before Navigation
```bash
# Find navigation calls that might occur before event tracking
grep -B5 "sendEvent.*Navigate" \
  app/src/main/kotlin/com/x8bit/bitwarden/ui/**/*/ViewModel.kt | \
  grep -v "organizationEventManager.trackEvent" && \
  echo "⚠️  Navigation without prior event tracking detected"
```

### Complete View State Assertion Validation
```bash
# Detect individual property assertions (anti-pattern in bitwarden/android)
rg "assertEquals\([^,]+\.[^,]+," app/src/test --type kotlin
```

### Markdown Documentation Line Number References
```bash
# Find hardcoded line number references that create maintenance burden
rg '\w+\.md:\d+(-\d+)?' --glob '*.md'
```

### Markdown Code Formatting Check
```bash
# Find file paths and code terms missing backtick formatting
rg '(?<!`)@\w+(?!`)' --glob '*.md'  # Annotations without backticks
rg '(?<!`)[\w/]+\.md(?!`)' --glob '*.md'  # Paths without backticks
```

### JSON Test Data Syntax Validation
```bash
# Find multiline JSON in test files (manual validation needed)
rg '"""[\s\S]*?"[^,\s]*\s*"' --type kotlin --glob '*Test.kt'
```

### State Persistence for Conditional Navigation
```bash
# Find StateFlow<Boolean> fields controlling navigation without persistence checks
rg 'StateFlow<Boolean>' app/src/main/kotlin --type kotlin -A10 | \
  rg -v 'storeMigration|hasMigrationBeenAttempted' && \
  echo "⚠️  StateFlow navigation without persistence tracking detected"
```

## Failed Attempts (Critical Learnings)

| Issue | Why Missed | Detection Strategy | Review Date | PR Link | Severity |
|-------|------------|-------------------|-------------|---------|----------|
| Hardcoded line number references in documentation | Focused on content correctness rather than maintainability of line references | Search for pattern `\w+\.md:\d+(-\d+)?` in documentation files; flag as maintenance risk | 2025-10-27 | [#6072](https://github.com/bitwarden/android/pull/6072) | ⚠️ IMPORTANT |
| Missing code formatting for technical terms in markdown | Initial focus on content structure rather than markdown formatting conventions | Verify file paths and code terms use backticks; search for unformatted patterns like `docs/\w+` or `@\w+` | 2025-10-27 | [#6072](https://github.com/bitwarden/android/pull/6072) | ⚠️ IMPORTANT |
| CODEOWNERS coverage for functionally-coupled workflow files | Focused on primary directory ownership without considering related workflows in different directories | When reviewing CODEOWNERS changes, grep workflow files for references to feature directory; check for ownership transitivity | 2025-10-27 | [#6072](https://github.com/bitwarden/android/pull/6072) | ⚠️ IMPORTANT |
| Weak test assertion pattern (property-by-property instead of complete state) | Claude's default test generation uses individual property assertions rather than complete state equality | Search for `assertEquals(expected.property, actual.property)` pattern; require complete state assertions: `assertEquals(expectedState, actualState)` | 2025-12-16 | [#6275](https://github.com/bitwarden/android/pull/6275) | ⚠️ IMPORTANT |
| JSON syntax error in test data (missing comma) | JSON syntax errors in triple-quoted raw strings don't get IDE validation | Always validate JSON test data syntax; paste into JSON validator; check CI test results for parsing failures | 2025-12-17 | [#6281](https://github.com/bitwarden/android/pull/6281) | ❌ CRITICAL |
| Documentation placeholder vs implementation mismatch flagged incorrectly | Did not recognize that documentation examples commonly use placeholder values for pedagogical clarity | Check if values are marked as placeholders (9999, example, REPLACE_ME); distinguish configuration files from documentation examples | 2025-12-19 | [#6282](https://github.com/bitwarden/android/pull/6282) | 🎨 SUGGESTED |
| Network serialization tests missing for OrganizationEventType 1618/1619 | Generic serializer handles all enums; tests seemed redundant | Search for new enum values in OrganizationEventType.kt, verify corresponding test exists in EventServiceTest.kt | 2025-12-16 | [#6273](https://github.com/bitwarden/android/pull/6273) | ⚠️ IMPORTANT |
| String resource file location inconsistency not documented in feature flags skill | Assumed single canonical location for string resources | Check both strings.xml and strings_non_localized.xml when documenting patterns; note historical inconsistencies | 2025-12-05 | [#6238](https://github.com/bitwarden/android/pull/6238) | ⚠️ IMPORTANT |
| Naming convention automation limitations in feature flags | Assumed mechanical kebab-case to snake_case transformation | Document that string resource keys use semantic variations and abbreviations; always confirm generated names with user | 2025-12-05 | [#6238](https://github.com/bitwarden/android/pull/6238) | ⚠️ IMPORTANT |
| ProGuard rule duplication across app modules | Focused on dependency change, didn't check build configuration files | When reviewing dependency updates, grep for library name in all proguard-rules.pro files across modules | 2025-12-04 | [#6230](https://github.com/bitwarden/android/pull/6230) | 🎨 SUGGESTED |
| Handler pattern introduced but not documented | New architectural pattern not explicitly flagged for documentation | When novel patterns appear (first usage in codebase), recommend adding to docs/ARCHITECTURE.md | 2025-12-05 | [#6239](https://github.com/bitwarden/android/pull/6239) | 🎨 SUGGESTED |

## Repository Gotchas

_Architectural patterns and conventions specific to this repository._

### Complete View State Assertions Required

**Pattern**: bitwarden/android requires complete view state assertions in tests rather than individual property verification. This testing philosophy makes tests "stronger" by catching state coupling issues.

**Common Mistake**: Claude (and Claude-assisted developers) generate tests with individual property verification:
```kotlin
assertEquals(expectedState.property1, actualState.property1)
assertEquals(expectedState.property2, actualState.property2)
```

**Required Pattern**:
```kotlin
assertEquals(expectedState, actualState)
// or when specific fields change
assertEquals(expectedState.copy(changedField = newValue), actualState)
```

**Detection Strategy**:
```bash
rg "assertEquals\([^,]+\.[^,]+," app/src/test --type kotlin
```

**Impact**: Weaker tests that miss state coupling issues; false confidence; inconsistent testing patterns; human reviewer time wasted catching this repeatedly

**References**: PR [#6275](https://github.com/bitwarden/android/pull/6275)

### State Persistence Required for Conditional Navigation Flows

**Pattern**: When implementing conditional navigation flows based on feature flags, policies, or user state, must track whether user has already seen/dismissed the flow to prevent infinite loops.

**Common Mistake**: Implementing `StateFlow<Boolean>` that emits `true` whenever conditions are met, without tracking user interaction history. This causes navigation to trigger repeatedly on every sync/state check.

**Example Problem**:
```kotlin
val shouldMigratePersonalVaultFlow: StateFlow<Boolean>

private fun verifyConditions(cipherList: List<Cipher>) {
    val shouldMigrate = policyManager.getActivePolicies(PolicyTypeJson.PERSONAL_OWNERSHIP).any() &&
        featureFlagManager.getFeatureFlag(FlagKey.MigrateMyVaultToMyItems) &&
        connectionManager.isNetworkConnected &&
        cipherList.any { it.organizationId == null }
    // ⚠️ No check for whether user already dismissed this!
    mutableShouldMigratePersonalVaultFlow.update { shouldMigrate }
}
```

**Required Fix Pattern**:
```kotlin
// Add persistence methods in SettingsDiskSource or AuthDiskSource
fun storeMigrationAttempted(userId: String, organizationId: String)
fun hasMigrationBeenAttempted(userId: String, organizationId: String): Boolean

// Update validation logic
private fun verifyConditions(cipherList: List<Cipher>) {
    val shouldMigrate =
        !hasMigrationBeenAttempted(currentUserId, organizationId) && // NEW CHECK
        policyManager.getActivePolicies(PolicyTypeJson.PERSONAL_OWNERSHIP).any() &&
        featureFlagManager.getFeatureFlag(FlagKey.MigrateMyVaultToMyItems) &&
        connectionManager.isNetworkConnected &&
        cipherList.any { it.organizationId == null }
    mutableShouldMigratePersonalVaultFlow.update { shouldMigrate }
}
```

**Detection Strategy**:
```bash
# Find StateFlow<Boolean> fields controlling navigation without persistence checks
rg 'StateFlow<Boolean>' app/src/main/kotlin --type kotlin -A10 | \
  rg -v 'storeMigration|hasMigrationBeenAttempted'
```

**Impact**: Critical UX issue - infinite navigation loops make app unusable; applies to all feature-flag-driven conditional navigation flows

**References**: PR [#6279](https://github.com/bitwarden/android/pull/6279)

### Kotlin Delegation Pattern for Interface Composition

**Pattern**: Bitwarden Android uses Kotlin's `by` delegation keyword for interface composition when implementing cross-cutting concerns.

**Example**:
```kotlin
class SettingsDiskSourceImpl(
    private val sharedPreferences: SharedPreferences,
    private val json: Json,
    flightRecorderDiskSource: FlightRecorderDiskSource,
) : BaseDiskSource(sharedPreferences = sharedPreferences),
    SettingsDiskSource,
    FlightRecorderDiskSource by flightRecorderDiskSource {
    // Implementation only for SettingsDiskSource methods
    // FlightRecorderDiskSource methods delegated automatically
}
```

**Common Mistake**: Manually implementing interface methods instead of using delegation.

**Detection Strategy**: When adding cross-cutting concerns (logging, analytics), check if delegation is appropriate; look for constructor parameters that implement interfaces; search for pattern `Interface by parameter`.

**Impact**: Reduces boilerplate, improves testability, follows Single Responsibility Principle. Constructor complexity is acceptable trade-off.

**References**: PR [#6281](https://github.com/bitwarden/android/pull/6281)

### Module Architecture - Shared Logic in `:data` Module

**Pattern**: Common data source implementations belong in `:data` module, app-specific modules delegate.

**Architecture**:
```
:data/
  └── FlightRecorderDiskSource (concrete implementation)
:app/
  └── SettingsDiskSource (delegates to FlightRecorderDiskSource)
:authenticator/
  └── SettingsDiskSource (delegates to FlightRecorderDiskSource)
```

**Common Mistake**: Duplicating implementations in `:app` and `:authenticator`.

**Detection Strategy**: When reviewing data source changes, check if logic is duplicated across modules; if implementation identical, suggest moving to `:data` module; verify DI setup in all modules.

**Impact**: Code reusability across Bitwarden apps; single source of truth; easier testing.

**References**: PR [#6281](https://github.com/bitwarden/android/pull/6281)

### Talkback Behavior with Custom VisualTransformation

**Pattern**: Custom `VisualTransformation` in Compose prevents Talkback from reading text values normally. Solution requires explicit `semantics { contentDescription = actualText }` when content should be readable.

**Common Mistake**: Using custom visual transformations without considering accessibility implications.

**Detection Strategy**: Search for `VisualTransformation` implementations; verify accessibility semantics are set when content should be spoken; consider system setting overrides.

**Impact**: Accessibility issues for users relying on Talkback; potential security implications when overriding system "Speak Passwords" setting.

**References**: PR [#6222](https://github.com/bitwarden/android/pull/6222)

### Organization Event Tracking Two-Layer Pattern

**Pattern**: Organization events use dual abstraction - network enum with server integer values + application sealed class hierarchy

**Common Mistake**: Creating event types without both layers, or inconsistent naming between layers

**Detection Strategy**:
- Verify new `@SerialName` values in `OrganizationEventType.kt` have corresponding sealed class in `OrganizationEvent.kt`
- Check event numbering matches server definitions (1600-series for org events)
- Confirm event tracking occurs BEFORE UI state updates and navigation

**Impact**: Missing network layer causes serialization failures; missing app layer prevents type-safe tracking; wrong timing causes events to be lost due to ViewModel destruction

**References**: PR [#6275](https://github.com/bitwarden/android/pull/6275), [#6273](https://github.com/bitwarden/android/pull/6273)

### Package Name Logging Sensitivity in Credential Manager

**Pattern**: Package names are acceptable in Autofill flows but MUST NOT be logged in Credential Manager/passkey flows

**Common Mistake**: Logging `callingAppInfo.packageName` in error messages for Credential Manager operations

**Detection Strategy**:
```bash
grep -r "callingAppInfo.packageName" app/src/main/kotlin/com/x8bit/bitwarden/data/credentials/ | grep -E "(Timber|Log)"
```

**Impact**: Security-relevant information disclosure - reveals which apps are attempting sensitive credential operations

**References**: PR [#6229](https://github.com/bitwarden/android/pull/6229)

### String Resource Location Split (Legacy vs Modern)

**Pattern**: Feature flag strings split between `strings.xml` (legacy CXP flags) and `strings_non_localized.xml` (modern pattern)

**Common Mistake**: Assuming all non-localized strings go in same file

**Detection Strategy**: Search both files when validating feature flag completeness; prefer `strings_non_localized.xml` for new flags

**Impact**: Inconsistency in codebase; confusion about where to add new strings

**References**: PR [#6238](https://github.com/bitwarden/android/pull/6238)

### Navigation Args vs Repository Lookups

**Pattern**: If calling screen knows the data, pass it via navigation args rather than having ViewModel query repositories

**Common Mistake**: Injecting repositories into ViewModel to look up data that navigation source already has

**Detection Strategy**: When reviewing ViewModels with repository dependencies, check if injected data could come from navigation args instead

**Impact**: Unnecessary dependencies, increased ViewModel complexity, harder testing

**References**: PR [#6239](https://github.com/bitwarden/android/pull/6239)

### Vector Drawable Scaling Requirements

**Pattern**: Vector drawables require `rememberVectorPainter` + explicit `ContentScale` (not `painterResource` + `fillMaxWidth()`)

**Common Mistake**: Using `painterResource` with `fillMaxWidth()` causes image distortion

**Detection Strategy**: Search for `painterResource` used with vector drawables; verify `rememberVectorPainter` and `ContentScale.FillHeight` used instead

**Impact**: Visual UI distortion, poor user experience

**References**: PR [#6239](https://github.com/bitwarden/android/pull/6239)

### Test Coverage for Observability Code

**Pattern**: Logging statements (Timber calls) typically do NOT require test coverage in this codebase

**Common Mistake**: Requesting test coverage for observability-only PRs

**Detection Strategy**: When Codecov reports uncovered lines, check if they're Timber/logging statements; accept lower coverage for observability changes

**Impact**: Wasted effort writing tests for implementation details that aren't behavioral contracts

**References**: PR [#6229](https://github.com/bitwarden/android/pull/6229), [#6231](https://github.com/bitwarden/android/pull/6231)

### ProGuard Rules Duplication Across Modules

**Pattern**: Both `app/` and `authenticator/` modules have independent ProGuard configurations with duplicated rules

**Common Mistake**: Updating ProGuard rules in one module but not the other

**Detection Strategy**: When reviewing dependency updates or ProGuard changes, diff both proguard-rules.pro files

**Impact**: Inconsistent R8 optimization, potential runtime crashes in one module

**References**: PR [#6230](https://github.com/bitwarden/android/pull/6230)

### ZXing Usage Scope (QR_CODE Only)

**Pattern**: Bitwarden only uses ZXing for QR_CODE format decoding, not other formats (PDF417, Code128, etc.)

**Common Mistake**: Reviewing all ZXing release notes equally; focusing on irrelevant format improvements

**Detection Strategy**: Check `QrCodeAnalyzerImpl.kt` for `BarcodeFormat` usage; filter ZXing release notes by QR_CODE relevance

**Impact**: Time wasted on irrelevant release note analysis

**References**: PR [#6230](https://github.com/bitwarden/android/pull/6230)

### Markdown Files Excluded from Linting

**Pattern**: IDE formatters and detekt don't process `.md` files - manual whitespace vigilance required

**Common Mistake**: Assuming IDE will catch trailing whitespace in documentation

**Detection Strategy**:
```bash
git grep -I '[[:space:]]$' -- '*.md'
```

**Impact**: Whitespace inconsistencies in documentation files

**References**: PR [#6256](https://github.com/bitwarden/android/pull/6256)

### Event Tracking Timing Critical

**Pattern**: Organization event tracking must occur BEFORE navigation and UI state updates to prevent loss

**Common Mistake**: Placing `trackEvent` call after `sendEvent(NavigateEvent)` or state updates

**Detection Strategy**: Search for navigation events, verify `organizationEventManager.trackEvent` appears before them in control flow

**Impact**: Events lost due to ViewModel destruction during navigation; analytics gaps

**References**: PR [#6275](https://github.com/bitwarden/android/pull/6275)

## Methodology Improvements

_What worked and what didn't in review approaches._

### Documentation Review Process Effectiveness

**What Worked**: Iterative review with multiple team members caught progressively finer details; fresh eyes identified formatting issues; quick turnaround time (<2 hours for most issues); thread resolution discipline.

**What Didn't Work**: Initial submission didn't catch documentation quality issues in self-review; no apparent documentation linting or automated checks.

**Lesson**: For documentation-heavy PRs, conduct dedicated formatting/maintainability review pass separate from content review. Consider establishing documentation quality checklist or linting automation.

**Applicability**: Documentation PRs, CLAUDE.md changes, SKILL.md additions, markdown-heavy changes

**Example**: PR [#6072](https://github.com/bitwarden/android/pull/6072)

### Documentation Placeholder Pattern Recognition

**What Worked**: Using placeholder values (like `9999`) in documentation examples makes intent clear; keeping documentation examples generic improves pedagogical value.

**What Didn't Work**: Claude flagged documentation placeholders as critical mismatches without considering pedagogical intent; severity assessment too high for documentation style choices.

**Lesson**: When reviewing documentation changes, assess documentation purpose (reference vs example); recognize placeholder patterns (`9999`, `example.com`, `YOUR_VALUE_HERE`); calibrate severity appropriately; suggest clarification over demanding values match.

**Applicability**: CI/CD configuration examples, README getting-started guides, API documentation with sample requests/responses

**Example**: PR [#6282](https://github.com/bitwarden/android/pull/6282)

### Claude Bot Review Limitations with Repository-Specific Conventions

**What Worked**: Claude bot validated basic patterns (dependency injection, MVVM architecture, test presence); fast initial review (3m 16s); correctly identified core functionality was sound.

**What Didn't Work**: Bot failed to detect repository-specific testing conventions; approved code that violated established patterns; no check for complete vs partial state assertions; generated false confidence.

**Lesson**: Claude bot reviews require calibration to repository-specific conventions beyond language/framework defaults. Generic "best practices" may conflict with project-specific philosophies. Repository gotchas must be explicitly encoded in bot instructions.

**Applicability**: All automated Claude reviews for bitwarden/android; any repository with testing conventions that differ from framework defaults; projects where architectural philosophy trumps generic best practices

**Example**: PR [#6275](https://github.com/bitwarden/android/pull/6275)

### Early Architectural Review for Navigation Changes

**What Worked**: Claude identified state persistence issue by analyzing navigation flow and state management patterns before PR merged; traced how `StateFlow` would behave across multiple sync cycles; provided specific code examples showing required persistence pattern.

**What Didn't Work**: N/A - pattern was successful

**Lesson**: For refactoring PRs involving navigation or state management, validate architectural decisions first. Proactively trace state flows across multiple user interaction cycles to identify infinite loop patterns.

**Applicability**: Feature-flag-driven UX changes, policy-based navigation redirects, one-time setup/onboarding flows, migration prompts triggered by state conditions

**Example**: PR [#6279](https://github.com/bitwarden/android/pull/6279)

### Test-First Validation with CI Integration

**What Worked**: CI automatically runs tests on all PRs; failed "Test" check immediately flagged JSON syntax error; Claude bot review identified same issue before human review; combination of automated review + CI testing provides rapid feedback.

**What Didn't Work**: N/A - pattern was successful

**Lesson**: Multi-layered validation (bot review + CI) provides redundancy. JSON syntax errors in test data are easily caught by CI if tests attempt to parse the data. Always check CI test results before human review.

**Applicability**: Test data includes JSON, YAML, or other structured formats; any PR with test changes

**Example**: PR [#6281](https://github.com/bitwarden/android/pull/6281)

### Layered PR Strategy for Event Type Introduction

**What Worked**: Splitting event type additions into separate PRs - one for type definitions, one for usage implementation

**What Didn't Work**: N/A - pattern was successful

**Lesson**: Type system changes can be reviewed in isolation from business logic, enabling focused reviews with smaller surface area

**Applicability**: Feature additions requiring new types/models; gradual rollout of cross-cutting changes

**Example**: PR [#6273](https://github.com/bitwarden/android/pull/6273) defined types, [#6275](https://github.com/bitwarden/android/pull/6275) implemented tracking

### Version Discrepancy Cross-Validation

**What Worked**: Cross-referencing PR description URLs against actual code changes caught version mismatch

**What Didn't Work**: Could have automatically fetched correct release notes for implemented version

**Lesson**: Always validate PR descriptions against code diffs, especially for dependency updates; automate release notes fetching when discrepancy detected

**Applicability**: All dependency update PRs; any PR with external documentation links

**Example**: PR [#6231](https://github.com/bitwarden/android/pull/6231) - description referenced v7.2.0, code implemented v7.1.0

### Security Self-Review Two-Pass Pattern

**What Worked**: Author self-corrected security issue (package name logging) in second commit before review

**What Didn't Work**: N/A - self-correction prevented reviewer burden

**Lesson**: Security-sensitive changes benefit from explicit "security self-review" pass before submitting; demonstrates value of author pre-review

**Applicability**: Credential Manager changes, authentication flows, logging in sensitive contexts

**Example**: PR [#6229](https://github.com/bitwarden/android/pull/6229) - two commits with security cleanup in second

### Documentation Cross-Reference Validation Protocol

**What Worked**: Identifying companion objects mentioned in layout section but missing from documentation section

**What Didn't Work**: Gap existed because structure separates "what goes where" from "what requires docs"

**Lesson**: Multi-section documents require systematic cross-reference checks when updating element-type rules

**Applicability**: Style guide updates, architecture documentation, any multi-section reference docs

**Example**: PR [#6256](https://github.com/bitwarden/android/pull/6256) - added companion objects to documentation requirements

### Format-Specific Scope Analysis for Libraries

**What Worked**: Would have been more efficient to identify QR_CODE-only usage upfront

**What Didn't Work**: Generic barcode library review without usage scoping

**Lesson**: For format/feature-specific libraries (barcodes, media codecs, etc.), identify actual usage scope first, then filter release notes by relevance

**Applicability**: Barcode libraries, media format libraries, multi-format parsing libraries

**Example**: PR [#6230](https://github.com/bitwarden/android/pull/6230) - ZXing update where only QR_CODE format matters
