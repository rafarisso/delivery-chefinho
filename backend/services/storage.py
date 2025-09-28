"""Supabase storage service integration."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import BinaryIO

import httpx
from fastapi import Depends
from httpx import HTTPStatusError, RequestError

from settings import Settings, get_settings


class StorageService:
    """Wrapper for Supabase Storage interactions."""

    def __init__(self, supabase_url: str, service_role_key: str, bucket: str = "receipts") -> None:
        self.supabase_url = supabase_url.rstrip("/")
        self.service_role_key = service_role_key
        self.bucket = bucket

    def upload_receipt(self, file_obj: BinaryIO, destination: Path, content_type: str | None = None) -> str:
        """Upload a receipt to Supabase Storage and return the public URL."""

        path = destination.as_posix()
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{path}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": content_type or "application/octet-stream",
        }
        data = file_obj.read()

        try:
            with httpx.Client(timeout=30) as client:
                response = client.put(url, content=data, headers=headers)
                response.raise_for_status()
        except (HTTPStatusError, RequestError) as exc:
            raise RuntimeError("Failed to upload receipt to Supabase") from exc

        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{path}"


@lru_cache
def _storage_service_factory(supabase_url: str, service_role_key: str, bucket: str = "receipts") -> StorageService:
    """Cache StorageService instances by credentials."""

    return StorageService(supabase_url, service_role_key, bucket=bucket)


def get_storage_service(settings: Settings = Depends(get_settings)) -> StorageService:
    """Return a cached storage service instance."""

    config = settings.supabase_config()
    if not config:
        raise RuntimeError("Supabase storage is not configured")

    return _storage_service_factory(config.url, config.service_role_key, bucket=config.bucket)
