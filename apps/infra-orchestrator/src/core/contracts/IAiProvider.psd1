@{
    ModuleName        = 'IAiProvider'
    FunctionsToExport = @(
        'Initialize-Provider',  # Настройка API-ключа, endpoint
        'Invoke-Completion',    # Генерация ответа
        'Invoke-Embedding',     # Получение эмбеддингов
        'Get-ProviderInfo',     # Мета-информация (модель, лимиты)
        'Test-Connection'       # Health check провайдера
    )
}
