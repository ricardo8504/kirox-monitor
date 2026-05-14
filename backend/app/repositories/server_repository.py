import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.server import Server


class ServerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, server_id: uuid.UUID) -> Server | None:
        result = await self._session.execute(select(Server).where(Server.id == server_id))
        return result.scalar_one_or_none()

    async def create(self, server: Server) -> Server:
        self._session.add(server)
        await self._session.flush()
        await self._session.refresh(server)
        return server

    async def update(self, server: Server) -> Server:
        await self._session.flush()
        await self._session.refresh(server)
        return server

    async def delete(self, server: Server) -> None:
        await self._session.delete(server)
        await self._session.flush()

    async def update_last_seen(self, server_id: uuid.UUID, ts: datetime) -> None:
        await self._session.execute(
            update(Server)
            .where(Server.id == server_id)
            .values(last_seen=ts.isoformat())
        )

    async def list(
        self,
        is_active: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Server]:
        q = select(Server)
        if is_active is not None:
            q = q.where(Server.is_active == is_active)
        q = q.offset(offset).limit(limit)
        result = await self._session.execute(q)
        return result.scalars().all()
