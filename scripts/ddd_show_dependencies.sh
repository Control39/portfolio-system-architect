#!/usr/bin/env bash
# ddd_show_dependencies.sh - Показать зависимости между сервисами

# Используем относительные пути для совместимости с разными ОС
cd "$(dirname "$0")/.."

python scripts/ddd_show_dependencies.py
