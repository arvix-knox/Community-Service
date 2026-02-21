"""Типы событий для event publishing."""
from enum import Enum


class EventType(str, Enum):
    COMMUNITY_CREATED = "community.created"
    COMMUNITY_UPDATED = "community.updated"
    COMMUNITY_DELETED = "community.deleted"
    MEMBER_JOINED = "member.joined"
    MEMBER_LEFT = "member.left"
    POST_CREATED = "post.created"
    POST_UPDATED = "post.updated"
    POST_DELETED = "post.deleted"
    DONATION_RECEIVED = "donation.received"
    SUBSCRIPTION_STARTED = "subscription.started"
    SUBSCRIPTION_ENDED = "subscription.ended"
    EVENT_CREATED = "event.created"
    EVENT_UPDATED = "event.updated"
    EVENT_DELETED = "event.deleted"
