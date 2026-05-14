import time

import pytest

from app.core.encryption import decrypt, encrypt
from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


# --- Password ---

def test_hash_password_returns_string():
    h = hash_password("mypassword")
    assert isinstance(h, str)
    assert h != "mypassword"


def test_verify_password_correct():
    h = hash_password("secret123")
    assert verify_password("secret123", h) is True


def test_verify_password_wrong():
    h = hash_password("secret123")
    assert verify_password("wrongpass", h) is False


def test_hash_is_unique():
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2  # bcrypt salt is random


# --- JWT ---

def test_create_and_decode_access_token():
    token = create_access_token("user-uuid", "ADMIN")
    payload = decode_token(token, "access")
    assert payload["sub"] == "user-uuid"
    assert payload["role"] == "ADMIN"
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token():
    token = create_refresh_token("user-uuid")
    payload = decode_token(token, "refresh")
    assert payload["sub"] == "user-uuid"
    assert payload["type"] == "refresh"


def test_wrong_token_type_raises():
    access = create_access_token("u", "READONLY")
    with pytest.raises(UnauthorizedError, match="Expected refresh token"):
        decode_token(access, "refresh")


def test_invalid_token_raises():
    with pytest.raises(UnauthorizedError, match="Invalid token"):
        decode_token("not.a.token", "access")


def test_tampered_token_raises():
    token = create_access_token("u", "ADMIN")
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(UnauthorizedError):
        decode_token(tampered)


# --- Fernet encryption ---

def test_encrypt_decrypt_roundtrip():
    secret = "my-ssh-password-123"
    ciphertext = encrypt(secret)
    assert ciphertext != secret
    assert decrypt(ciphertext) == secret


def test_encrypt_produces_different_ciphertext():
    c1 = encrypt("same")
    c2 = encrypt("same")
    assert c1 != c2  # Fernet uses random IV
