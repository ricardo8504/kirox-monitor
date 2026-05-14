import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import ChangePasswordRequest, UserCreate, UserUpdate


def test_login_request_valid():
    req = LoginRequest(email="user@example.com", password="secret")
    assert req.email == "user@example.com"


def test_login_request_invalid_email():
    with pytest.raises(ValidationError):
        LoginRequest(email="not-an-email", password="secret")


def test_token_response_defaults():
    t = TokenResponse(access_token="acc", refresh_token="ref")
    assert t.token_type == "bearer"


def test_user_create_valid():
    u = UserCreate(email="a@b.com", username="admin", password="12345678")
    assert u.role.value == "READONLY"


def test_user_create_short_password():
    with pytest.raises(ValidationError, match="8 characters"):
        UserCreate(email="a@b.com", username="admin", password="short")


def test_user_create_short_username():
    with pytest.raises(ValidationError, match="3 characters"):
        UserCreate(email="a@b.com", username="ab", password="12345678")


def test_user_update_partial():
    u = UserUpdate(is_active=False)
    assert u.email is None
    assert u.is_active is False


def test_change_password_valid():
    r = ChangePasswordRequest(current_password="old123456", new_password="new123456")
    assert r.new_password == "new123456"


def test_change_password_short_new():
    with pytest.raises(ValidationError):
        ChangePasswordRequest(current_password="old123456", new_password="short")
