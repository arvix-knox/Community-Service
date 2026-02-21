"""Централизованная обработка ошибок."""
from __future__ import annotations
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Базовое исключение приложения."""

    def __init__(
        self,
        message: str = "Internal server error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, entity: str = "Resource", entity_id: Any = None):
        msg = f"{entity} не найден"
        if entity_id:
            msg = f"{entity} с id={entity_id} не найден"
        super().__init__(message=msg, status_code=status.HTTP_404_NOT_FOUND)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Недостаточно прав"):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class ConflictException(AppException):
    def __init__(self, message: str = "Конфликт данных"):
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


class ValidationException(AppException):
    def __init__(self, message: str = "Ошибка валидации", detail: Any = None):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Не авторизован"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация обработчиков исключений."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        error_id = str(uuid.uuid4())
        logger.error(
            exc.message,
            extra={"error_id": error_id, "status_code": exc.status_code, "path": str(request.url)},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "id": error_id,
                    "message": exc.message,
                    "detail": exc.detail,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        error_id = str(uuid.uuid4())
        logger.exception(
            "Непредвиденная ошибка",
            extra={"error_id": error_id, "path": str(request.url)},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "id": error_id,
                    "message": "Internal server error",
                }
            },
        )
