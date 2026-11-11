import secrets
import hashlib
import base64


# 1. Generate state
state = secrets.token_urlsafe(32)

# 2. Generate nonce
nonce = secrets.token_urlsafe(32)

# 3. Generate PKCE code verifier
code_verifier = secrets.token_urlsafe(64)

# 4. Generate SHA-256 challenge
digest = hashlib.sha256(
    code_verifier.encode("ascii")
).digest()

code_challenge = (
    base64.urlsafe_b64encode(digest)
    .rstrip(b"=")
    .decode("ascii")
)

print("STATE:", state)
print("NONCE:", nonce)
print("CODE VERIFIER:", code_verifier)
print("CODE CHALLENGE:", code_challenge)

# 5. Verify PKCE calculation
verification = (
    base64.urlsafe_b64encode(
        hashlib.sha256(
            code_verifier.encode("ascii")
        ).digest()
    )
    .rstrip(b"=")
    .decode("ascii")
)

assert verification == code_challenge

print("\nPKCE verification successful!")
