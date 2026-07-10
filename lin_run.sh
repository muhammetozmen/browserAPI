#!/usr/bin/env bash

echo "============================================="
echo "  Starting browserAPI Gateway (Linux)"
echo "============================================="

# 1. Check if venv python exists
VENV_PYTHON=".venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "[-] Error: Virtual environment python not found at $VENV_PYTHON."
    echo "    Please run ./install.sh first to set up the environment."
    
    # Check if system python exists to help the user
    if command -v python3 >/dev/null 2>&1; then
        echo "[+] Found system python3. You can set up the environment by running: ./install.sh"
    elif command -v python >/dev/null 2>&1; then
        echo "[+] Found system python. You can set up the environment by running: ./install.sh"
    else
        echo "[-] System Python was not found either. Please install Python 3.11+."
    fi
    exit 1
fi

# 2. Run the application
echo "[+] Starting app with $VENV_PYTHON src/main.py"
exec "$VENV_PYTHON" src/main.py
