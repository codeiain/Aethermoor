"""Smoke tests for the auth service schemas."""
import pytest
from schemas import (
    RegisterRequest,
    LoginRequest,
    VerifyTokenRequest,
    TokenResponse,
    UserResponse,
    VerifyTokenResponse,
    MessageResponse,
)


class TestRegisterRequest:
    def test_valid_registration(self):
        req = RegisterRequest(email="Test@Example.com", password="securepassword123")
        assert req.email == "test@example.com"

    def test_email_normalized_to_lowercase(self):
        req = RegisterRequest(email="USER@GMAIL.COM", password="password123")
        assert req.email == "user@gmail.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValueError, match="invalid email"):
            RegisterRequest(email="not-an-email", password="password123")

    def test_email_missing_tld_rejected(self):
        with pytest.raises(ValueError, match="invalid email"):
            RegisterRequest(email="user@example", password="password123")

    def test_password_too_short(self):
        with pytest.raises(ValueError, match="at least 8 characters"):
            RegisterRequest(email="user@example.com", password="short")

    def test_password_exactly_8_chars_accepted(self):
        req = RegisterRequest(email="user@example.com", password="12345678")
        assert len(req.password) == 8


class TestLoginRequest:
    def test_login_request_accepts_valid_data(self):
        req = LoginRequest(email="user@example.com", password="password123")
        assert req.email == "user@example.com"
        assert req.password == "password123"


class TestVerifyTokenRequest:
    def test_verify_token_request(self):
        req = VerifyTokenRequest(token="some.jwt.token")
        assert req.token == "some.jwt.token"


class TestResponses:
    def test_token_response(self):
        resp = TokenResponse(
            access_token="access",
            refresh_token="refresh",
            expires_in=3600,
        )
        assert resp.token_type == "bearer"
        assert resp.expires_in == 3600

    def test_user_response(self):
        from datetime import datetime
        resp = UserResponse(
            id="user-123",
            username="aldric",
            email="aldric@example.com",
            is_active=True,
            created_at=datetime.now(),
        )
        assert resp.id == "user-123"
        assert resp.username == "aldric"

    def test_verify_token_response_valid(self):
        resp = VerifyTokenResponse(valid=True, user_id="user-123", username="aldric")
        assert resp.valid is True
        assert resp.user_id == "user-123"

    def test_verify_token_response_invalid(self):
        resp = VerifyTokenResponse(valid=False)
        assert resp.valid is False
        assert resp.user_id is None

    def test_message_response(self):
        resp = MessageResponse(message="Operation successful")
        assert resp.message == "Operation successful"
