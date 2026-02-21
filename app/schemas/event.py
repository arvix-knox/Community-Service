"""Схемы для Event."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)
    starts_at: datetime
    ends_at: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=500)
    online_url: Optional[str] = Field(None, max_length=1024)
    max_attendees: Optional[int] = Field(None, ge=1)
    cover_url: Optional[str] = None


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)
    status: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=500)
    online_url: Optional[str] = None
    max_attendees: Optional[int] = Field(None, ge=1)
    cover_url: Optional[str] = None


class EventResponse(BaseModel):
    id: uuid.UUID
    community_id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    description: Optional[str] = None
    status: str
    starts_at: datetime
    ends_at: Optional[datetime] = None
    location: Optional[str] = None
    online_url: Optional[str] = None
    max_attendees: Optional[int] = None
    attendee_count: int
    cover_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
