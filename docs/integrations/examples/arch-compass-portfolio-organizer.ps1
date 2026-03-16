# Пример интеграции arch-compass-framework и portfolio-organizer
# Демонстрация PowerShell скрипта для интеграции архитектурного фреймворка и организатора портфолио

# Функция для инициализации архитектурного проекта
function Initialize-ArchProject {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectName,
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath,
        [string]$Description = "",
        [string[]]$Technologies = @()
    )

    Write-Host "Инициализация архитектурного проекта: $ProjectName" -ForegroundColor Green

    # Создание структуры проекта
    $folders = @(
        "docs",
        "src",
        "tests",
        "config",
        "infrastructure"
    )

    foreach ($folder in $folders) {
        $fullPath = Join-Path $ProjectPath $folder
        if (!(Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath | Out-Null
            Write-Host "Создана папка: $folder"
        }
    }

    # Создание архитектурного описания
    $archDocPath = Join-Path $ProjectPath "docs/architecture.md"
    $archContent = @"
# Архитектура проекта $ProjectName

## Описание
$Description

## Используемые технологии
$($Technologies -join ", ")

## Компоненты системы
1. [Компонент 1] - Описание компонента
2. [Компонент 2] - Описание компонента
3. [Компонент 3] - Описание компонента

## Диаграммы
- Диаграмма компонентов
- Диаграмма развертывания
- Диаграмма последовательности

## Рекомендации по реализации
1. Следовать принципам SOLID
2. Использовать паттерны проектирования
3. Обеспечить тестируемость кода
"@

    $archContent | Out-File -FilePath $archDocPath -Encoding UTF8
    Write-Host "Создан файл архитектурного описания: $archDocPath"

    # Создание конфигурационного файла
    $configPath = Join-Path $ProjectPath "config/arch-config.json"
    $config = @{
        projectName = $ProjectName
        version = "1.0.0"
        technologies = $Technologies
        components = @()
        patterns = @("MVC", "Repository", "Dependency Injection")
    }

    $config | ConvertTo-Json -Depth 10 | Out-File -FilePath $configPath -Encoding UTF8
    Write-Host "Создан конфигурационный файл: $configPath"
}

# Функция для добавления компонента в архитектуру
function Add-ArchComponent {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath,
        [Parameter(Mandatory=$true)]
        [string]$ComponentName,
        [string]$ComponentType = "Service",
        [string]$Description = ""
    )

    Write-Host "Добавление компонента '$ComponentName' в проект" -ForegroundColor Yellow

    # Обновление конфигурационного файла
    $configPath = Join-Path $ProjectPath "config/arch-config.json"
    if (Test-Path $configPath) {
        $config = Get-Content $configPath | ConvertFrom-Json
        $newComponent = @{
            name = $ComponentName
            type = $ComponentType
            description = $Description
            dependencies = @()
        }

        $config.components += $newComponent
        $config | ConvertTo-Json -Depth 10 | Out-File -FilePath $configPath -Encoding UTF8
        Write-Host "Компонент добавлен в конфигурацию"
    }

    # Создание документации по компоненту
    $componentDocPath = Join-Path $ProjectPath "docs/components/$ComponentName.md"
    $docFolder = Split-Path $componentDocPath
    if (!(Test-Path $docFolder)) {
        New-Item -ItemType Directory -Path $docFolder | Out-Null
    }

    $componentContent = @"
# Компонент $ComponentName

## Тип
$ComponentType

## Описание
$Description

## Ответственность
- [Ответственность 1]
- [Ответственность 2]
- [Ответственность 3]

## Интерфейсы
- [Интерфейс 1]
- [Интерфейс 2]

## Зависимости
- [Зависимость 1]
- [Зависимость 2]

## Паттерны проектирования
- [Паттерн 1]
- [Паттерн 2]
"@

    $componentContent | Out-File -FilePath $componentDocPath -Encoding UTF8
    Write-Host "Создана документация по компоненту: $componentDocPath"
}

# Функция для интеграции с portfolio-organizer
function Update-Portfolio {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath,
        [Parameter(Mandatory=$true)]
        [string]$PortfolioPath,
        [string]$Category = "Architecture"
    )

    Write-Host "Обновление портфолио: $PortfolioPath" -ForegroundColor Cyan

    $projectName = Split-Path $ProjectPath -Leaf
    $projectConfig = Join-Path $ProjectPath "config/arch-config.json"

    if (Test-Path $projectConfig) {
        $config = Get-Content $projectConfig | ConvertFrom-Json
        $projectInfo = @{
            name = $config.projectName
            technologies = $config.technologies -join ", "
            components = $config.components.Count
            category = $Category
            lastUpdated = Get-Date -Format "yyyy-MM-dd"
        }

        # Создание записи в портфолио
        $portfolioEntry = Join-Path $PortfolioPath "projects/$projectName.json"
        $portfolioDir = Split-Path $portfolioEntry
        if (!(Test-Path $portfolioDir)) {
            New-Item -ItemType Directory -Path $portfolioDir | Out-Null
        }

        $projectInfo | ConvertTo-Json | Out-File -FilePath $portfolioEntry -Encoding UTF8
        Write-Host "Добавлена запись в портфолио: $portfolioEntry"
    }
}

# Основная функция демонстрации
function Main {
    Write-Host "Демонстрация интеграции arch-compass-framework и portfolio-organizer" -ForegroundColor Magenta
    Write-Host "=" * 70

    # Параметры проекта
    $projectName = "ECommercePlatform"
    $projectPath = ".\$projectName"
    $portfolioPath = ".\portfolio"

    # Инициализация проекта
    Initialize-ArchProject -ProjectName $projectName -ProjectPath $projectPath -Description "Платформа электронной коммерции" -Technologies @("ASP.NET Core", "React", "PostgreSQL", "Redis")

    # Добавление компонентов
    Add-ArchComponent -ProjectPath $projectPath -ComponentName "UserService" -ComponentType "Service" -Description "Сервис управления пользователями"
    Add-ArchComponent -ProjectPath $projectPath -ComponentName "ProductCatalog" -ComponentType "Service" -Description "Сервис каталога продуктов"
    Add-ArchComponent -ProjectPath $projectPath -ComponentName "OrderProcessing" -ComponentType "Service" -Description "Сервис обработки заказов"

    # Создание структуры портфолио
    if (!(Test-Path $portfolioPath)) {
        New-Item -ItemType Directory -Path $portfolioPath | Out-Null
        New-Item -ItemType Directory -Path "$portfolioPath/projects" | Out-Null
    }

    # Обновление портфолио
    Update-Portfolio -ProjectPath $projectPath -PortfolioPath $portfolioPath -Category "Web Applications"

    Write-Host "`n=== ЗАВЕРШЕНИЕ ДЕМОНСТРАЦИИ ===" -ForegroundColor Green
    Write-Host "Интеграция arch-compass-framework и portfolio-organizer позволяет:"
    Write-Host "1. Автоматизировать создание архитектурных описаний"
    Write-Host "2. Структурировать информацию о компонентах системы"
    Write-Host "3. Поддерживать актуальность портфолио"
    Write-Host "4. Обеспечивать консистентность архитектурной документации"
}

# Запуск демонстрации
Main
