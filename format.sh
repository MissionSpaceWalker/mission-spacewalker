#!/bin/bash

echo "[+] Formatting Python files with black..."
black .

echo "[+] Sorting imports with isort..."
isort .

echo "[+] Lint-fixing with ruff..."
ruff check . --fix

echo "[✓] Formatting complete."
