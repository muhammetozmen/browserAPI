@echo off
setlocal enabledelayedexpansion

echo =============================================
echo   Starting browserAPI Gateway (Windows)
echo =============================================

:: 1. Check if venv python exists
set VENV_PYTHON=.venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo [-] Error: Virtual environment python not found at %VENV_PYTHON%.
    echo     Please run install.bat first to set up the environment.
    
    :: Check if system python exists to help the user
    where python >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        echo [+] Found system python. You can set up the environment by running: install.bat
    ) else (
        echo [-] System Python was not found either. Please install Python 3.11+.
    )
    pause
    exit /b 1
fi

:: 2. Run the application
echo [+] Starting app with %VENV_PYTHON% src/main.py
"%VENV_PYTHON%" src/main.py
pause
