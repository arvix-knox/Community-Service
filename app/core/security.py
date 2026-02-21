"""JWT-валидация и контекст пользователя."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Optional

import jwt
from fastapi import Request

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class UserContext:
    """Контекст аутентифицированного пользователя."""
    user_id: uuid.UUID
    email: str = ""
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    is_superadmin: bool = False


def decode_jwt_token(token: str) -> dict:
    """Декодирование и валидация JWT-токена."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedException("Токен истёк") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedException(f"Невалидный токен: {str(exc)}") from exc


def extract_user_from_token(token: str) -> UserContext:
    """Извлечение контекста пользователя из JWT."""
    payload = decode_jwt_token(token)

    user_id_raw = payload.get("sub") or payload.get("user_id")
    if not user_id_raw:
        raise UnauthorizedException("В токене отсутствует user_id")

    try:
        user_id = uuid.UUID(str(user_id_raw))
    except ValueError as exc:
        raise UnauthorizedException("Невалидный user_id в токене") from exc

    return UserContext(
        user_id=user_id,
        email=payload.get("email", ""),
        roles=payload.get("roles", []),
        permissions=payload.get("permissions", []),
        is_superadmin=payload.get("is_superadmin", False),
    )


def get_current_user(request: Request) -> UserContext:
    """Получение текущего пользователя из request.state."""
    user: Optional[UserContext] = getattr(request.state, "user", None)
    if user is None:
        raise UnauthorizedException()
    return user


def get_optional_user(request: Request) -> Optional[UserContext]:
    """Получение пользователя без обязательной авторизации."""
    return getattr(request.state, "user", None)
