\`
arch-compass-system/
├── .github/                          # GitHub специфичные файлы
│   ├── workflows/                    # GitHub Actions workflows
│   ├── ISSUE\_TEMPLATE/               # Шаблоны issue
│   └── PULL\_REQUEST\_TEMPLATE/        # Шаблоны PR
│
├── .devcontainer/                    # Dev Containers конфигурация
│   └── devcontainer.json
│
├── .vscode/                          # VS Code настройки
│   ├── settings.json
│   ├── extensions.json
│   └── tasks.json
│
├── artifacts/                        # Сгенерированные артефакты (в .gitignore)
│   ├── builds/                       # Сборки
│   ├── packages/                     # Пакеты
│   ├── reports/                      # Отчеты
│   └── logs/                         # Временные логи
│
├── src/                              # Исходный код
│   ├── core/                         # Ядро фреймворка
│   │   ├── commands/                 # Обработчики команд
│   │   │   ├── InitCommand.ps1
│   │   │   ├── DeployCommand.ps1
│   │   │   ├── AnalyzeCommand.ps1
│   │   │   └── ReportCommand.ps1
│   │   │
│   │   ├── logging/                  # Логирование
│   │   │   ├── AsyncLogger.psm1
│   │   │   ├── LogFormatter.psm1
│   │   │   └── LogLevel.psm1
│   │   │
│   │   ├── validation/               # Валидация
│   │   │   ├── InputValidator.psm1
│   │   │   ├── DependencyValidator.psm1
│   │   │   └── SecurityValidator.psm1
│   │   │
│   │   ├── rollback/                 # Система отката
│   │   │   ├── RollbackManager.psm1
│   │   │   └── Transaction.psm1
│   │   │
│   │   ├── localization/             # Локализация
│   │   │   ├── LocalizationManager.psm1
│   │   │   ├── en-US/
│   │   │   └── ru-RU/
│   │   │
│   │   └── utilities/                # Утилиты
│   │       ├── FileSystem.psm1
│   │       ├── TemplateEngine.psm1
│   │       └── RetryHandler.psm1
│   │
│   ├── providers/                    # Провайдеры облачных сервисов
│   │   ├── azure/                    # Azure провайдер
│   │   │   ├── AzureProvider.psm1
│   │   │   ├── ResourceDeployer.psm1
│   │   │   └── Authenticator.psm1
│   │   │
│   │   ├── aws/                      # AWS провайдер (будущее)
│   │   └── gcp/                      # GCP провайдер (будущее)
│   │
│   ├── ai/                           # AI интеграции
│   │   ├── analyzers/                # Анализаторы
│   │   │   ├── StructureAnalyzer.psm1
│   │   │   ├── CodeAnalyzer.psm1
│   │   │   └── SecurityAnalyzer.psm1
│   │   │
│   │   ├── providers/                # AI провайдеры
│   │   │   ├── OpenAIIntegration.psm1
│   │   │   ├── ClaudeIntegration.psm1
│   │   │   └── LocalLLMIntegration.psm1
│   │   │
│   │   └── prompts/                  # Промпты и шаблоны
│   │       ├── structure-analysis/
│   │       └── code-review/
│   │
│   ├── infrastructure/               # Инфраструктурные модули
│   │   ├── monitoring/               # Мониторинг
│   │   │   ├── PrometheusClient.psm1
│   │   │   ├── MetricsCollector.psm1
│   │   │   └── HealthChecker.psm1
│   │   │
│   │   ├── messaging/                # Очереди и сообщения
│   │   │   ├── RabbitMQClient.psm1
│   │   │   ├── KafkaClient.psm1
│   │   │   └── EventDispatcher.psm1
│   │   │
│   │   ├── security/                 # Безопасность
│   │   │   ├── SecretManager.psm1
│   │   │   ├── VaultIntegration.psm1
│   │   │   └── EncryptionService.psm1
│   │   │
│   │   └── deployment/               # Деплоймент

l, \[17.01.2026 3:39\]
│   │       ├── TerraformManager.psm1
│   │       └── KubernetesDeployer.psm1
│   │
│   ├── templates/                    # Шаблоны проектов
│   │   ├── dotnet-webapi/           # .NET Web API шаблон
│   │   ├── nodejs-microservice/     # Node.js микросервис
│   │   ├── python-data/             # Python data проект
│   │   └── react-frontend/          # React фронтенд
│   │
│   └── web/                          # Веб-интерфейс (опционально)
│       ├── dashboard/               # Dashboard SPA
│       └── api/                     # Backend API
│
├── config/                           # Конфигурация
│   ├── environments/                 # Конфиги окружений
│   │   ├── development.json
│   │   ├── staging.json
│   │   └── production.json
│   │
│   ├── templates/                    # Шаблоны конфигов
│   │   ├── appsettings.template.json
│   │   └── docker-compose.template.yml
│   │
│   └── schema/                       # JSON схемы для валидации
│       └── config-schema.json
│
├── docs/                             # Документация
│   ├── api/                          # API документация
│   │   ├── reference/
│   │   └── examples/
│   │
│   ├── architecture/                 # Архитектура
│   │   ├── decisions/               # ADR (Architectural Decision Records)
│   │   └── diagrams/                # Диаграммы
│   │
│   ├── guides/                       # Руководства
│   │   ├── getting-started/
│   │   ├── deployment/
│   │   └── troubleshooting/
│   │
│   ├── specifications/               # Технические спецификации
│   └── translations/                 # Переводы документации
│
├── tests/                            # Тесты
│   ├── unit/                         # Юнит-тесты
│   │   ├── core/
│   │   ├── providers/
│   │   └── ai/
│   │
│   ├── integration/                  # Интеграционные тесты
│   │   ├── azure/
│   │   ├── monitoring/
│   │   └── security/
│   │
│   ├── e2e/                          # End-to-end тесты
│   │   ├── scenarios/
│   │   └── fixtures/
│   │
│   ├── performance/                  # Нагрузочные тесты
│   │   └── benchmarks/
│   │
│   └── test-data/                    # Данные для тестов
│       └── mocks/
│
├── scripts/                          # Вспомогательные скрипты
│   ├── build/                        # Скрипты сборки
│   │   ├── build.ps1
│   │   ├── pack.ps1
│   │   └── publish.ps1
│   │
│   ├── dev/                          # Скрипты для разработки
│   │   ├── setup-dev.ps1
│   │   ├── start-dependencies.ps1
│   │   └── codegen.ps1
│   │
│   ├── deployment/                   # Скрипты деплоя
│   │   ├── deploy-azure.ps1
│   │   └── deploy-kubernetes.ps1
│   │
│   └── maintenance/                  # Скрипты обслуживания
│       ├── cleanup.ps1
│       └── update-deps.ps1
│
├── tools/                            # Инструменты и утилиты
│   ├── code-analysis/                # Анализ кода
│   │   ├── lint.ps1
│   │   └── complexity-check.ps1
│   │
│   ├── migration/                    # Миграционные инструменты
│   └── diagnostics/                  # Диагностические утилиты
│
├── infrastructure/                   # Инфраструктура как код
│   ├── terraform/                    # Terraform конфигурации
│   │   ├── modules/                  # Переиспользуемые модули
│   │   ├── environments/             # Конфиги окружений
│   │   └── state/                    # Бэкенд для state файлов
│   │
│   ├── kubernetes/                   # Kubernetes манифесты
│   │   ├── base/                     # Базовые ресурсы
│   │   ├── overlays/                 # Оверлеи для окружений
│   │   └── helm/                     # Helm charts
│   │
│   ├── docker/                       # Docker конфигурации
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   │
│   └── monitoring/                   # Мониторинг инфраструктуры

l, \[17.01.2026 3:39\]
│       ├── prometheus/
│       └── grafana/
│
├── samples/                          # Примеры использования
│   ├── quickstart/                   # Быстрый старт
│   ├── tutorials/                    # Пошаговые руководства
│   └── advanced/                     # Продвинутые сценарии
│
├── packages/                         # Пакеты для распространения
│   ├── nuget/                        # NuGet пакеты
│   ├── npm/                          # NPM пакеты
│   └── pypi/                         # PyPI пакеты
│
├── .env.example                      # Шаблон переменных окружения
├── .gitignore                        # Git ignore правила
├── .gitattributes                    # Git атрибуты
├── .editorconfig                     # Настройки редактора
├── .prettierrc                       # Prettier конфиг
├── .eslintrc.json                    # ESLint конфиг
├── .powershell-psscriptanalyzer.psd1 # PSScriptAnalyzer конфиг
├── LICENSE                           # Лицензия
├── [README.md](http://README.md)                         # Основной README
├── [CONTRIBUTING.md](http://CONTRIBUTING.md)                   # Руководство для контрибьюторов
├── [CHANGELOG.md](http://CHANGELOG.md)                      # История изменений
├── [SECURITY.md](http://SECURITY.md)                       # Политика безопасности
├── CODE\_OF\_CONDUCT.md                # Кодекс поведения
├── arch-compass.psd1                 # Манифест модуля PowerShell
├── requirements.txt                  # Python зависимости
├── package.json                      # Node.js зависимости
└── Directory.Build.props             # Общие настройки сборки .NET