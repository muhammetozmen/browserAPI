@echo off
setlocal enabledelayedexpansion

echo =============================================
echo   browserAPI Installer (Windows)
echo =============================================

:: 1. Check if python exists
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [-] Error: Python is not installed or not in PATH.
    echo     Please install Python 3.11+ and try again.
    exit /b 1
)

:: 2. Check Python version (requires 3.11+)
for /f "tokens=*" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%i

for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set major=%%a
    set minor=%%b
)

if !major! LSS 3 (
    echo [-] Error: Python 3.11 or higher is required. Found Python %PYTHON_VERSION%
    exit /b 1
)
if !major! EQU 3 (
    if !minor! LSS 11 (
        echo [-] Error: Python 3.11 or higher is required. Found Python %PYTHON_VERSION%
        exit /b 1
    )
)

echo [+] Using Python %PYTHON_VERSION%

:: 3. Create virtual environment if it does not exist
if not exist .venv (
    echo [+] Creating virtual environment '.venv'...
    python -m venv .venv
) else (
    echo [+] Virtual environment '.venv' already exists.
)

:: 4. Verify virtual environment python and pip
set PYTHON_VENV=.venv\Scripts\python.exe
set PIP_VENV=.venv\Scripts\pip.exe

if not exist "%PYTHON_VENV%" (
    echo [-] Error: Virtual environment python.exe not found at %PYTHON_VENV%.
    exit /b 1
)

:: 5. Install dependencies
echo [+] Upgrading pip inside virtual environment...
"%PYTHON_VENV%" -m pip install --upgrade pip

echo [+] Installing requirements...
"%PIP_VENV%" install -r requirements.txt

echo =============================================
echo   Installation Completed successfully.
echo   To run the app:
echo     win_run.bat
echo =============================================
pause
