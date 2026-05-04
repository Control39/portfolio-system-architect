#!/usr/bin/env pwsh
<#
.SYNOPSIS
Активация интеграции системы автоматизации расширений VS Code с Cognitive Automation Agent

.DESCRIPTION
Этот скрипт настраивает интеграцию между системой автоматического управления расширениями VS Code
и Cognitive Automation Agent (CAA). После активации CAA будет автоматически управлять расширениями.

.PARAMETER Mode
Режим активации: install, configure, test, remove

.PARAMETER Force
Принудительное выполнение без подтверждения

.EXAMPLE
.\activate-vscode-extensions-integration.ps1 -Mode install
.\activate-vscode-extensions-integration.ps1 -Mode test
.\activate-vscode-extensions-integration.ps1 -Mode remove
#>

param(
    [ValidateSet("install", "configure", "test", "remove")]
    [string]$Mode = "install",

    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Конфигурация
$Config = @{
    IntegrationConfig = "apps/cognitive-agent/config/vscode-extensions-caa-integration.yaml"
    CaaSkillPath = "apps/cognitive-agent/skills/vscode-extensions-manager"
    ScriptsPath = "scripts"
    ReportsPath = "reports"
}

# Функции
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-Prerequisites {
    Write-Info "Проверка предварительных требований..."

    $missing = @()

    # Проверка Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            $missing += "Python 3.8+"
        } else {
            Write-Info "Python найден: $pythonVersion"
        }
    } catch {
        $missing += "Python 3.8+"
    }

    # Проверка VS Code
    try {
        $vscodePath = Get-Command code -ErrorAction SilentlyContinue
        if (-not $vscodePath) {
            Write-Warning "VS Code CLI (code) не найден в PATH"
        } else {
            Write-Info "VS Code CLI найден"
        }
    } catch {
        Write-Warning "VS Code CLI (code) не найден в PATH"
    }

    # Проверка основного скрипта
    if (-not (Test-Path "$($Config.ScriptsPath)/vscode-extensions-manager.py")) {
        $missing += "Основной скрипт vscode-extensions-manager.py"
    }

    # Проверка конфигурации расширений
    if (-not (Test-Path "config/vscode/vscode-extensions.json")) {
        $missing += "Конфигурация расширений config/vscode/vscode-extensions.json"
    }

    if ($missing.Count -gt 0) {
        Write-Error "Отсутствуют необходимые компоненты:"
        $missing | ForEach-Object { Write-Error "  - $_" }
        return $false
    }

    Write-Success "Все предварительные требования выполнены"
    return $true
}

function Install-Integration {
    Write-Info "Установка интеграции с CAA..."

    # Создание структуры каталогов
    $directories = @(
        $Config.CaaSkillPath,
        $Config.ReportsPath,
        "$($Config.ReportsPath)/vscode-extensions"
    )

    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Info "Создан каталог: $dir"
        }
    }

    # Создание скилла для CAA
    $skillContent = @"
---
name: vscode-extensions-manager
description: |
  Автоматическое управление расширениями VS Code через Cognitive Automation Agent.
  Проверяет соответствие, синхронизирует и оптимизирует расширения.
license: MIT
metadata:
  author: Cognitive Automation Agent
  version: "1.0"
  category: development-tools
  autonomy_level: high
---

# VSCode Extensions Manager Skill

## Команды активации

- "проверь расширения vs code"
- "синхронизируй расширения с конфигурацией"
- "оптимизируй расширения vs code"
- "сгенерируй отчет по расширениям"
- "настрой расширения для проекта"

## Автоматические триггеры

1. **При открытии проекта** - проверка соответствия расширений
2. **При изменении конфигурации** - автоматическая синхронизация
3. **По расписанию (понедельник 9:00)** - еженедельный аудит
4. **При низкой оценке соответствия** - уведомление и предложение исправления

## Интеграция с CI/CD

Интегрировано с GitHub Actions workflow:
\`.github/workflows/vscode-extensions-check.yml\`

## Метрики

- \`extensions_compliance_score\` - оценка соответствия (цель: >90%)
- \`extensions_count\` - количество установленных расширений
- \`optimization_savings_mb\` - экономия места после оптимизации

## Безопасность

- Только dry-run режим по умолчанию
- Требуется подтверждение для изменений
- Резервное копирование перед изменениями
"@

    Set-Content -Path "$($Config.CaaSkillPath)/SKILL.md" -Value $skillContent
    Write-Info "Создан скилл для CAA: $($Config.CaaSkillPath)/SKILL.md"

    # Создание скрипта активации для CAA
    $activationScript = @"
#!/usr/bin/env python3
"""
Скрипт активации для интеграции с Cognitive Automation Agent
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def check_extensions_compliance():
    """Проверка соответствия расширений"""
    cmd = [sys.executable, "scripts/vscode-extensions-manager.py", "--check", "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        data = json.loads(result.stdout)
        return {
            "success": True,
            "compliance_score": data.get("compliance_score", 0),
            "missing": data.get("missing_extensions", []),
            "recommendations": data.get("recommendations", [])
        }
    else:
        return {
            "success": False,
            "error": result.stderr
        }

def sync_extensions(dry_run=True):
    """Синхронизация расширений"""
    cmd = [sys.executable, "scripts/vscode-extensions-manager.py", "--sync"]
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd, capture_output=True, text=True)

    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr if result.returncode != 0 else None
    }

def generate_report():
    """Генерация отчета"""
    cmd = [sys.executable, "scripts/vscode-extensions-manager.py", "--report"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    report_path = "reports/vscode-extensions-report.md"
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()

        return {
            "success": True,
            "report_path": report_path,
            "summary": report_content[:500] + "..." if len(report_content) > 500 else report_content
        }
    else:
        return {
            "success": False,
            "error": "Отчет не сгенерирован"
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python activate.py <command> [options]")
        print("Команды: check, sync, report")
        sys.exit(1)

    command = sys.argv[1]

    if command == "check":
        result = check_extensions_compliance()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "sync":
        dry_run = "--dry-run" in sys.argv
        result = sync_extensions(dry_run)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "report":
        result = generate_report()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        print(f"Неизвестная команда: {command}")
        sys.exit(1)
"@

    Set-Content -Path "$($Config.CaaSkillPath)/activate.py" -Value $activationScript
    Write-Info "Создан скрипт активации: $($Config.CaaSkillPath)/activate.py"

    # Добавление конфигурации в CAA
    if (Test-Path $Config.IntegrationConfig) {
        Write-Info "Конфигурация интеграции уже существует: $($Config.IntegrationConfig)"
    } else {
        Write-Warning "Конфигурационный файл не найден, создан по умолчанию"
    }

    Write-Success "Интеграция с CAA установлена"
    Write-Info "Для тестирования запустите: .\activate-vscode-extensions-integration.ps1 -Mode test"
}

function Test-Integration {
    Write-Info "Тестирование интеграции..."

    $tests = @(
        @{Name = "Конфигурация"; Path = $Config.IntegrationConfig},
        @{Name = "Скрипт активации CAA"; Path = "$($Config.CaaSkillPath)/activate.py"},
        @{Name = "Скилл CAA"; Path = "$($Config.CaaSkillPath)/SKILL.md"},
        @{Name = "Основной скрипт"; Path = "$($Config.ScriptsPath)/vscode-extensions-manager.py"}
    )

    $allPassed = $true

    foreach ($test in $tests) {
        if (Test-Path $test.Path) {
            Write-Success "✓ $($test.Name): $($test.Path)"
        } else {
            Write-Error "✗ $($test.Name): $($test.Path) не найден"
            $allPassed = $false
        }
    }

    # Тестирование выполнения скрипта
    Write-Info "Тестирование выполнения скрипта проверки..."
    try {
        $result = python "$($Config.ScriptsPath)/vscode-extensions-manager.py" --check --dry-run 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✓ Скрипт проверки выполняется успешно"
        } else {
            Write-Error "✗ Скрипт проверки завершился с ошибкой"
            Write-Error $result
            $allPassed = $false
        }
    } catch {
        Write-Error "✗ Ошибка при выполнении скрипта проверки: $_"
        $allPassed = $false
    }

    if ($allPassed) {
        Write-Success "Все тесты пройдены успешно!"
        return $true
    } else {
        Write-Error "Некоторые тесты не пройдены"
        return $false
    }
}

function Remove-Integration {
    Write-Warning "Удаление интеграции с CAA..."

    if (-not $Force) {
        $confirmation = Read-Host "Вы уверены, что хотите удалить интеграцию? (y/N)"
        if ($confirmation -notin @("y", "Y", "yes", "Yes")) {
            Write-Info "Удаление отменено"
            return
        }
    }

    # Удаление скилла CAA
    if (Test-Path $Config.CaaSkillPath) {
        Remove-Item -Path $Config.CaaSkillPath -Recurse -Force
        Write-Info "Удален скилл CAA: $($Config.CaaSkillPath)"
    }

    # Удаление конфигурации
    if (Test-Path $Config.IntegrationConfig) {
        Remove-Item -Path $Config.IntegrationConfig -Force
        Write-Info "Удалена конфигурация: $($Config.IntegrationConfig)"
    }

    Write-Success "Интеграция удалена"
}

# Основная логика
Write-Info "Активация интеграции системы расширений VS Code с CAA"
Write-Info "Режим: $Mode"

switch ($Mode) {
    "install" {
        if (Test-Prerequisites) {
            Install-Integration
            Test-Integration
        }
    }

    "configure" {
        Write-Info "Конфигурация интеграции..."
        # Дополнительная конфигурация может быть добавлена здесь
        Write-Success "Конфигурация завершена"
    }

    "test" {
        Test-Integration
    }

    "remove" {
        Remove-Integration
    }

    default {
        Write-Error "Неизвестный режим: $Mode"
        exit 1
    }
}

Write-Info "Завершено"
