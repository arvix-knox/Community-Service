"""Схемы для Donation."""
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DonationCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    message: Optional[str] = Field(None, max_length=1000)
    is_anonymous: bool = False


class DonationResponse(BaseModel):
    id: uuid.UUID
    community_id: uuid.UUID
    donor_id: uuid.UUID
    amount: Decimal
    currency: str
    message: Optional[str] = None
    status: str
    transaction_id: Optional[str] = None
    is_anonymous: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
