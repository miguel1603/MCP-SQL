@echo off
setlocal enabledelayedexpansion

REM ------------------------------------------------------------
REM MCP SQL Server launcher (Windows)
REM - Crea entorno virtual si no existe
REM - Instala dependencias
REM - Levanta el servidor MCP
REM ------------------------------------------------------------

cd /d "%~dp0"

set "VENV_DIR=.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

echo [1/4] Verificando Python...
where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python no esta en PATH.
  echo Instala Python 3.11+ y marca "Add Python to PATH".
  pause
  exit /b 1
)

if not exist "%PYTHON_EXE%" (
  echo [2/4] Creando entorno virtual en %VENV_DIR%...
  python -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual.
    pause
    exit /b 1
  )
) else (
  echo [2/4] Entorno virtual ya existe.
)

echo [3/4] Instalando/actualizando dependencias...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
  echo ERROR: No se pudo actualizar pip.
  pause
  exit /b 1
)

"%PYTHON_EXE%" -m pip install -e .
if errorlevel 1 (
  echo ERROR: No se pudo instalar el proyecto.
  pause
  exit /b 1
)

echo [4/4] Iniciando MCP SQL Server...
echo Puedes cerrar esta ventana para detener el servidor.
"%PYTHON_EXE%" -m mcp_sql_server.server

set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
  echo.
  echo El servidor termino con codigo %EXIT_CODE%.
  pause
)

exit /b %EXIT_CODE%
