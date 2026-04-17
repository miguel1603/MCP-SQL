@echo off
setlocal enabledelayedexpansion

REM MCP-safe launcher (stdout reservado al protocolo JSON-RPC)
cd /d "%~dp0"

set "VENV_DIR=.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

>&2 echo [1/4] Verificando Python...
where python >nul 2>&1
if errorlevel 1 (
  >&2 echo ERROR: Python no esta en PATH. Instala Python 3.11+.
  exit /b 1
)

if not exist "%PYTHON_EXE%" (
  >&2 echo [2/4] Creando entorno virtual en %VENV_DIR%...
  python -m venv "%VENV_DIR%" 1>&2
  if errorlevel 1 (
    >&2 echo ERROR: No se pudo crear el entorno virtual.
    exit /b 1
  )
) else (
  >&2 echo [2/4] Entorno virtual ya existe.
)

>&2 echo [3/4] Instalando/actualizando dependencias...
"%PYTHON_EXE%" -m pip --disable-pip-version-check install --upgrade pip 1>&2
if errorlevel 1 (
  >&2 echo ERROR: No se pudo actualizar pip.
  exit /b 1
)

"%PYTHON_EXE%" -m pip --disable-pip-version-check install -e . 1>&2
if errorlevel 1 (
  >&2 echo ERROR: No se pudo instalar el proyecto.
  exit /b 1
)

>&2 echo [4/4] Iniciando MCP SQL Server...
"%PYTHON_EXE%" -m mcp_sql_server.server
exit /b %ERRORLEVEL%
