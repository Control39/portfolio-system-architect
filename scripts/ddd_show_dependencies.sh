#!/usr/bin/env bash
# ddd_show_dependencies.sh - Показать зависимости между сервисами

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"
"$PYTHON_CMD" scripts/ddd_show_dependencies.py
