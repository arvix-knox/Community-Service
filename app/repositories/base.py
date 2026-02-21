"""Базовый репозиторий с общими CRUD-операциями."""
from __future__ import annotations
import uuid
from typing import Any, Generic, List, Optional, Sequence, Type, TypeVar

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self._model = model
        self._session = session

    async def get_by_id(self, entity_id: uuid.UUID) -> Optional[ModelType]:
        result = await self._session.get(self._model, entity_id)
        return result

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        filters: Optional[list] = None,
        order_by: Optional[Any] = None,
    ) -> Sequence[ModelType]:
        stmt = select(self._model)
        if filters:
            for f in filters:
                stmt = stmt.where(f)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        else:
            stmt = stmt.order_by(self._model.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count(self, filters: Optional[list] = None) -> int:
        stmt = select(func.count()).select_from(self._model)
        if filters:
            for f in filters:
                stmt = stmt.where(f)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def create(self, entity: ModelType) -> ModelType:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update_by_id(self, entity_id: uuid.UUID, data: dict) -> Optional[ModelType]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.get_by_id(entity_id)

        stmt = (
            update(self._model)
            .where(self._model.id == entity_id)
            .values(**update_data)
            .returning(self._model)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        entity = result.scalar_one_or_none()
        if entity:
            await self._session.refresh(entity)
        return entity

    async def delete_by_id(self, entity_id: uuid.UUID) -> bool:
        stmt = delete(self._model).where(self._model.id == entity_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0
