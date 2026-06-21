#!/bin/bash
# ddd_show_issues.sh - Показать архитектурные проблемы

cd /c/repo
source .venv/Scripts/activate

python scripts/ddd_show_issues.py
