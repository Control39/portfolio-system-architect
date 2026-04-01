# Тесты Arch-Compass Framework

## Структура тестов

```
tests/
├── unit/              # Unit тесты для отдельных модулей
│   ├── core/
│   │   ├── logging/
│   │   ├── security/
│   │   └── validation/
│   └── ...
├── integration/       # Интеграционные тесты
├── e2e/              # End-to-end тесты
└── run-tests.ps1     # Скрипт для запуска тестов
```

## Запуск тестов

### Все тесты
```powershell
.\tests\run-tests.ps1
```

### Только Unit тесты
```powershell
.\tests\run-tests.ps1 -TestType Unit
```

### Только Integration тесты
```powershell
.\tests\run-tests.ps1 -TestType Integration
```

### С покрытием кода
```powershell
.\tests\run-tests.ps1 -CodeCoverage
```

### С фильтрацией по тегам
```powershell
.\tests\run-tests.ps1 -Tag "Security", "Critical"
```

## Требования

- PowerShell 7.2+
- Pester 5.0+

### Установка Pester
```powershell
Install-Module -Name Pester -Force -Scope CurrentUser -SkipPublisherCheck
```

## Покрытие кода

Цель: **> 80% покрытия кода**

Текущее покрытие можно проверить:
```powershell
.\tests\run-tests.ps1 -CodeCoverage
```

Результаты сохраняются в `tests/TestResults/CodeCoverage.xml`

## CI/CD

Тесты автоматически запускаются при:
- Push в `main` или `develop`
- Pull Request в `main` или `develop`
- Ручной запуск через GitHub Actions

См. `.github/workflows/test.yml` для деталей.

## Структура Unit тестов

Каждый модуль имеет свой файл тестов:
- `SecretManager.Tests.ps1` - тесты для SecretManager
- `StructuredLogger.Tests.ps1` - тесты для StructuredLogger
- `InputValidator.Tests.ps1` - тесты для InputValidator
- `SecurityScanner.Tests.ps1` - тесты для SecurityScanner

## Интеграционные тесты

`ModuleIntegration.Tests.ps1` проверяет взаимодействие между модулями:
- SecretManager ↔ StructuredLogger (маскирование секретов в логах)
- InputValidator ↔ SecretManager (валидация перед установкой)
- SecurityScanner ↔ SecretManager (использование паттернов)
- Полный цикл: валидация → SecretManager → логирование → сканирование

## Troubleshooting

### Ошибка "Module not found"
Убедитесь, что все модули находятся в правильных путях:
- `src/infrastructure/security/SecretManager.psm1`
- `src/core/logging/StructuredLogger.psm1`
- `src/core/validation/InputValidator.psm1`
- `src/infrastructure/security/SecurityScanner.psm1`

### Ошибка "Pester not found"
Установите Pester:
```powershell
Install-Module -Name Pester -Force -Scope CurrentUser
```

### Тесты падают из-за временных файлов
Некоторые тесты создают временные файлы. Убедитесь, что у вас есть права на запись в `$TestDrive` (автоматически создается Pester).

