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

### ECB Mode

```csharp
// WRONG — ECB mode (reveals patterns in plaintext)
var aes = Aes.Create();
aes.Mode = CipherMode.ECB;

// CORRECT — GCM mode (authenticated encryption)
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
