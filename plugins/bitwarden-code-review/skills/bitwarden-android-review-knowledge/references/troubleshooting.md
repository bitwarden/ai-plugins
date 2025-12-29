# Review Troubleshooting: bitwarden/android

## Error → Solution Mappings

### Package Name Logged in Credential Manager Context

**Symptom**: Review comment flags package name logging in Credential Manager/Origin validation flows

**Cause**: `callingAppInfo.packageName` included in error/debug logs for credential operations

**Solution**: Remove package name from log messages; use generic "calling app" phrasing

**Detection Command**:
```bash
grep -r "callingAppInfo.packageName" \
  app/src/main/kotlin/com/x8bit/bitwarden/data/credentials/ | \
  grep -E "(Timber|Log)"
```

**References**: PR [#6229](https://github.com/bitwarden/android/pull/6229)

---

### Network Serialization Tests Missing for New Event Types

**Symptom**: New OrganizationEventType enum values lack explicit serialization tests

**Cause**: Generic `BaseEnumeratedIntSerializer` handles all enums, making tests seem redundant

**Solution**: Add round-trip serialization tests to document API contract and catch enum reordering

**Detection Command**:
```bash
# Find new @SerialName annotations without corresponding tests
NEW_EVENTS=$(grep -oP '@SerialName\("\K\d+' \
  network/src/main/kotlin/com/bitwarden/network/model/OrganizationEventType.kt)

for event_num in $NEW_EVENTS; do
  grep -q "$event_num" \
    network/src/test/kotlin/com/bitwarden/network/service/EventServiceTest.kt || \
    echo "Missing test for event type $event_num"
done
```

**References**: PR [#6273](https://github.com/bitwarden/android/pull/6273)

---

### ProGuard Rules Out of Sync Across Modules

**Symptom**: Library works in one app module but fails in another with R8/ProGuard errors

**Cause**: ProGuard rules updated in `app/proguard-rules.pro` but not `authenticator/proguard-rules.pro`

**Solution**: Synchronize rules across both modules when updating library-specific configurations

**Detection Command**:
```bash
# Check for ZXing rule differences
diff -u \
  <(grep -A10 "zxing" app/proguard-rules.pro) \
  <(grep -A10 "zxing" authenticator/proguard-rules.pro)
```

**References**: PR [#6230](https://github.com/bitwarden/android/pull/6230)

---

### Navigation Occurs Before Event Tracking

**Symptom**: Analytics show missing organization events despite tracking code present

**Cause**: `sendEvent(NavigateEvent)` called before `organizationEventManager.trackEvent()`, causing ViewModel destruction

**Solution**: Always place event tracking BEFORE navigation and UI state updates

**Detection Command**:
```bash
# Find potential ordering issues
grep -B5 "sendEvent.*Navigate" \
  app/src/main/kotlin/com/x8bit/bitwarden/ui/**/*/ViewModel.kt | \
  grep -v "organizationEventManager.trackEvent"
```

**References**: PR [#6275](https://github.com/bitwarden/android/pull/6275)

---

### Vector Drawable Distortion in Compose

**Symptom**: Illustration renders stretched or distorted in screen

**Cause**: Using `painterResource` with `fillMaxWidth()` instead of proper vector painter

**Solution**: Use `rememberVectorPainter` with explicit `ContentScale.FillHeight`

**Detection Command**:
```bash
# Find potentially problematic vector usage
grep -r "painterResource.*drawable.ill_" \
  app/src/main/kotlin/com/x8bit/bitwarden/ui/ | \
  xargs -I {} sh -c 'grep -l "fillMaxWidth" $(dirname {})'
```

**References**: PR [#6239](https://github.com/bitwarden/android/pull/6239)

---

### Feature Flag Missing from Required Files

**Symptom**: Compilation error or runtime crash when feature flag accessed

**Cause**: Feature flag defined in `FlagKey.kt` but missing from test, UI, or strings files

**Solution**: Ensure flag exists in all 4 required locations with matching names

**Detection Command**:
```bash
# Verify flag completeness (replace with your flag name)
FLAG="YourDataObjectName"
FILES=(
  "core/src/main/kotlin/com/bitwarden/core/data/manager/model/FlagKey.kt"
  "core/src/test/kotlin/com/bitwarden/core/data/manager/model/FlagKeyTest.kt"
  "ui/src/main/kotlin/com/bitwarden/ui/platform/components/debug/FeatureFlagListItems.kt"
  "ui/src/main/res/values/strings_non_localized.xml"
)
for file in "${FILES[@]}"; do
  grep -q "$FLAG" "$file" || echo "❌ Missing in: $file"
done
```

**References**: PR [#6238](https://github.com/bitwarden/android/pull/6238)

---

### SavedStateHandle Extension Mocking Fails

**Symptom**: ViewModel test fails with "no mock behavior defined" for SavedStateHandle extension

**Cause**: Extension functions require static mocking with MockK

**Solution**: Use `mockkStatic` before test, `unmockkStatic` in cleanup

**Detection Command**:
```bash
# Find SavedStateHandle extensions that might need mocking
grep -r "fun SavedStateHandle\.to.*Args" \
  app/src/main/kotlin/com/x8bit/bitwarden/ui/
```

**Example Fix**:
```kotlin
@BeforeEach
fun setup() {
    mockkStatic(SavedStateHandle::toFeatureArgs)
}

@AfterEach
fun tearDown() {
    unmockkStatic(SavedStateHandle::toFeatureArgs)
}
```

**References**: PR [#6239](https://github.com/bitwarden/android/pull/6239)

---

### Dependency Update Version Mismatch

**Symptom**: PR description links to different version than code implements

**Cause**: PR description written before final version decided, not updated

**Solution**: Cross-reference PR description URLs against actual version in `libs.versions.toml`

**Detection Command**:
```bash
# Extract version from PR description and compare to code
# (Manual process - review PR body URLs vs gradle file)
```

**References**: PR [#6231](https://github.com/bitwarden/android/pull/6231)
