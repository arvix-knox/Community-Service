"""Фикстуры для тестов."""
from __future__ import annotations
import uuid
from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport


def create_test_token(user_id=None, is_superadmin=False):
    import jwt
    from app.core.config import settings
    payload = {
        "sub": str(user_id or uuid.uuid4()),
        "email": "test@example.com",
        "roles": ["admin"],
        "permissions": [],
        "is_superadmin": is_superadmin,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    from main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client() -> AsyncGenerator[AsyncClient, None]:
    from main import app
    token = create_test_token()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test",
                            headers={"Authorization": f"Bearer {token}"}) as ac:
        yield ac
