from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import sqlparse
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .config import QueryResult, ServerSettings

READ_STATEMENTS = {"SELECT", "WITH", "SHOW", "PRAGMA", "DESCRIBE", "EXPLAIN"}
DESTRUCTIVE_DDL = {"DROP", "TRUNCATE"}


@dataclass
class SQLService:
    settings: ServerSettings
    engine: Engine

    @classmethod
    def from_settings(cls, settings: ServerSettings) -> "SQLService":
        return cls(settings=settings, engine=create_engine(settings.sqlalchemy_database_url, future=True))

    def _first_keyword(self, statement: str) -> str:
        parsed = sqlparse.parse(statement)
        if not parsed:
            return "UNKNOWN"

        for token in parsed[0].flatten():
            value = token.value.strip().upper()
            if value:
                return value
        return "UNKNOWN"

    def run_statement(self, statement: str, params: dict[str, Any] | None = None) -> QueryResult:
        statement = statement.strip()
        if not statement:
            return QueryResult(ok=False, statement_type="UNKNOWN", message="Empty SQL statement")

        statement_type = self._first_keyword(statement)
        if not self.settings.allow_destructive_ddl and statement_type in DESTRUCTIVE_DDL:
            return QueryResult(
                ok=False,
                statement_type=statement_type,
                message=f"Statement '{statement_type}' is blocked. Set MCP_SQL_ALLOW_DESTRUCTIVE_DDL=true to allow it.",
            )

        try:
            with self.engine.begin() as conn:
                result = conn.execute(text(statement), params or {})
                if result.returns_rows:
                    rows = [dict(row._mapping) for row in result.fetchmany(self.settings.max_rows)]
                    columns = list(result.keys())
                    return QueryResult(
                        ok=True,
                        statement_type=statement_type,
                        rowcount=len(rows),
                        columns=columns,
                        rows=rows,
                        message=f"Returned up to {self.settings.max_rows} rows",
                    )

                return QueryResult(
                    ok=True,
                    statement_type=statement_type,
                    rowcount=result.rowcount,
                    message="Statement executed successfully",
                )
        except SQLAlchemyError as exc:
            return QueryResult(
                ok=False,
                statement_type=statement_type,
                message=str(exc.__class__.__name__) + ": " + str(exc),
            )

    def run_script(self, script: str) -> dict[str, Any]:
        statements = [s.strip() for s in sqlparse.split(script) if s.strip()]
        if not statements:
            return {"ok": False, "message": "No SQL statements found", "results": []}

        if len(statements) > self.settings.max_script_statements:
            return {
                "ok": False,
                "message": (
                    f"Script has {len(statements)} statements; max allowed is "
                    f"{self.settings.max_script_statements}."
                ),
                "results": [],
            }

        results: list[dict[str, Any]] = []
        ok = True
        for idx, stmt in enumerate(statements, start=1):
            result = self.run_statement(stmt)
            results.append({"index": idx, "sql": stmt, **result.model_dump()})
            if not result.ok:
                ok = False
                break

        return {
            "ok": ok,
            "count": len(results),
            "stopped_on_error": not ok,
            "results": results,
        }

    def list_tables(self) -> dict[str, Any]:
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            views = inspector.get_view_names()
            return {"ok": True, "tables": tables, "views": views}
        except SQLAlchemyError as exc:
            return {"ok": False, "message": str(exc)}

    def describe_table(self, table_name: str) -> dict[str, Any]:
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            pks = inspector.get_pk_constraint(table_name)
            fks = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            return {
                "ok": True,
                "table": table_name,
                "columns": columns,
                "primary_key": pks,
                "foreign_keys": fks,
                "indexes": indexes,
            }
        except SQLAlchemyError as exc:
            return {"ok": False, "table": table_name, "message": str(exc)}

    def capabilities(self) -> dict[str, Any]:
        return {
            "mode": "development",
            "database_url": self.settings.database_url,
            "sqlalchemy_database_url": self.settings.sqlalchemy_database_url,
            "allow_destructive_ddl": self.settings.allow_destructive_ddl,
            "max_rows": self.settings.max_rows,
            "max_script_statements": self.settings.max_script_statements,
            "supported_operations": {
                "DDL": ["CREATE", "ALTER", "DROP (optional)", "TRUNCATE (optional)"],
                "DML": ["INSERT", "UPDATE", "DELETE", "MERGE (database dependent)"],
                "QUERY": ["SELECT", "WITH", "SHOW", "DESCRIBE", "EXPLAIN"],
            },
        }
