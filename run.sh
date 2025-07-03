#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

if [ -d "venv" ]; then
  read -p "[~] Virtual environment already exists. Recreate it? [y/N]: " confirm
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    echo "[!] Removing existing virtual environment..."
    rm -rf venv
  else
    echo "[>] Reusing existing virtual environment..."
  fi
fi

echo "[+] Creating virtual environment..."
python3 -m venv venv

echo "[+] Activating virtual environment..."
source venv/bin/activate

echo "[+] Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[+] Running main system script..."
python3 src/main.py
