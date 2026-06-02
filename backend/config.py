"""Centralized application configuration for BetavanX Phase 1."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _env_bool(name: str, default: str = "false") -> bool:
    value = os.getenv(name, default)
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _build_database_url() -> str:
    explicit = os.getenv("DATABASE_URL", "").strip()
    if explicit:
        return explicit

    host = os.getenv("DB_HOST", "localhost").strip()
    port = os.getenv("DB_PORT", "5432").strip()
    name = os.getenv("DB_NAME", "betavanx_dev").strip()
    user = os.getenv("DB_USER", "betavanx_app").strip()
    password = os.getenv("DB_PASSWORD", "").strip()

    if password:
        credentials = f"{user}:{password}"
    else:
        credentials = user

    return f"postgresql://{credentials}@{host}:{port}/{name}"


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from the environment."""

    database_url: str
    db_echo: bool
    app_env: str
    legacy_api_enabled: bool
    workforce_extension_enabled: bool


@lru_cache
def get_settings() -> Settings:
    """Return cached settings (loads .env once on first call)."""
    _load_dotenv()
    return Settings(
        database_url=_build_database_url(),
        db_echo=_env_bool("DB_ECHO", "false"),
        app_env=os.getenv("APP_ENV", "development").strip(),
        legacy_api_enabled=_env_bool("LEGACY_API_ENABLED", "false"),
        workforce_extension_enabled=_env_bool(
            "BETAVANX_ENABLE_WORKFORCE_EXTENSION",
            "false",
        ),
    )
