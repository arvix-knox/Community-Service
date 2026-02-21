"""Community Service — точка входа."""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.middleware import JWTMiddleware, RequestLoggingMiddleware
from app.api.v1.router import api_router
from app.infrastructure.container import Container
from app.core.exceptions import register_exception_handlers

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Жизненный цикл приложения."""
    setup_logging()
    logger.info("Запуск Community Service", extra={"version": settings.APP_VERSION})

    container = Container()
    await container.init_resources()
    application.state.container = container

    yield

    logger.info("Остановка Community Service")
    await container.shutdown_resources()


def create_application() -> FastAPI:
    """Фабрика приложения."""
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(JWTMiddleware)

    application.include_router(api_router, prefix="/api/v1")

    register_exception_handlers(application)

    return application


app = create_application()


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS_COUNT,
        log_level="info",
    )
