"""Схемы для Channel."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    channel_type: str = Field(default="text")
    is_default: bool = False
    position: int = 0
    settings: Optional[dict] = None


class ChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    channel_type: Optional[str] = None
    position: Optional[int] = None
    settings: Optional[dict] = None


class ChannelResponse(BaseModel):
    id: uuid.UUID
    community_id: uuid.UUID
    name: str
    description: Optional[str] = None
    channel_type: str
    is_default: bool
    position: int
    settings: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
