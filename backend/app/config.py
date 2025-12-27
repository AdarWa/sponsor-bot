"""Application settings and configuration helpers."""
from functools import lru_cache
from pathlib import Path
from ssl import create_default_context
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration pulled from environment variables when available."""

    app_name: str = "Sponsor Bot"
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 60 * 24
    database_url: Optional[str] = None
    front_end_dist: str = "frontend/dist"
    scrape_api_base_url: str = "http://localhost:7071/api"
    scrape_api_key: str = ""

    # Azure Database for PostgreSQL specific overrides
    azure_pg_host: Optional[str] = None
    azure_pg_user: Optional[str] = None
    azure_pg_password: Optional[str] = None
    azure_pg_database: Optional[str] = None
    azure_pg_require_ssl: bool = True
    azure_pg_ssl_cert: Optional[Path] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    # --------------------------------------------------------------------- #
    # Database helpers
    # --------------------------------------------------------------------- #
    def _build_azure_database_url(self) -> Optional[str]:
        """Assemble an Azure PostgreSQL DSN when individual env vars are set."""

        if not all([self.azure_pg_host, self.azure_pg_user, self.azure_pg_password, self.azure_pg_database]):
            return None
        return (
            "postgresql+asyncpg://"
            f"{self.azure_pg_user}:{self.azure_pg_password}"
            f"@{self.azure_pg_host}/{self.azure_pg_database}"
        )

    @property
    def resolved_database_url(self) -> str:
        """Connection string used by SQLAlchemy."""

        return self.database_url or self._build_azure_database_url() or "sqlite+aiosqlite:///./app.db"

    def sqlalchemy_connect_args(self) -> dict[str, object]:
        """Provide SSL connect args for Azure PostgreSQL when required."""

        if not self.resolved_database_url.startswith("postgresql"):
            return {}

        if not self.azure_pg_require_ssl:
            return {}

        ssl_context = (
            create_default_context(cafile=str(self.azure_pg_ssl_cert)) if self.azure_pg_ssl_cert else create_default_context()
        )
        return {"ssl": ssl_context}


@lru_cache
def get_settings() -> "Settings":
    """Return a cached Settings instance."""

    return Settings()
