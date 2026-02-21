"""Схемы для Post."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PostCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1, max_length=50000)
    channel_id: Optional[uuid.UUID] = None
    status: str = Field(default="published")
    is_pinned: bool = False
    media_urls: Optional[List[str]] = None


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=1, max_length=50000)
    status: Optional[str] = None
    is_pinned: Optional[bool] = None
    media_urls: Optional[List[str]] = None


class PostResponse(BaseModel):
    id: uuid.UUID
    community_id: uuid.UUID
    channel_id: Optional[uuid.UUID] = None
    author_id: uuid.UUID
    title: Optional[str] = None
    content: str
    status: str
    is_pinned: bool
    media_urls: Optional[List[str]] = None
    like_count: int
    comment_count: int
    view_count: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
