"""Главный роутер API v1."""
from fastapi import APIRouter

from app.api.v1 import communities, members, roles, posts, channels, events, subscriptions, donations, analytics

api_router = APIRouter()

api_router.include_router(communities.router, prefix="/communities", tags=["Communities"])
api_router.include_router(members.router, tags=["Members"])
api_router.include_router(roles.router, tags=["Roles"])
api_router.include_router(posts.router, tags=["Posts"])
api_router.include_router(channels.router, tags=["Channels"])
api_router.include_router(events.router, tags=["Events"])
api_router.include_router(subscriptions.router, tags=["Subscriptions"])
api_router.include_router(donations.router, tags=["Donations"])
api_router.include_router(analytics.router, tags=["Analytics"])
