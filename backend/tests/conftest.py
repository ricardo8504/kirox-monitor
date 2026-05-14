import base64
import os

import pytest

# Force test environment before any app imports
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("SECRET_KEY", "test_secret_key_that_is_at_least_32_chars_long!!")
# Valid Fernet key: 32 bytes URL-safe base64 encoded (single `=` padding)
os.environ.setdefault(
    "ENCRYPTION_KEY",
    base64.urlsafe_b64encode(b"test_fernet_key_32bytes_exactly_").decode(),
)
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture(scope="session")
def test_settings():
    from app.core.config import Settings

    return Settings(
        app_env="test",
        secret_key="test_secret_key_that_is_at_least_32_chars_long!!",
        encryption_key="dGVzdF9lbmNyeXB0aW9uX2tleV8zMmNoYXJzX19fXw==",
        database_url="postgresql+asyncpg://test:test@localhost:5432/test",
        redis_url="redis://localhost:6379/0",
    )
