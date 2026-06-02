# src/core/localization/Localization.psm1

$script:Translations = @{
    "en-US" = @{
        Title = "🚀 Arch-Compass: Your Architecture, Automated"
        Creating = "Creating project structure in: {0}"
        Dependencies = "Checking dependencies..."
        Success = "✅ Project created successfully!"
        InitComplete = "Initialization complete. Run 'arch.ps1 deploy' to continue."
    }
    "ru-RU" = @{
        Title = "🚀 Arch-Compass: Ваша архитектура, автоматизирована"
        Creating = "Создание структуры проекта в: {0}"
        Dependencies = "Проверка зависимостей..."
        Success = "✅ Проект успешно создан!"
        InitComplete = "Инициализация завершена. Выполните 'arch.ps1 deploy' для продолжения."
    }
}

$script:CurrentLanguage = "en-US"

function Set-Localization {
    param([string]$LanguageCode)
    if ($script:Translations.ContainsKey($LanguageCode)) {
        $script:CurrentLanguage = $LanguageCode
        Write-Host "Language set to $LanguageCode" -ForegroundColor Green
    } else {
        Write-Warning "Language '$LanguageCode' not supported. Using $($script:CurrentLanguage)"
    }
}

function Get-LocalizedString {
    param([string]$Key, [object[]]$Args = @())
    $dict = $script:Translations[$script:CurrentLanguage]
    if ($dict -and $dict.ContainsKey($Key)) {
        $msg = $dict[$Key]
        if ($Args.Count -gt 0) {
            return $msg -f $Args
        }
        return $msg
    }
    return $Key
}

Export-ModuleMember -Function Set-Localization, Get-LocalizedString
