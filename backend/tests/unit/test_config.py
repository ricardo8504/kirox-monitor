import pytest

from app.core.config import Settings


def test_settings_loads_correctly(test_settings: Settings) -> None:
    assert test_settings.app_env == "test"
    assert test_settings.jwt_algorithm == "HS256"
    assert test_settings.access_token_expire_minutes == 60
    assert test_settings.default_monitoring_interval == 60


def test_secret_key_min_length() -> None:
    with pytest.raises(Exception):
        Settings(
            app_env="test",
            secret_key="tooshort",
            encryption_key="anykey",
            database_url="postgresql+asyncpg://x:x@localhost/x",
        )


def test_allowed_origins_list(test_settings: Settings) -> None:
    settings = Settings(
        app_env="test",
        secret_key="test_secret_key_that_is_at_least_32_chars_long!!",
        encryption_key="key",
        database_url="postgresql+asyncpg://x:x@localhost/x",
        allowed_origins="http://localhost,http://localhost:3000, http://app.example.com",
    )
    origins = settings.allowed_origins_list
    assert len(origins) == 3
    assert "http://localhost" in origins
    assert "http://app.example.com" in origins


def test_is_test_flag(test_settings: Settings) -> None:
    assert test_settings.is_test is True
    assert test_settings.is_development is False


def test_is_development_flag() -> None:
    s = Settings(
        app_env="development",
        secret_key="test_secret_key_that_is_at_least_32_chars_long!!",
        encryption_key="key",
        database_url="postgresql+asyncpg://x:x@localhost/x",
    )
    assert s.is_development is True
    assert s.is_test is False
