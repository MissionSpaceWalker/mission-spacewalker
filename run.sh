#!/bin/bash

set -e  # exit on error

USE_DUMMY=false

if [[ "$1" == "--dummy" ]]; then
  USE_DUMMY=true
elif [[ -n "$1" ]]; then
  echo "[!] unknown option: $1"
  echo "usage: ./run.sh [--dummy]"
  exit 1
fi

# setup virtual environment
if [ ! -d "venv" ]; then
  echo "creating virtual environment..."
  python3 -m venv venv
fi

echo "activating virtual environment..."
source venv/bin/activate

echo "installing requirements..."
pip install --upgrade pip --quiet || echo "pip upgrade failed"
pip install -r requirements.txt --quiet || echo "requirements install failed"

clear

# run the main system script
echo "running main system..."
if $USE_DUMMY; then
  echo "running in DUMMY mode (no Raspberry Pi hardware required)"
  USE_DUMMY_SENSORS=true python3 src/mswua.py
else
  python3 src/mswua.py
fi
