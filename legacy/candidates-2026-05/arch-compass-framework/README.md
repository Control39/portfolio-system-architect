# Arch-Compass-Framework 🧭

## Профессиональный PowerShell фреймворк

**Создан архитектором когнитивных систем Екатериной Куделей**

Этот фреймворк — не просто набор скриптов, а воплощение моего архитектурного мышления. Я не пишу код ради кода, я проектирую системы, где PowerShell используется как язык оркестрации сложных процессов. Arch-Compass — это инструмент, который позволяет мне, как архитектору, управлять ИИ и инфраструктурой, создавая безопасные и масштабируемые решения.

### Быстрый старт:
```powershell
Import-Module .\ArchCompass.psm1 -Force
Start-ArchCompass -Environment default
```

### Особенности:
* Модульная архитектура
* Управление секретами
* Конфигурация через YAML
* Проверка безопасности
* CI/CD с GitHub Actions
* Интеграция с gitleaks для сканирования секретов

### Безопасность

Фреймворк включает встроенные механизмы проверки безопасности:

#### Управление секретами
* Использование SecretManager для безопасного хранения секретов
* Автоматическое маскирование секретов в логах
* Проверка на хардкодированные секреты в коде

#### Сканирование секретов
* Интеграция с gitleaks для продвинутого сканирования секретов
* Конфигурационный файл .gitleaks.toml для настройки правил
* Автоматическое сканирование при запуске тестов

#### Запуск сканирования безопасности
```powershell
# Запуск тестов с проверкой безопасности
.\arch.ps1 test -RunSecurityTests

# Запуск сканирования секретов gitleaks
.\arch.ps1 analyze -RunGitleaksScan

# Получение оценки безопасности
.\arch.ps1 score
```

### Статус:
Проект в активной разработке. Готовы базовые модули.

### Integrations
- **Terraform Infrastructure**: [packages/terraform/modules/cognitive-system](packages/terraform/modules/cognitive-system) - GCP GKE cluster module
- **Cloud Reason** ([02_MODULES/cloud-reason](02_MODULES/cloud-reason)): Architecture validation via reasoning API
- **IT Compass** ([02_MODULES/it-compass](02_MODULES/it-compass)): Architecture competency tracking
