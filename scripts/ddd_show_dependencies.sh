#!/bin/bash
# ddd_show_dependencies.sh - Показать зависимости между сервисами

cd /c/repo
source .venv/Scripts/activate

python scripts/ddd_show_dependencies.py
