#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "============================================="
echo "  browserAPI Installer"
echo "============================================="

# 1. Check if python exists
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[-] Error: Python is not installed or not in PATH."
    echo "    Please install Python 3.11+ and try again."
    exit 1
fi

# 2. Check Python version (requires 3.11+)
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
IFS='.' read -r major minor <<< "$PYTHON_VERSION"

if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 11 ]; }; then
    echo "[-] Error: Python 3.11 or higher is required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "[+] Using Python $PYTHON_VERSION ($PYTHON_CMD)"

# 3. Create virtual environment if it does not exist
if [ ! -d ".venv" ]; then
    echo "[+] Creating virtual environment '.venv'..."
    $PYTHON_CMD -m venv .venv
else
    echo "[+] Virtual environment '.venv' already exists."
fi

# 4. Determine paths based on OS
OS_NAME=$(uname -s)
if [[ "$OS_NAME" == *"NT"* ]] || [[ "$OS_NAME" == *"MINGW"* ]] || [[ "$OS_NAME" == *"MSYS"* ]] || [[ "$OS_NAME" == *"CYGWIN"* ]]; then
    PIP_PATH=".venv/Scripts/pip"
    PYTHON_VENV_PATH=".venv/Scripts/python"
else
    PIP_PATH=".venv/bin/pip"
    PYTHON_VENV_PATH=".venv/bin/python"
fi

# Double check if pip path exists, otherwise try standard fallback
if [ ! -f "$PIP_PATH" ]; then
    if [ -f ".venv/bin/pip" ]; then
        PIP_PATH=".venv/bin/pip"
        PYTHON_VENV_PATH=".venv/bin/python"
    elif [ -f ".venv/Scripts/pip" ]; then
        PIP_PATH=".venv/Scripts/pip"
        PYTHON_VENV_PATH=".venv/Scripts/python"
    else
        echo "[-] Error: Virtual environment structure is invalid. Pip not found."
        exit 1
    fi
fi

# 5. Install dependencies
echo "[+] Upgrading pip inside virtual environment..."
$PYTHON_VENV_PATH -m pip install --upgrade pip

echo "[+] Installing requirements..."
$PIP_PATH install -r requirements.txt

echo "============================================="
echo "  Installation Completed successfully."
echo "  To run the app:"
echo "    Linux:   ./lin_run.sh"
echo "    macOS:   ./mac_run.sh"
echo "    Windows: win_run.bat"
echo "============================================="
