#!/usr/bin/env bash
# ddd_show_issues.sh - Показать архитектурные проблемы

# Используем относительные пути для совместимости с разными ОС
cd "$(dirname "$0")/.."

python scripts/ddd_show_issues.py
