# Run Daily

- **Путь**: `scripts\run_daily.ps1`
- **Тип**: .PS1
- **Размер**: 1,251 байт
- **Последнее изменение**: 2026-03-13 02:11:23

## Превью

```
# Запуск ежедневной автоматизации портфолио
# Использование: .\run_daily.ps1

Write-Host "[*] Начало ежедневной автоматизации portfolio-system-architect" -ForegroundColor Green

# 1. Обновление локального репозитория
Write-Host "[1/4] Обновление локального репозитория..." -ForegroundColor Yellow
git pull origin main

# 2. Генерация карты знаний Obsidian
Write-Host "[2/4] Генерация карты знаний Obsidian..." -ForegroundColor Yellow
python scripts/generate_obsidian_map.py

# 3. Генерация веб-сайта

... (файл продолжается)
```
