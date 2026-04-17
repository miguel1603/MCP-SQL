from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    """Settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="MCP_SQL_", case_sensitive=False)

    database_url: str = Field(
        default="sqlite:///./dev.db",
        description="SQLAlchemy database URL",
    )
    max_rows: int = Field(default=200, ge=1, le=5000)
    max_script_statements: int = Field(default=100, ge=1, le=500)
    allow_destructive_ddl: bool = Field(default=False)


class QueryResult(BaseModel):
    ok: bool
    statement_type: str
    rowcount: int | None = None
    columns: list[str] = Field(default_factory=list)
    rows: list[dict] = Field(default_factory=list)
    message: str | None = None
