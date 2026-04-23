@{
    ModuleName        = 'IModule'
    ModuleVersion     = '1.0.0'
    Description       = 'Базовый контракт для всех подмодулей Arch-Compass'
    FunctionsToExport = @(
        'Initialize-Module',   # Инициализация зависимостей
        'Validate-Config',     # Валидация конфигурации
        'Execute-Command',     # Основная логика
        'Get-ModuleStatus'     # Health check модуля
    )
    Parameters        = @{
        Initialize-Module = @('ConfigPath', 'LogLevel')
        Validate-Config = @('ConfigObject')
        Execute-Command = @('CommandName', 'Parameters', 'WhatIf')
        Get-ModuleStatus = @()
    }
}