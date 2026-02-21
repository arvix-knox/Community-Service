"""Схемы аналитики."""
from __future__ import annotations
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class DonorInfo(BaseModel):
    user_id: str
    total_amount: Decimal
    donation_count: int


class CommunityAnalytics(BaseModel):
    total_members: int
    active_members: int
    total_posts: int
    total_events: int
    total_donations: Decimal
    total_subscriptions: int
    member_growth_7d: int
    post_growth_7d: int
    top_donors: List[DonorInfo] = []
    engagement_rate: float


class PostAnalytics(BaseModel):
    view_count: int
    like_count: int
    comment_count: int
    engagement_rate: float
    unique_viewers: int


class MemberAnalytics(BaseModel):
    communities_count: int
    total_posts: int
    total_donations: Decimal
    joined_since: Optional[str] = None
    activity_score: float
