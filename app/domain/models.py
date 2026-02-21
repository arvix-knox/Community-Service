"""SQLAlchemy 2.0 модели."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовая модель."""
    pass


class TimestampMixin:
    """Миксин для временных меток."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# Ассоциация Роли — Участники (M2M)
member_roles = Table(
    "member_roles",
    Base.metadata,
    Column("member_id", PGUUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", PGUUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Community(Base, TimestampMixin):
    __tablename__ = "communities"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    community_type: Mapped[str] = mapped_column(
        SAEnum("public", "private", "restricted", name="community_type_enum", create_constraint=False),
        default="public",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        SAEnum("active", "suspended", "archived", name="community_status_enum", create_constraint=False),
        default="active",
        nullable=False,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    banner_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    member_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    post_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    members: Mapped[List["Member"]] = relationship("Member", back_populates="community", lazy="selectin", cascade="all, delete-orphan")
    roles: Mapped[List["Role"]] = relationship("Role", back_populates="community", lazy="selectin", cascade="all, delete-orphan")
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="community", lazy="noload", cascade="all, delete-orphan")
    channels: Mapped[List["Channel"]] = relationship("Channel", back_populates="community", lazy="selectin", cascade="all, delete-orphan")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="community", lazy="noload", cascade="all, delete-orphan")
    subscription_levels: Mapped[List["SubscriptionLevel"]] = relationship("SubscriptionLevel", back_populates="community", lazy="selectin", cascade="all, delete-orphan")
    donations: Mapped[List["Donation"]] = relationship("Donation", back_populates="community", lazy="noload", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_communities_status", "status"),
        Index("idx_communities_type_status", "community_type", "status"),
    )


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    permissions_list: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True, default=list)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    community: Mapped["Community"] = relationship("Community", back_populates="roles")
    members: Mapped[List["Member"]] = relationship("Member", secondary=member_roles, back_populates="roles")

    __table_args__ = (
        UniqueConstraint("community_id", "name", name="uq_role_community_name"),
        Index("idx_roles_community", "community_id"),
    )


class Member(Base, TimestampMixin):
    __tablename__ = "members"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        SAEnum("active", "banned", "muted", "pending", name="member_status_enum", create_constraint=False),
        default="active",
        nullable=False,
    )
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    community: Mapped["Community"] = relationship("Community", back_populates="members")
    roles: Mapped[List["Role"]] = relationship("Role", secondary=member_roles, back_populates="members", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("community_id", "user_id", name="uq_member_community_user"),
        Index("idx_members_community_status", "community_id", "status"),
        Index("idx_members_user", "user_id"),
    )


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("channels.id", ondelete="SET NULL"), nullable=True)
    author_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum("draft", "published", "archived", "moderated", name="post_status_enum", create_constraint=False),
        default="published",
        nullable=False,
    )
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    media_urls: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True, default=list)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    community: Mapped["Community"] = relationship("Community", back_populates="posts")
    channel: Mapped[Optional["Channel"]] = relationship("Channel", back_populates="posts")

    __table_args__ = (
        Index("idx_posts_community_status", "community_id", "status"),
        Index("idx_posts_author", "author_id"),
        Index("idx_posts_published", "published_at"),
        Index("idx_posts_community_pinned", "community_id", "is_pinned"),
    )


class Channel(Base, TimestampMixin):
    __tablename__ = "channels"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    channel_type: Mapped[str] = mapped_column(
        SAEnum("text", "announcement", "media", "forum", name="channel_type_enum", create_constraint=False),
        default="text",
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    community: Mapped["Community"] = relationship("Community", back_populates="channels")
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="channel", lazy="noload")

    __table_args__ = (
        UniqueConstraint("community_id", "name", name="uq_channel_community_name"),
        Index("idx_channels_community", "community_id"),
    )


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum("scheduled", "active", "completed", "cancelled", name="event_status_enum", create_constraint=False),
        default="scheduled",
        nullable=False,
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    online_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    max_attendees: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    attendee_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cover_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True, default=dict)

    community: Mapped["Community"] = relationship("Community", back_populates="events")

    __table_args__ = (
        Index("idx_events_community_status", "community_id", "status"),
        Index("idx_events_starts_at", "starts_at"),
    )


class SubscriptionLevel(Base, TimestampMixin):
    __tablename__ = "subscription_levels"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_subscribers: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    subscriber_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    community: Mapped["Community"] = relationship("Community", back_populates="subscription_levels")
    subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="level", lazy="noload")

    __table_args__ = (
        Index("idx_sub_levels_community", "community_id"),
        UniqueConstraint("community_id", "name", name="uq_sub_level_community_name"),
    )


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("subscription_levels.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    community_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum("active", "expired", "cancelled", name="subscription_status_enum", create_constraint=False),
        default="active",
        nullable=False,
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    level: Mapped["SubscriptionLevel"] = relationship("SubscriptionLevel", back_populates="subscriptions")
    community: Mapped["Community"] = relationship("Community")

    __table_args__ = (
        Index("idx_subscriptions_user", "user_id"),
        Index("idx_subscriptions_community", "community_id"),
        Index("idx_subscriptions_expires", "expires_at"),
    )


class Donation(Base, TimestampMixin):
    __tablename__ = "donations"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False)
    donor_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum("pending", "completed", "failed", "refunded", name="donation_status_enum", create_constraint=False),
        default="completed",
        nullable=False,
    )
    transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    community: Mapped["Community"] = relationship("Community", back_populates="donations")

    __table_args__ = (
        Index("idx_donations_community", "community_id"),
        Index("idx_donations_donor", "donor_id"),
        Index("idx_donations_status", "status"),
    )
