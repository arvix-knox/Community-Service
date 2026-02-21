"""Схемы для Subscription."""
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionLevelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=3)
    duration_days: int = Field(default=30, ge=1)
    features: Optional[dict] = None
    max_subscribers: Optional[int] = Field(None, ge=1)


class SubscriptionLevelResponse(BaseModel):
    id: uuid.UUID
    community_id: uuid.UUID
    name: str
    description: Optional[str] = None
    price: Decimal
    currency: str
    duration_days: int
    features: Optional[dict] = None
    is_active: bool
    max_subscribers: Optional[int] = None
    subscriber_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionCreate(BaseModel):
    level_id: uuid.UUID
    auto_renew: bool = True


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    level_id: uuid.UUID
    user_id: uuid.UUID
    community_id: uuid.UUID
    status: str
    starts_at: datetime
    expires_at: datetime
    auto_renew: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
