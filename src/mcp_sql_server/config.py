from __future__ import annotations

from urllib.parse import quote_plus

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(raw_value: str) -> str:
    """Normalize input into a SQLAlchemy URL.

    Supports:
    - native SQLAlchemy URLs (sqlite://, postgresql+..., mssql+...)
    - SQL Server connection strings in ADO/ODBC style:
      "Server=...;Database=...;User ID=...;Password=...;Encrypt=True;..."
    """

    value = (raw_value or "").strip()
    if not value:
        raise ValueError("MCP_SQL_DATABASE_URL is empty")

    if "://" in value:
        return value

    parts: dict[str, str] = {}
    for item in value.split(";"):
        item = item.strip()
        if not item or "=" not in item:
            continue
        k, v = item.split("=", 1)
        parts[k.strip().lower()] = v.strip()

    if "server" not in parts:
        return value

    server = parts.get("server", "")
    if server.lower().startswith("tcp:"):
        server = server[4:]

    driver = parts.get("driver", "ODBC Driver 18 for SQL Server")
    odbc_parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
    ]

    database = parts.get("database")
    if database:
        odbc_parts.append(f"DATABASE={database}")

    user = parts.get("user id") or parts.get("uid") or parts.get("user")
    password = parts.get("password") or parts.get("pwd")
    if user:
        odbc_parts.append(f"UID={user}")
    if password:
        odbc_parts.append(f"PWD={password}")

    for key in ("encrypt", "trustservercertificate", "connection timeout", "timeout"):
        if key in parts:
            normalized_key = {
                "encrypt": "Encrypt",
                "trustservercertificate": "TrustServerCertificate",
                "connection timeout": "Connection Timeout",
                "timeout": "Connection Timeout",
            }[key]
            odbc_parts.append(f"{normalized_key}={parts[key]}")

    odbc_connection = ";".join(odbc_parts) + ";"
    return f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_connection)}"


class ServerSettings(BaseSettings):
    """Settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="MCP_SQL_", case_sensitive=False)

    database_url: str = Field(
        default="sqlite:///./dev.db",
        description="SQLAlchemy database URL or SQL Server ADO/ODBC connection string",
    )
    max_rows: int = Field(default=200, ge=1, le=5000)
    max_script_statements: int = Field(default=100, ge=1, le=500)
    allow_destructive_ddl: bool = Field(default=False)

    @property
    def sqlalchemy_database_url(self) -> str:
        return normalize_database_url(self.database_url)


class QueryResult(BaseModel):
    ok: bool
    statement_type: str
    rowcount: int | None = None
    columns: list[str] = Field(default_factory=list)
    rows: list[dict] = Field(default_factory=list)
    message: str | None = None
