import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator, model_validator

from app.models.server import Environment, ServerType


class ServerCreate(BaseModel):
    name: str
    host: str
    port: int = 22
    ssh_user: str
    ssh_password: str | None = None
    ssh_key: str | None = None
    server_type: ServerType = ServerType.PRODUCTION
    environment: Environment = Environment.PRODUCTION
    monitoring_interval: int = 60
    odoo_port: int = 8069
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str | None = None

    @field_validator("port")
    @classmethod
    def valid_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("monitoring_interval")
    @classmethod
    def valid_interval(cls, v: int) -> int:
        if v < 10:
            raise ValueError("Monitoring interval must be at least 10 seconds")
        return v

    @model_validator(mode="after")
    def require_auth(self) -> "ServerCreate":
        if not self.ssh_password and not self.ssh_key:
            raise ValueError("Either ssh_password or ssh_key must be provided")
        return self


class ServerUpdate(BaseModel):
    name: str | None = None
    host: str | None = None
    port: int | None = None
    ssh_user: str | None = None
    ssh_password: str | None = None
    ssh_key: str | None = None
    server_type: ServerType | None = None
    environment: Environment | None = None
    monitoring_interval: int | None = None
    odoo_port: int | None = None
    db_port: int | None = None
    db_user: str | None = None
    db_password: str | None = None
    is_active: bool | None = None


class ServerResponse(BaseModel):
    id: uuid.UUID
    name: str
    host: str
    port: int
    ssh_user: str
    server_type: ServerType
    environment: Environment
    monitoring_interval: int
    odoo_port: int
    db_port: int
    db_user: str
    is_active: bool
    last_seen: str | None
    created_by: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ServerListResponse(BaseModel):
    items: list[ServerResponse]
    total: int
