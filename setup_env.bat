@echo off
setlocal

echo ==================================================
echo   🏀 Deep Stat AI: Environment Setup
echo ==================================================

:: 1. Find Python 3.10
set "PYTHON_CMD=python"
if exist "C:\Users\henry-cao-local\AppData\Local\Programs\Python\Python310\python.exe" (
    set "PYTHON_CMD=C:\Users\henry-cao-local\AppData\Local\Programs\Python\Python310\python.exe"
    echo [INFO] Found Python 3.10 at specific path.
) else (
    echo [INFO] Using system default python.
)

:: 2. Create Virtual Environment
if not exist "venv" (
    echo [INFO] Creating venv...
    "%PYTHON_CMD%" -m venv venv
) else (
    echo [INFO] venv already exists.
)

:: 3. Install Dependencies
echo [INFO] Installing requirements...
call venv\Scripts\activate
pip install duckdb chromadb pandas sentence-transformers langchain langchain-community langchain-core langchain-ollama fastapi uvicorn tabulate
if %errorlevel% neq 0 (
    echo [ERROR] Dependency installation failed!
    pause
    exit /b %errorlevel%
)

:: 4. Initialize Database
if not exist "nba.duckdb" (
    echo [INFO] Initializing Database (DuckDB + Chroma)...
    echo      (This may take a minute to load CSVs)
    python utils/init_db.py
) else (
    echo [INFO] Database already exists.
)

echo.
echo [SUCCESS] Environment Ready!
echo Use start_app.bat to launch.
echo.
pause
