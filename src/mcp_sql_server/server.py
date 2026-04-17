from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import ServerSettings
from .db import SQLService

settings = ServerSettings()
service = SQLService.from_settings(settings)

mcp = FastMCP(
    "mcp-sql-server",
    instructions=(
        "Servidor MCP para desarrollo asistido con SQL. "
        "Permite consultas, DML y DDL controlado sobre una conexión SQLAlchemy."
    ),
)


@mcp.tool()
def sql_capabilities() -> dict[str, Any]:
    """Describe la configuración activa y operaciones soportadas."""

    return service.capabilities()


@mcp.tool()
def sql_list_tables() -> dict[str, Any]:
    """Lista tablas y vistas disponibles en el esquema actual."""

    return service.list_tables()


@mcp.tool()
def sql_describe_table(table_name: str) -> dict[str, Any]:
    """Describe columnas, PK, FK e índices de una tabla."""

    return service.describe_table(table_name)


@mcp.tool()
def sql_run(statement: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Ejecuta una sentencia SQL individual usando parámetros nombrados opcionales."""

    return service.run_statement(statement, params).model_dump()


@mcp.tool()
def sql_run_script(script: str) -> dict[str, Any]:
    """Ejecuta múltiples sentencias SQL en secuencia; se detiene al primer error."""

    return service.run_script(script)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
