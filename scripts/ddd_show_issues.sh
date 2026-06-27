#!/usr/bin/env bash
# ddd_show_issues.sh - Показать архитектурные проблемы

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"
"$PYTHON_CMD" scripts/ddd_show_issues.py
