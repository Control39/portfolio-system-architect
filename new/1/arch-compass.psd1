# ArchCompass.psm1 - главный модуль

# Импорт модулей
Import-Module "$PSScriptRoot\src/core/utilities/ConfigurationManager.psm1" -Force
Import-Module "$PSScriptRoot\src/infrastructure/security/SecretManager.psm1" -Force

function Start-ArchCompass {
    param(
        [string]$Environment = "default",
        [switch]$RunSecurityTests,
        [switch]$Help
    )
    
    if ($Help) {
        Write-Host "Использование: Start-ArchCompass [-Environment <string>] [-RunSecurityTests] [-Help]" -ForegroundColor Cyan
        return
    }
    
    try {
        Write-Host "🚀 Запуск Arch-Compass Framework..." -ForegroundColor Cyan
        
        # 1. Инициализация конфигурации
        $configManager = [ConfigurationManager]::GetInstance()
        $configManager.Initialize($Environment)
        
        # 2. Инициализация SecretManager
        [SecretManager]::Initialize(@{
            VaultType = "Environment"
        })
        
        # 3. Получение API ключа
        $apiKey = [SecretManager]::GetSecret("OPENAI_API_KEY")
        if (-not $apiKey) {
            Write-Host "⚠️  OpenAI API ключ не найден. Установите переменную окружения OPENAI_API_KEY" -ForegroundColor Yellow
        } else {
            Write-Host "✅ OpenAI API ключ получен" -ForegroundColor Green
        }
        
        # 4. Проверка безопасности
        if ($RunSecurityTests) {
            Write-Host "🔐 Выполняется проверка безопасности..." -ForegroundColor Cyan
            # Здесь будет вызов SecurityScanner
        }
        
        Write-Host "`n✅ Arch-Compass Framework успешно запущен!" -ForegroundColor Green
        Write-Host "   Окружение: $Environment" -ForegroundColor Yellow
        Write-Host "   Версия: 1.0.0" -ForegroundColor Yellow
        
    } catch {
        Write-Host "❌ Ошибка при запуске: $_" -ForegroundColor Red
    }
}

# Экспорт функции
Export-ModuleMember -Function Start-ArchCompass
