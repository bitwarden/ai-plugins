# Cryptographic Patterns

## Algorithm Selection

| Use Case              | Recommended                                                     | Deprecated / Avoid                      |
| --------------------- | --------------------------------------------------------------- | --------------------------------------- |
| Symmetric encryption  | AES-256-GCM, ChaCha20-Poly1305                                  | DES, 3DES, AES-ECB, Blowfish            |
| Hashing               | SHA-256, SHA-384, SHA-512, BLAKE2                               | MD5, SHA-1                              |
| Password hashing      | Argon2id, bcrypt, PBKDF2 (high iterations)                      | MD5, SHA-\*, plain bcrypt with low cost |
| Asymmetric encryption | RSA-OAEP (2048+ bits), ECIES                                    | RSA-PKCS1v1.5, RSA < 2048 bits          |
| Digital signatures    | Ed25519, ECDSA P-256, RSA-PSS                                   | RSA-PKCS1v1.5, DSA                      |
| Key exchange          | ECDH P-256, X25519                                              | DH with small primes                    |
| Random generation     | `RandomNumberGenerator` (.NET), `crypto.getRandomValues()` (JS) | `Math.random()`, `System.Random`        |

## Common Crypto Anti-Patterns

### Hand-Built Tokens and Formats

```csharp
// WRONG — a JWS composed by hand: header and claims serialized, then signed with the primitive
var signingInput = $"{Base64Url(header)}.{Base64Url(claims)}";
var signature = ecdsa.SignData(Encoding.ASCII.GetBytes(signingInput), HashAlgorithmName.SHA256);
var jwt = $"{signingInput}.{Base64Url(signature)}";

// CORRECT — the token library builds and signs it
var token = new JsonWebTokenHandler().CreateToken(new SecurityTokenDescriptor
{
    Issuer = clientId,
    Audience = audience,
    Expires = now.AddMinutes(1),
    TokenType = "client-authentication+jwt",
    Claims = new Dictionary<string, object>
    {
        ["sub"] = clientId,
        ["jti"] = Guid.NewGuid().ToString(),
    },
    SigningCredentials = new SigningCredentials(new ECDsaSecurityKey(ecdsa), SecurityAlgorithms.EcdsaSha256),
});
```

The hand-built version can be correct and still be a finding: every format detail it gets right by hand is one a library already tests, and every one it gets wrong is a vulnerability no one else will catch.

### ECB Mode

```csharp
// WRONG — ECB mode (reveals patterns in plaintext)
var aes = Aes.Create();
aes.Mode = CipherMode.ECB;

// CORRECT (mode choice only) — GCM mode (authenticated encryption)
// For a stored or transmitted format, use the codebase's library (EncString, Data Protection) rather than AesGcm directly
var aesGcm = new AesGcm(key);
```

### Predictable IV

```csharp
// WRONG — predictable IV
var iv = new byte[16]; // All zeros

// CORRECT — random IV for each encryption operation
var iv = RandomNumberGenerator.GetBytes(16);
```

### Insecure Random

```typescript
// WRONG — Math.random() for security-sensitive values
const token = Math.random().toString(36);

// CORRECT — cryptographic random
const token = crypto.getRandomValues(new Uint8Array(32));
```
