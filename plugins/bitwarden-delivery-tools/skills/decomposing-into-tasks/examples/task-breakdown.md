# Tech Breakdown examples

Shape references for the `Tech Breakdown` field on a task row. Use these as a guide for what good code-first content looks like; do not copy verbatim.

## A row touching a C# enum

````markdown
- **Tech Breakdown**:
  ```csharp
  // server/src/Core/Notifications/PushType.cs
  public enum PushType {
      // existing values...
      LoginApprovalRequest = 24,
      SecurityKeyRegistered = 25, // new
  }
  ```
````

## A row adding a controller dispatch

````markdown
- **Tech Breakdown**:
  ```csharp
  // server/src/Api/Auth/Controllers/WebAuthnController.cs
  // Inside PostAttestation, after AttestationVerificationSucceeded:
  if (_featureService.IsEnabled(FeatureFlagKeys.SecurityKeyRegisteredPush)) {
      await _pushService.PushAsync(user.Id, PushType.SecurityKeyRegistered, new {
          friendlyName = request.Name,
          keyId = credential.Id,
      });
      _metrics.Counter("notifications.security_key_registered.sent").Increment();
  }
  ```
````

## A row adding a TypeScript handler branch

````markdown
- **Tech Breakdown**:

  ```ts
  // clients/libs/common/src/services/push.service.ts
  case PushType.SecurityKeyRegistered:
      this.handleSecurityKeyRegistered(payload as { friendlyName: string; keyId: string });
      break;

  private handleSecurityKeyRegistered(payload: { friendlyName: string; keyId: string }) {
      // emit to banner host subject; pattern mirrors handleLoginApprovalRequest
  }
  ```
````
