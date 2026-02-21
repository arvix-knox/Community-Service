"""Конфигурация приложения из переменных окружения."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Общие
    APP_NAME: str = "community-service"
    APP_VERSION: str = "1.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    WORKERS_COUNT: int = 4

    # PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/community_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PREFIX: str = "community:"
    CACHE_DEFAULT_TTL: int = 300
    CACHE_ANALYTICS_TTL: int = 600

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    AUTH_SERVICE_URL: str = "http://auth-service:8001"

    # Event Broker
    EVENT_BROKER_TYPE: str = "kafka"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_PREFIX: str = "community"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    RABBITMQ_EXCHANGE: str = "community_events"

    # S3 / MinIO
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "community-media"
    S3_REGION: str = "us-east-1"

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # Пагинация
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()
