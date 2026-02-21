"""Перечисления доменной области."""
import enum


class CommunityType(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"


class CommunityStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class MemberStatus(str, enum.Enum):
    ACTIVE = "active"
    BANNED = "banned"
    MUTED = "muted"
    PENDING = "pending"


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    MODERATED = "moderated"


class ChannelType(str, enum.Enum):
    TEXT = "text"
    ANNOUNCEMENT = "announcement"
    MEDIA = "media"
    FORUM = "forum"


class EventStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DonationStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
