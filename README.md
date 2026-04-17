# MCP SQL Server (Desarrollo)

Servidor **MCP profesional** para conectar cualquier LLM compatible con MCP a una base de datos SQL y ejecutar:

- **Consultas** (`SELECT`, `WITH`, `SHOW`, etc.)
- **DML** (`INSERT`, `UPDATE`, `DELETE`)
- **DDL** (`CREATE`, `ALTER`, y opcionalmente `DROP`/`TRUNCATE`)

> Este servidor está diseñado para **uso personal en desarrollo asistido**.

## Características

- Protocolo MCP vía stdio (compatible con clientes MCP).
- Conexión multi-motor mediante `SQLAlchemy` (`sqlite`, `postgresql`, `mysql`, `mssql`, etc.).
- Herramientas MCP enfocadas en operación diaria:
  - `sql_capabilities`
  - `sql_list_tables`
  - `sql_describe_table`
  - `sql_run`
  - `sql_run_script`
- Bloqueo de DDL destructivo por defecto (`DROP`/`TRUNCATE` bloqueados).
- Límite configurable de filas y de sentencias por script.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuración (variables de entorno)

Prefijo: `MCP_SQL_`

- `MCP_SQL_DATABASE_URL`: URL SQLAlchemy **o** connection string SQL Server estilo ADO/ODBC. Default: `sqlite:///./dev.db`
- `MCP_SQL_MAX_ROWS`: máximo de filas devueltas por consulta. Default: `200`
- `MCP_SQL_MAX_SCRIPT_STATEMENTS`: máximo de sentencias por script. Default: `100`
- `MCP_SQL_ALLOW_DESTRUCTIVE_DDL`: `true/false` para permitir `DROP` y `TRUNCATE`. Default: `false`

### Ejemplo

```bash
export MCP_SQL_DATABASE_URL='postgresql+psycopg://dev_user:dev_pass@localhost:5432/devdb'
export MCP_SQL_MAX_ROWS=500
export MCP_SQL_ALLOW_DESTRUCTIVE_DDL=false
```


### Azure SQL / SQL Server

Si pasas una cadena tipo `Server=...;Database=...;User ID=...;Password=...;` el servidor la convierte automáticamente a URL de SQLAlchemy (`mssql+pyodbc:///?odbc_connect=...`).

También puedes pasar directamente la URL SQLAlchemy:

```bash
export MCP_SQL_DATABASE_URL='mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+18+for+SQL+Server%7D%3BSERVER%3Dmi-servidor.database.windows.net%2C1433%3BDATABASE%3Dmi_db%3BUID%3Dmi_usuario%3BPWD%3Dmi_password%3BEncrypt%3Dyes%3BTrustServerCertificate%3Dno%3B'
```

## Ejecutar el servidor

```bash
mcp-sql-server
```

También puedes ejecutarlo como módulo:

```bash
python -m mcp_sql_server.server
```


## Inicio con doble click en Windows

Se incluye el archivo `start_mcp_sql_server.bat` para facilitar el arranque:

1. Crea `.venv` automáticamente (si no existe).
2. Instala/actualiza dependencias.
3. Levanta el servidor MCP.

Solo haz doble click en ese `.bat`.

## Configuración en un cliente MCP (ejemplo genérico)

```json
{
  "mcpServers": {
    "sql-dev": {
      "command": "mcp-sql-server",
      "env": {
        "MCP_SQL_DATABASE_URL": "sqlite:///./dev.db",
        "MCP_SQL_MAX_ROWS": "200",
        "MCP_SQL_ALLOW_DESTRUCTIVE_DDL": "false"
      }
    }
  }
}
```

## Flujo recomendado

1. `sql_capabilities` para verificar configuración activa.
2. `sql_list_tables` para explorar el esquema.
3. `sql_describe_table` para inspeccionar metadatos.
4. `sql_run` para consultas o DML puntual.
5. `sql_run_script` para lotes de cambios controlados.

## Buenas prácticas para desarrollo asistido

- Usa usuarios de base de datos con privilegios mínimos.
- Trabaja sobre una DB local de desarrollo o snapshot desechable.
- Mantén `MCP_SQL_ALLOW_DESTRUCTIVE_DDL=false` por defecto.
- Versiona cambios estructurales con migraciones.

## Nota de seguridad

Este proyecto **no** está endurecido para producción. Está orientado a productividad local en entornos de desarrollo.


## Guía Claude en VS Code

Revisa `README_CLAUDE_VSCODE.md` para un ejemplo completo de configuración y uso.
