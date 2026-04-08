# Запуск ежедневной автоматизации портфолио
# Использование: .\run_daily.ps1

Write-Host "[*] Начало ежедневной автоматизации portfolio-system-architect" -ForegroundColor Green

# 1. Обновление локального репозитория
Write-Host "[1/4] Обновление локального репозитория..." -ForegroundColor Yellow
git pull origin main

# 2. Генерация карты знаний Obsidian
Write-Host "[2/4] Генерация карты знаний Obsidian..." -ForegroundColor Yellow
python ../documentation/generate_obsidian_map.py

# 3. Генерация веб-сайта
Write-Host "[3/4] Генерация веб-сайта..." -ForegroundColor Yellow
python ../documentation/generate_website.py

# 4. Коммит и пуш изменений
Write-Host "[4/4] Коммит и пуш изменений..." -ForegroundColor Yellow
$date = Get-Date -Format "yyyy-MM-dd HH:mm"
git add .
git commit -m "[AUTO] Ежедневное обновление: $date"
git push origin main

Write-Host "[V] Ежедневная автоматизация завершена успешно!" -ForegroundColor Green

