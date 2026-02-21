"""Схемы для Role."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    permissions_list: Optional[List[str]] = None
    is_default: bool = False
    priority: int = 0


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    permissions_list: Optional[List[str]] = None
    is_default: Optional[bool] = None
    priority: Optional[int] = None


class RoleResponse(BaseModel):
    id: uuid.UUID
    community_id: uuid.UUID
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    permissions_list: Optional[List[str]] = None
    is_default: bool
    priority: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
