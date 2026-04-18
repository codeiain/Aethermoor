"""Unit tests for auth utilities — no external dependencies required."""
import os
import time

import jwt
import pytest

# Set required env vars before importing service modules
os.environ.setdefault("JWT_SECRET", "test-secret-do-not-use-in-production")
os.environ.setdefault("SERVICE_TOKEN", "test-service-token-do-not-use-in-production")
os.environ.setdefault("DATABASE_URL", "postgresql://unused:unused@localhost/unused")
os.environ.setdefault("REDIS_URL", "redis://:unused@localhost:6379/0")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from zero_trust import ServiceTokenError, make_service_token, verify_service_token_value


# ── Password hashing ──────────────────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        pw = "correct-horse-battery-staple"
        hashed = hash_password(pw)
        assert hashed != pw

    def test_verify_correct_password(self):
        pw = "correct-horse-battery-staple"
        hashed = hash_password(pw)
        assert verify_password(pw, hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct-horse-battery-staple")
        assert verify_password("wrong-password", hashed) is False

    def test_two_hashes_differ(self):
        pw = "same-password"
        assert hash_password(pw) != hash_password(pw)  # different salts

    def test_verify_rejects_bad_hash(self):
        assert verify_password("password", "not-a-valid-hash") is False


# ── JWT ───────────────────────────────────────────────────────────────────────

class TestJWT:
    def test_access_token_roundtrip(self):
        token, jti = create_access_token("user-123", "testuser")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
        assert payload["jti"] == jti

    def test_refresh_token_roundtrip(self):
        token, jti = create_refresh_token("user-456")
        payload = decode_token(token)
        assert payload["sub"] == "user-456"
        assert payload["type"] == "refresh"
        assert payload["jti"] == jti

    def test_access_and_refresh_have_different_jtis(self):
        _, jti_a = create_access_token("user-1", "u1")
        _, jti_b = create_access_token("user-1", "u1")
        assert jti_a != jti_b

    def test_invalid_token_raises(self):
        with pytest.raises(jwt.InvalidTokenError):
            decode_token("not.a.valid.token")

    def test_tampered_token_raises(self):
        token, _ = create_access_token("user-123", "testuser")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(jwt.InvalidTokenError):
            decode_token(tampered)

    def test_wrong_algorithm_rejected(self):
        """Verify alg:none is rejected (algorithm pinning)."""
        payload = {"sub": "user-x", "type": "access"}
        # Create a token with alg:none (no signature)
        none_token = jwt.encode(payload, "", algorithm="none")
        with pytest.raises(jwt.InvalidTokenError):
            decode_token(none_token)

    def test_expire_minutes_is_15(self):
        assert ACCESS_TOKEN_EXPIRE_MINUTES == 15


# ── Zero-trust service tokens ─────────────────────────────────────────────────

class TestZeroTrust:
    def test_valid_token_accepted(self):
        token = make_service_token()
        verify_service_token_value(token)  # Should not raise

    def test_missing_token_raises(self):
        with pytest.raises(ServiceTokenError, match="Missing"):
            verify_service_token_value(None)

    def test_empty_token_raises(self):
        with pytest.raises(ServiceTokenError, match="Missing"):
            verify_service_token_value("")

    def test_malformed_token_raises(self):
        with pytest.raises(ServiceTokenError, match="Malformed"):
            verify_service_token_value("notimestamp")

    def test_expired_token_raises(self):
        old_bucket = (int(time.time()) // 60) - 5  # 5 minutes ago
        import hashlib
        import hmac
        digest = hmac.new(
            os.environ["SERVICE_TOKEN"].encode(),
            str(old_bucket).encode(),
            hashlib.sha256,
        ).hexdigest()
        with pytest.raises(ServiceTokenError, match="expired"):
            verify_service_token_value(f"{old_bucket}:{digest}")

    def test_wrong_secret_raises(self):
        import hashlib
        import hmac
        ts = int(time.time()) // 60
        bad_digest = hmac.new(
            b"wrong-secret",
            str(ts).encode(),
            hashlib.sha256,
        ).hexdigest()
        with pytest.raises(ServiceTokenError, match="invalid"):
            verify_service_token_value(f"{ts}:{bad_digest}")
