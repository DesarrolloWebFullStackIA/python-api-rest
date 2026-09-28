@echo off
setlocal enabledelayedexpansion

title VaporStore API - Quick Start

echo ======================================================================
echo           VaporStore Video Game REST API - Quick Start
echo ======================================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

:: 2. Check or create virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not detected. Creating .venv...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
)

:: 3. Activate virtual environment
call .\.venv\Scripts\activate.bat

:: 4. Verify/Install dependencies
echo [INFO] Verifying Python dependencies...
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies from requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies are up to date.

:: 5. Ensure .env file exists
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] .env not found. Copying .env.example to .env...
        copy ".env.example" ".env" >nul
        echo [OK] Created .env configuration.
    )
)

echo.
echo ======================================================================
echo   VaporStore API Server is starting!
echo.
echo   * Web Client UI:   http://127.0.0.1:8000/client/
echo   * Swagger UI Docs: http://127.0.0.1:8000/docs
echo   * ReDoc Specs:     http://127.0.0.1:8000/redoc
echo   * Health Check:    http://127.0.0.1:8000/api/v1/health
echo.
echo   Press CTRL+C in this window to stop the server at any time.
echo ======================================================================
echo.

:: 6. Launch default browser to Client application
start http://127.0.0.1:8000/client/

:: 7. Run Uvicorn server
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload

pause
