"""Centralized application configuration for BetavanX Phase 1."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

_DEFAULT_AUTH_SECRET = "dev-secret-change-me"


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _env_bool(name: str, default: str = "false") -> bool:
    value = os.getenv(name, default)
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_cors_origins(raw: str) -> list[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


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
    auth_secret: str
    cors_origins: tuple[str, ...]
    log_level: str
    log_json: bool
    slow_query_ms: int
    db_pool_size: int
    db_max_overflow: int


@lru_cache
def get_settings() -> Settings:
    """Return cached settings (loads .env once on first call)."""
    _load_dotenv()
    return Settings(
        database_url=_build_database_url(),
        db_echo=_env_bool("DB_ECHO", "false"),
        app_env=os.getenv("APP_ENV", "development").strip().lower(),
        legacy_api_enabled=_env_bool("LEGACY_API_ENABLED", "false"),
        workforce_extension_enabled=_env_bool(
            "BETAVANX_ENABLE_WORKFORCE_EXTENSION",
            "false",
        ),
        auth_secret=os.getenv("BETAVANX_AUTH_SECRET", _DEFAULT_AUTH_SECRET).strip(),
        cors_origins=tuple(
            _parse_cors_origins(
                os.getenv("BETAVANX_CORS_ORIGINS", "http://localhost:3000"),
            ),
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip(),
        log_json=_env_bool("LOG_JSON", "false"),
        slow_query_ms=int(os.getenv("SLOW_QUERY_MS", "500")),
        db_pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        db_max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
    )


def validate_environment_settings() -> None:
    """Fail fast when staging/production secrets are unsafe."""
    settings = get_settings()

    if settings.app_env in {"production", "staging"}:
        if settings.auth_secret == _DEFAULT_AUTH_SECRET:
            msg = (
                "BETAVANX_AUTH_SECRET must be set to a non-default value "
                f"when APP_ENV={settings.app_env}"
            )
            raise RuntimeError(msg)

        if "change_me" in settings.database_url.lower():
            msg = (
                "DATABASE_URL appears to use a placeholder password "
                f"for APP_ENV={settings.app_env}"
            )
            raise RuntimeError(msg)

    if settings.app_env == "production" and _env_bool("SKIP_STARTUP_VALIDATION"):
        raise RuntimeError(
            "SKIP_STARTUP_VALIDATION must not be enabled in production",
        )
