"""Security primitives: password hashing and JWT (HS256) token handling.

Implemented with the Python standard library only (hashlib/hmac) so the auth
layer adds no heavy third-party dependency. This is authentication
infrastructure; it contains no domain/business logic.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

_PBKDF2_ALGORITHM = "sha256"
_PBKDF2_ITERATIONS = 240_000
_PBKDF2_SALT_BYTES = 16

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("BETAVANX_AUTH_TOKEN_TTL", "3600"))


def _secret_key() -> str:
    return os.getenv("BETAVANX_AUTH_SECRET", "dev-secret-change-me")


# --------------------------------------------------------------------------- #
# Password hashing (PBKDF2-HMAC-SHA256)
# --------------------------------------------------------------------------- #
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_PBKDF2_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGORITHM, password.encode("utf-8"), salt, _PBKDF2_ITERATIONS,
    )
    return (
        f"pbkdf2_{_PBKDF2_ALGORITHM}${_PBKDF2_ITERATIONS}$"
        f"{salt.hex()}${digest.hex()}"
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        scheme, iterations_s, salt_hex, digest_hex = hashed_password.split("$")
        algorithm = scheme.split("_", 1)[1]
        iterations = int(iterations_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, IndexError):
        return False

    candidate = hashlib.pbkdf2_hmac(
        algorithm, plain_password.encode("utf-8"), salt, iterations,
    )
    return hmac.compare_digest(candidate, expected)


# --------------------------------------------------------------------------- #
# JWT (HS256) — minimal, dependency-free
# --------------------------------------------------------------------------- #
def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(signing_input: bytes) -> str:
    signature = hmac.new(
        _secret_key().encode("utf-8"), signing_input, hashlib.sha256,
    ).digest()
    return _b64url_encode(signature)


def create_access_token(
    data: dict[str, Any],
    *,
    expires_in: int | None = None,
) -> str:
    expires_in = ACCESS_TOKEN_EXPIRE_SECONDS if expires_in is None else expires_in
    issued_at = int(time.time())
    payload: dict[str, Any] = {
        **data,
        "iat": issued_at,
        "exp": issued_at + expires_in,
    }
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_segment = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_segment = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    return f"{header_segment}.{payload_segment}.{_sign(signing_input)}"


class TokenError(Exception):
    """Raised when a token is malformed, tampered with, or expired."""


def decode_token(token: str) -> dict[str, Any]:
    try:
        header_segment, payload_segment, signature = token.split(".")
    except ValueError as exc:
        raise TokenError("Malformed token") from exc

    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected_signature = _sign(signing_input)
    if not hmac.compare_digest(expected_signature, signature):
        raise TokenError("Invalid token signature")

    try:
        payload: dict[str, Any] = json.loads(_b64url_decode(payload_segment))
    except (ValueError, json.JSONDecodeError) as exc:
        raise TokenError("Invalid token payload") from exc

    expiry = payload.get("exp")
    if expiry is not None and int(time.time()) > int(expiry):
        raise TokenError("Token expired")

    return payload
