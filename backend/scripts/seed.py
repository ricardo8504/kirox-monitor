#!/usr/bin/env python3
"""Create the initial admin user from environment variables."""

import asyncio
import os

from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.auth_service import UserService

logger = get_logger(__name__)


async def seed() -> None:
    email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD", "")

    if not password:
        logger.warning("seed_skipped", reason="ADMIN_PASSWORD not set")
        return

    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        service = UserService(repo)

        existing = await repo.get_by_email(email)
        if existing:
            logger.info("seed_skipped", reason="admin already exists", email=email)
            return

        data = UserCreate(
            email=email,
            username=username,
            password=password,
            role=UserRole.ADMIN,
        )
        await service.create_user(data)
        await session.commit()
        logger.info("seed_done", email=email, username=username)


if __name__ == "__main__":
    asyncio.run(seed())
