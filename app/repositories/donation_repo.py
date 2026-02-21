"""Репозиторий донатов."""
from __future__ import annotations
import uuid
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Donation
from app.repositories.base import BaseRepository


class DonationRepository(BaseRepository[Donation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Donation, session)

    async def get_community_donations(
        self, community_id: uuid.UUID, offset: int = 0, limit: int = 20,
    ) -> tuple[Sequence[Donation], int]:
        filters = [Donation.community_id == community_id, Donation.status == "completed"]
        items = await self.get_all(offset=offset, limit=limit, filters=filters)
        total = await self.count(filters=filters)
        return items, total

    async def get_total_donations(self, community_id: uuid.UUID) -> Decimal:
        stmt = select(func.coalesce(func.sum(Donation.amount), 0)).where(
            and_(Donation.community_id == community_id, Donation.status == "completed")
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_top_donors(self, community_id: uuid.UUID, limit: int = 10) -> list[dict]:
        stmt = (
            select(
                Donation.donor_id,
                func.sum(Donation.amount).label("total_amount"),
                func.count(Donation.id).label("donation_count"),
            )
            .where(and_(Donation.community_id == community_id, Donation.status == "completed"))
            .group_by(Donation.donor_id)
            .order_by(func.sum(Donation.amount).desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [
            {"user_id": str(row.donor_id), "total_amount": float(row.total_amount), "donation_count": row.donation_count}
            for row in rows
        ]
