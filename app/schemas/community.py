"""Схемы для Community."""
from __future__ import annotations
import uuid
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CommunityCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    community_type: str = Field(default="public")
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    settings: Optional[dict] = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^[a-z0-9][a-z0-9\-]{0,253}[a-z0-9]$", v):
            raise ValueError("Slug должен содержать только строчные буквы, цифры и дефисы")
        return v

    @field_validator("community_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("public", "private", "restricted"):
            raise ValueError("Тип должен быть public, private или restricted")
        return v


class CommunityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    community_type: Optional[str] = None
    status: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    settings: Optional[dict] = None


class CommunityResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str]
    community_type: str
    status: str
    owner_id: uuid.UUID
    avatar_url: Optional[str]
    banner_url: Optional[str]
    settings: Optional[dict]
    member_count: int
    post_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommunityListResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str]
    community_type: str
    status: str
    member_count: int
    post_count: int
    avatar_url: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
