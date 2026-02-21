"""Ключи кэша Redis."""
from app.core.config import settings

PREFIX = settings.REDIS_PREFIX


class CacheKeys:
    @staticmethod
    def community(community_id: str) -> str:
        return f"{PREFIX}community:{community_id}"

    @staticmethod
    def community_list(page: int, page_size: int, filters_hash: str = "") -> str:
        return f"{PREFIX}communities:list:{page}:{page_size}:{filters_hash}"

    @staticmethod
    def popular_communities() -> str:
        return f"{PREFIX}communities:popular"

    @staticmethod
    def community_members(community_id: str, page: int) -> str:
        return f"{PREFIX}community:{community_id}:members:{page}"

    @staticmethod
    def community_posts(community_id: str, page: int) -> str:
        return f"{PREFIX}community:{community_id}:posts:{page}"

    @staticmethod
    def community_analytics(community_id: str) -> str:
        return f"{PREFIX}community:{community_id}:analytics"

    @staticmethod
    def post_analytics(post_id: str) -> str:
        return f"{PREFIX}post:{post_id}:analytics"

    @staticmethod
    def member_analytics(member_id: str) -> str:
        return f"{PREFIX}member:{member_id}:analytics"

    @staticmethod
    def top_donors(community_id: str) -> str:
        return f"{PREFIX}community:{community_id}:top_donors"

    @staticmethod
    def community_roles(community_id: str) -> str:
        return f"{PREFIX}community:{community_id}:roles"

    @staticmethod
    def invalidation_pattern(community_id: str) -> str:
        return f"{PREFIX}community:{community_id}:*"
