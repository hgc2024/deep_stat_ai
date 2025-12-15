@echo off
echo ==================================================
echo   🏀 Deep Stat AI: Launching System
echo ==================================================

:: 1. Start Backend (API)
start "Deep Stat API (Port 8000)" cmd /k "venv\Scripts\activate && python api.py"

:: 2. Start Frontend (React)
:: Check if node_modules exists, if not run install
if exist "client\package.json" (
    cd client
    if not exist "node_modules" (
        echo [INFO] Installing Frontend Dependencies...
        call npm install
    )
    start "Deep Stat UI" cmd /k "npm run dev"
    cd ..
) else (
    echo [WARNING] 'client' folder not found. Running API Only.
)

echo.
echo [INFO] API running at http://localhost:8000
echo [INFO] UI running at http://localhost:5173
echo.
pause
