from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    anon_key: str
    service_role_key: str
    bucket: str


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str = Field(default="sqlite:///./data.db", alias="DATABASE_URL")

    supabase_url: Optional[AnyHttpUrl] = Field(default=None, alias="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_bucket: str = Field(default="receipts", alias="SUPABASE_BUCKET")

    admin_token: str = Field(default="", alias="ADMIN_TOKEN")

    cors_origins: Optional[List[AnyHttpUrl]] = Field(default=None, alias="CORS_ORIGINS")
    allowed_origins: str = Field(default="", alias="ALLOWED_ORIGINS")

    tz: str = Field(default="America/Sao_Paulo", alias="TZ")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        env_ignore_empty=True,
    )

    def resolved_cors_origins(self) -> list[str]:
        """Return the list of origins allowed to access the API."""

        if self.cors_origins:
            return [str(origin) for origin in self.cors_origins]
        raw = self.allowed_origins.strip()
        if not raw:
            return []
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    def supabase_config(self) -> SupabaseConfig | None:
        """Return consolidated Supabase configuration when available."""

        if not self.supabase_url or not self.supabase_service_role_key:
            return None
        return SupabaseConfig(
            url=str(self.supabase_url).rstrip("/"),
            anon_key=self.supabase_anon_key or "",
            service_role_key=self.supabase_service_role_key,
            bucket=self.supabase_bucket or "receipts",
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
