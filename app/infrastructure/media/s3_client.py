"""S3/MinIO клиент для работы с медиа-файлами."""
from __future__ import annotations
from typing import Optional, BinaryIO

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class S3Client:
    def __init__(self):
        self._session = None

    async def connect(self) -> None:
        try:
            import aioboto3
            self._session = aioboto3.Session()
            logger.info("S3 клиент инициализирован")
        except ImportError:
            logger.warning("aioboto3 не установлен, S3 клиент в stub-режиме")
            self._session = None

    async def disconnect(self) -> None:
        self._session = None

    async def upload_file(self, file_data: BinaryIO, key: str,
                          content_type: str = "application/octet-stream",
                          bucket: Optional[str] = None) -> str:
        target_bucket = bucket or settings.S3_BUCKET
        if not self._session:
            logger.debug(f"S3 stub: upload {key}")
            return f"{settings.S3_ENDPOINT}/{target_bucket}/{key}"

        async with self._session.client(
            "s3", endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        ) as client:
            await client.upload_fileobj(file_data, target_bucket, key,
                                        ExtraArgs={"ContentType": content_type})
            return f"{settings.S3_ENDPOINT}/{target_bucket}/{key}"

    async def delete_file(self, key: str, bucket: Optional[str] = None) -> None:
        target_bucket = bucket or settings.S3_BUCKET
        if not self._session:
            return
        async with self._session.client(
            "s3", endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        ) as client:
            await client.delete_object(Bucket=target_bucket, Key=key)

    async def generate_presigned_url(self, key: str, bucket: Optional[str] = None,
                                      expires_in: int = 3600) -> str:
        target_bucket = bucket or settings.S3_BUCKET
        if not self._session:
            return f"{settings.S3_ENDPOINT}/{target_bucket}/{key}?presigned=stub"
        async with self._session.client(
            "s3", endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        ) as client:
            url = await client.generate_presigned_url(
                "get_object", Params={"Bucket": target_bucket, "Key": key}, ExpiresIn=expires_in)
            return url
