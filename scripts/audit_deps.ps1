# audit_deps.ps1 - Безопасный аудит зависимостей Python
# Ничего не удаляет без подтверждения, только анализирует и предлагает
# Сохранить в: C:\repo\scripts\audit_deps.ps1

param(
    [switch]$Fix,           # Добавьте -Fix, чтобы автоматически исправлять версии
    [switch]$RemoveFlask,   # Добавьте -RemoveFlask, чтобы удалить Flask
    [switch]$RemoveAzure    # Добавьте -RemoveAzure, чтобы удалить Azure пакеты
)

# Переходим в корень репозитория (откуда бы ни запустили скрипт)
Set-Location $PSScriptRoot\..
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Аудит зависимостей Python" -ForegroundColor Cyan
Write-Host "  Рабочая директория: $PWD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Сохраняем текущие зависимости
Write-Host "`n[1/6] Сохранение текущих зависимостей..." -ForegroundColor Yellow
pip list --format=freeze | Out-File -FilePath "current_deps.txt" -Encoding utf8
Write-Host "       ✅ Сохранено в current_deps.txt" -ForegroundColor Green

# 2. Проверяем несуществующие версии
Write-Host "`n[2/6] Проверка существования версий на PyPI..." -ForegroundColor Yellow

$suspicious = @(
    @{name="numpy"; version="2.4.6"},
    @{name="pandas"; version="3.0.3"},
    @{name="scipy"; version="1.17.1"},
    @{name="cryptography"; version="48.0.1"},
    @{name="urllib3"; version="2.7.0"},
    @{name="starlette"; version="1.3.1"},
    @{name="pip_audit"; version="2.10.0"},
    @{name="safety"; version="3.7.0"}
)

$bad_versions = @()
$fixed_requirements = @()

foreach ($pkg in $suspicious) {
    $pkgName = $pkg.name
    $badVer = $pkg.version

    Write-Host "       Проверяю $pkgName==$badVer..." -NoNewline

    # Проверяем, существует ли такая версия
    $check = pip index versions $pkgName 2>$null | Select-String -Pattern "Available versions:"

    if ($check -match $badVer) {
        Write-Host " ✅ существует" -ForegroundColor Green
        $fixed_requirements += "$pkgName==$badVer"
    } else {
        Write-Host " ❌ НЕ СУЩЕСТВУЕТ!" -ForegroundColor Red
        $bad_versions += $pkg

        # Пытаемся найти последнюю версию
        $latestVer = pip index versions $pkgName 2>$null | Select-String -Pattern "Available versions:" | ForEach-Object { $_ -replace ".*Available versions: ", "" } | ForEach-Object { ($_ -split ", ")[0] }

        if ($latestVer) {
            Write-Host "         → Рекомендую: $pkgName==$latestVer" -ForegroundColor Yellow
            if ($Fix) {
                $fixed_requirements += "$pkgName==$latestVer"
                Write-Host "         ✅ Будет исправлено" -ForegroundColor Green
            } else {
                $fixed_requirements += "# $pkgName==$badVer (не существует, замените на $latestVer)"
            }
        }
    }
}

# 3. Проверяем импорты Flask и Azure в коде
Write-Host "`n[3/6] Проверка использования Flask и Azure в коде..." -ForegroundColor Yellow

$flask_usage = Get-ChildItem -Recurse -Filter "*.py" -ErrorAction SilentlyContinue | Select-String -Pattern "from flask import|import flask"
$azure_usage = Get-ChildItem -Recurse -Filter "*.py" -ErrorAction SilentlyContinue | Select-String -Pattern "from azure\.|import azure"

if ($flask_usage) {
    Write-Host "       ⚠️ Найдено использование Flask:" -ForegroundColor Yellow
    $flask_usage | ForEach-Object { Write-Host "         $_" -ForegroundColor Gray }
} else {
    Write-Host "       ✅ Flask не используется" -ForegroundColor Green
    if ($RemoveFlask -or $Fix) {
        Write-Host "         → Можно безопасно удалить Flask" -ForegroundColor Green
        $remove_flask = $true
    }
}

if ($azure_usage) {
    Write-Host "       ⚠️ Найдено использование Azure:" -ForegroundColor Yellow
    $azure_usage | ForEach-Object { Write-Host "         $_" -ForegroundColor Gray }
} else {
    Write-Host "       ✅ Azure не используется" -ForegroundColor Green
    if ($RemoveAzure -or $Fix) {
        Write-Host "         → Можно безопасно удалить Azure пакеты" -ForegroundColor Green
        $remove_azure = $true
    }
}

# 4. Генерируем чистый requirements.txt
Write-Host "`n[4/6] Генерация чистого requirements.txt..." -ForegroundColor Yellow

# Получаем текущие установленные пакеты (реальные версии)
$installed = pip list --format=freeze | Out-String -Stream | Where-Object { $_ -match "==" }

# Фильтруем Flask и Azure если нужно
$filtered = $installed
if ($RemoveFlask -and $flask_usage.Count -eq 0) {
    $filtered = $filtered | Where-Object { $_ -notmatch "Flask|Jinja2|Werkzeug|itsdangerous|click|blinker|MarkupSafe" }
    Write-Host "       🧹 Flask и зависимости будут удалены" -ForegroundColor Yellow
}
if ($RemoveAzure -and $azure_usage.Count -eq 0) {
    $filtered = $filtered | Where-Object { $_ -notmatch "azure-" }
    Write-Host "       🧹 Azure пакеты будут удалены" -ForegroundColor Yellow
}

# Заменяем плохие версии на хорошие
$clean_requirements = @()
foreach ($line in $filtered) {
    $fixed = $false
    foreach ($bad in $bad_versions) {
        if ($line -match "$($bad.name)==") {
            if ($Fix) {
                # Находим последнюю версию
                $latestVer = pip index versions $bad.name 2>$null | Select-String -Pattern "Available versions:" | ForEach-Object { $_ -replace ".*Available versions: ", "" } | ForEach-Object { ($_ -split ", ")[0] }
                $clean_requirements += "$($bad.name)==$latestVer"
                Write-Host "       🔧 Исправлен: $($bad.name)" -ForegroundColor Green
            } else {
                $clean_requirements += "# $line (проблемная версия, требует проверки)"
            }
            $fixed = $true
            break
        }
    }
    if (-not $fixed) {
        $clean_requirements += $line
    }
}

$clean_requirements | Out-File -FilePath "requirements.clean.txt" -Encoding utf8
Write-Host "       ✅ Сохранено в requirements.clean.txt" -ForegroundColor Green

# 5. Запускаем pip-audit
Write-Host "`n[5/6] Запуск аудита безопасности..." -ForegroundColor Yellow

if (Test-Path "requirements.clean.txt") {
    $audit_output = pip-audit --requirement requirements.clean.txt --format=json 2>&1
    $audit_json = $audit_output -join "`n" | ConvertFrom-Json -ErrorAction SilentlyContinue

    if ($audit_json -and $audit_json.Count -gt 0 -and $audit_json[0].vulnerabilities) {
        Write-Host "       ⚠️ Найдены уязвимости:" -ForegroundColor Red
        $vulnerabilities = @()
        foreach ($finding in $audit_json) {
            foreach ($vuln in $finding.vulnerabilities) {
                $vulnObj = [PSCustomObject]@{
                    Пакет = $finding.name
                    Версия = $finding.version
                    Критичность = $vuln.severity
                    CVE = $vuln.id
                    Описание = $vuln.description
                }
                $vulnerabilities += $vulnObj

                $severityColor = if ($vuln.severity -eq "high") { "Red" } elseif ($vuln.severity -eq "medium") { "Yellow" } else { "White" }
                Write-Host "         - $($finding.name) $($finding.version) [$($vuln.severity)] $($vuln.id)" -ForegroundColor $severityColor
            }
        }

        if ($vulnerabilities.Count -gt 0) {
            $vulnerabilities | Export-Csv -Path "vulnerabilities.csv" -NoTypeInformation -Encoding utf8
            Write-Host "       📄 Подробности сохранены в vulnerabilities.csv" -ForegroundColor Yellow
        }
    } elseif ($audit_output -match "No known vulnerabilities found") {
        Write-Host "       ✅ Критических уязвимостей не найдено" -ForegroundColor Green
    } else {
        Write-Host "       ⚠️ Не удалось выполнить аудит (возможно, нет интернета или проблема с форматом)" -ForegroundColor Yellow
        $audit_output | Out-File -FilePath "pip-audit-error.log" -Encoding utf8
        Write-Host "       📄 Ошибка сохранена в pip-audit-error.log" -ForegroundColor Gray
    }
}

# 6. Проверка конфликтов версий
Write-Host "`n[6/7] Проверка конфликтов версий..." -ForegroundColor Yellow
$pip_check = pip check 2>&1
if ($pip_check -match "No broken requirements found") {
    Write-Host "       ✅ Конфликтов версий не найдено" -ForegroundColor Green
} else {
    Write-Host "       ⚠️ Найдены конфликты:" -ForegroundColor Red
    $pip_check | Out-File -FilePath "pip-conflicts.txt" -Encoding utf8
    Write-Host "       📄 Конфликты сохранены в pip-conflicts.txt" -ForegroundColor Yellow
    $pip_check | ForEach-Object { Write-Host "         $_" -ForegroundColor Gray }
}

# 7. Итоговый отчёт
Write-Host "`n[7/7] Формирование итогового отчёта..." -ForegroundColor Yellow

$report = @"
======================================
ОТЧЁТ АУДИТА ЗАВИСИМОСТЕЙ
======================================

Дата: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Репозиторий: $PWD

--- ПРОБЛЕМНЫЕ ЗАВИСИМОСТИ ---

"@

if ($bad_versions.Count -gt 0) {
    $report += "⚠️ Найдены пакеты с несуществующими версиями:`n"
    foreach ($bad in $bad_versions) {
        $latestVer = pip index versions $bad.name 2>$null | Select-String -Pattern "Available versions:" | ForEach-Object { $_ -replace ".*Available versions: ", "" } | ForEach-Object { ($_ -split ", ")[0] }
        $report += "  - $($bad.name): $($bad.version) → рекомендуется $latestVer`n"
    }
} else {
    $report += "✅ Пакетов с несуществующими версиями не найдено.`n"
}

$report += @"

--- СТАТУС FLASK ---
$(if ($flask_usage) { "⚠️ ИСПОЛЬЗУЕТСЯ (не удалять без проверки)" } else { "✅ НЕ ИСПОЛЬЗУЕТСЯ (можно удалить)" })

--- СТАТУС AZURE ---
$(if ($azure_usage) { "⚠️ ИСПОЛЬЗУЕТСЯ (не удалять без проверки)" } else { "✅ НЕ ИСПОЛЬЗУЕТСЯ (можно удалить)" })

--- КОНФЛИКТЫ ВЕРСИЙ ---
$((Get-Content "pip-conflicts.txt" -Raw -ErrorAction SilentlyContinue) -replace "`n","`n  ")

--- РЕКОМЕНДАЦИИ ---

"@

if ($bad_versions.Count -gt 0) {
    $report += "1. 🔧 Исправьте несуществующие версии в requirements.txt`n"
    $report += "   Запустите: .\scripts\audit_deps.ps1 -Fix`n"
}

if (-not $flask_usage) {
    $report += "2. 🧹 Удалите Flask (не используется): .\scripts\audit_deps.ps1 -RemoveFlask`n"
}

if (-not $azure_usage) {
    $report += "3. 🧹 Удалите Azure (не используется): .\scripts\audit_deps.ps1 -RemoveAzure`n"
}

$report += @"
4. 📦 Обновите зависимости:
   pip install -r requirements.clean.txt

5. 🔒 Повторите аудит безопасности:
   pip-audit --requirement requirements.clean.txt

--- ФАЙЛЫ ОТЧЁТА ---
- current_deps.txt - текущие зависимости
- requirements.clean.txt - исправленные зависимости
"@

if (Test-Path "vulnerabilities.csv") {
    $report += "- vulnerabilities.csv - детали уязвимостей`n"
}
if (Test-Path "pip-conflicts.txt") {
    $report += "- pip-conflicts.txt - конфликты версий`n"
}

$report += @"

======================================
"@

$report | Out-File -FilePath "audit_report.txt" -Encoding utf8
Write-Host "       ✅ Отчёт сохранён в audit_report.txt" -ForegroundColor Green

# Финальный вывод
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✅ АУДИТ ЗАВЕРШЁН" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n📄 Полный отчёт: audit_report.txt" -ForegroundColor White
Write-Host "📦 Чистые зависимости: requirements.clean.txt" -ForegroundColor White
if (Test-Path "vulnerabilities.csv") {
    Write-Host "⚠️  Уязвимости: vulnerabilities.csv" -ForegroundColor Yellow
}
if (Test-Path "pip-conflicts.txt") {
    Write-Host "⚠️  Конфликты версий: pip-conflicts.txt" -ForegroundColor Yellow
}

Write-Host "`n👉 Для автоматического исправления запустите с ключом -Fix:" -ForegroundColor Cyan
Write-Host "   .\scripts\audit_deps.ps1 -Fix" -ForegroundColor White

if (-not $flask_usage) {
    Write-Host "`n👉 Для удаления Flask (не используется):" -ForegroundColor Cyan
    Write-Host "   .\scripts\audit_deps.ps1 -RemoveFlask" -ForegroundColor White
}

if (-not $azure_usage) {
    Write-Host "`n👉 Для удаления Azure (не используется):" -ForegroundColor Cyan
    Write-Host "   .\scripts\audit_deps.ps1 -RemoveAzure" -ForegroundColor White
}

Write-Host "`n👉 Комбо-режим (исправить + удалить всё ненужное):" -ForegroundColor Cyan
Write-Host "   .\scripts\audit_deps.ps1 -Fix -RemoveFlask -RemoveAzure" -ForegroundColor White

Write-Host ""ы
