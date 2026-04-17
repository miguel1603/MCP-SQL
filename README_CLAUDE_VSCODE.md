# Uso desde Claude en VS Code (MCP SQL Server)

Este documento muestra una configuración **rápida** para usar este servidor MCP desde un cliente/extension de Claude en VS Code que soporte la clave `mcpServers`.

> Si tu extension usa otro archivo o nombre de clave, copia la misma estructura y ajusta la ruta.

## 1) Arranque con doble click (Windows)

1. Haz doble click en `start_mcp_sql_server.bat`.
2. El script automáticamente:
   - crea `.venv` (si no existe),
   - instala dependencias,
   - levanta el servidor MCP.

## 2) Configura Claude en VS Code

Ejemplo de configuración JSON (ajusta rutas):

```json
{
  "mcpServers": {
    "sql-dev": {
      "command": "C:\\ruta\\a\\tu\\repo\\start_mcp_sql_server.bat",
      "env": {
        "MCP_SQL_DATABASE_URL": "sqlite:///./dev.db",
        "MCP_SQL_MAX_ROWS": "200",
        "MCP_SQL_MAX_SCRIPT_STATEMENTS": "100",
        "MCP_SQL_ALLOW_DESTRUCTIVE_DDL": "false"
      }
    }
  }
}
```



### Importante sobre `MCP_SQL_DATABASE_URL`

Tu valor puede ser:

1. URL SQLAlchemy (recomendado), por ejemplo:
   `mssql+pyodbc:///?odbc_connect=...`
2. O una cadena SQL Server tipo ADO/ODBC:
   `Server=tcp:...;Database=...;User ID=...;Password=...;Encrypt=True;TrustServerCertificate=False;`

Este servidor ahora acepta ambos formatos.

## 3) Prompt de prueba en Claude

Puedes probar con algo como:

- "Ejecuta `sql_capabilities` para validar el servidor"
- "Lista tablas con `sql_list_tables`"
- "Crea tabla de prueba y luego inserta registros usando `sql_run`"

## 4) Ejemplo de flujo SQL

1. `sql_run`:
   ```sql
   CREATE TABLE IF NOT EXISTS usuarios (
     id INTEGER PRIMARY KEY,
     nombre TEXT NOT NULL,
     email TEXT UNIQUE
   );
   ```
2. `sql_run`:
   ```sql
   INSERT INTO usuarios (nombre, email)
   VALUES (:nombre, :email);
   ```
   Params:
   ```json
   {"nombre":"Ana","email":"ana@example.com"}
   ```
3. `sql_run`:
   ```sql
   SELECT * FROM usuarios;
   ```

## 5) Recomendaciones

- Usa una base de datos de desarrollo o desechable.
- Mantén `MCP_SQL_ALLOW_DESTRUCTIVE_DDL=false` por defecto.
- No uses esta configuración directa para producción.
