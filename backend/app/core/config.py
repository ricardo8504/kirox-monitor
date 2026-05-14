from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "odoo-monitor"
    app_env: Literal["production", "development", "test"] = "production"
    debug: bool = False
    log_level: str = "INFO"

    # Security
    secret_key: str
    encryption_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Database
    database_url: str
    database_url_sync: str = ""

    # Redis
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # CORS
    allowed_origins: str = "http://localhost"

    # Admin seed
    admin_email: str = "admin@example.com"
    admin_password: str = "changeme"
    admin_username: str = "admin"

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@example.com"
    smtp_tls: bool = True

    # Telegram
    telegram_bot_token: str = ""

    # Monitoring
    default_monitoring_interval: int = 60
    metric_retention_days: int = 90
    max_concurrent_ssh: int = 10
    ssh_timeout: int = 10

    # Rate limiting
    rate_limit_login: str = "5/minute"

    @field_validator("secret_key")
    @classmethod
    def secret_key_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_test(self) -> bool:
        return self.app_env == "test"


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
