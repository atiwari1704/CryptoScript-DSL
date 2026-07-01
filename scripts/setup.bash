#!/bin/bash

echo "Setting up CryptoScript..."

if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v py &>/dev/null; then
    PYTHON_CMD="py"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python is not installed or not in PATH."
    exit 1
fi

# Create virtual environment
$PYTHON_CMD -m venv "Crypto"
echo "Virtual environment created."

if [ -f "Crypto/Scripts/activate" ]; then
    source "Crypto/Scripts/activate"
elif [ -f "Crypto/bin/activate" ]; then
    source "Crypto/bin/activate"
fi

# Install dependencies
pip install --quiet -r "./scripts/requirements.txt"
echo "Dependencies installed."

source "./scripts/alias"
