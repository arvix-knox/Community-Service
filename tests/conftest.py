"""Фикстуры для тестов."""
from __future__ import annotations
import os
import uuid
from pathlib import Path
from typing import Generator

from app.core.bootstrap import add_local_venv_site_packages

add_local_venv_site_packages(project_root=Path(__file__).resolve().parents[1])

import pytest
from fastapi.testclient import TestClient


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


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    os.environ["DEBUG"] = "false"
    from main import app
    with TestClient(app) as tc:
        yield tc


@pytest.fixture
def auth_client() -> Generator[TestClient, None, None]:
    os.environ["DEBUG"] = "false"
    from main import app
    token = create_test_token()
    with TestClient(app) as tc:
        tc.headers.update({"Authorization": f"Bearer {token}"})
        yield tc
