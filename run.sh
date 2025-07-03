#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "[+] Creating virtual environment..."
python3 -m venv venv

echo "[+] Activating virtual environment..."
source venv/bin/activate

echo "[+] Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[+] Running main system script..."
python3 src/main.py
