"""Схемы для Member."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MemberRoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    color: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MemberCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    nickname: Optional[str] = Field(None, max_length=100)


class MemberUpdate(BaseModel):
    status: Optional[str] = None
    nickname: Optional[str] = Field(None, max_length=100)
    role_ids: Optional[List[uuid.UUID]] = None


class MemberResponse(BaseModel):
    id: uuid.UUID
    community_id: uuid.UUID
    user_id: uuid.UUID
    status: str
    is_owner: bool
    nickname: Optional[str] = None
    joined_at: datetime
    last_active_at: Optional[datetime] = None
    roles: List[MemberRoleResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
