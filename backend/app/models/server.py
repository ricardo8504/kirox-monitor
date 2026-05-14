import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ServerType(StrEnum):
    PRODUCTION = "PRODUCTION"
    STAGING = "STAGING"
    DEVELOPMENT = "DEVELOPMENT"


class Environment(StrEnum):
    PRODUCTION = "PRODUCTION"
    STAGING = "STAGING"
    DEVELOPMENT = "DEVELOPMENT"


class Server(BaseModel):
    __tablename__ = "servers"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False, default=22)
    ssh_user: Mapped[str] = mapped_column(String(100), nullable=False)
    ssh_password_encrypted: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ssh_key_encrypted: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    server_type: Mapped[ServerType] = mapped_column(
        Enum(ServerType, name="server_type"), nullable=False, default=ServerType.PRODUCTION
    )
    environment: Mapped[Environment] = mapped_column(
        Enum(Environment, name="environment"), nullable=False, default=Environment.PRODUCTION
    )
    monitoring_interval: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_seen: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
