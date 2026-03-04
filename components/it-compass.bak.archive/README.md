# IT Compass Component (Архивная версия)

Этот компонент является архивной копией оригинальной версии IT Compass с веб-интерфейсом и API-интеграциями.

## Назначение архива

Этот архив сохранен для:
- Сохранения истории разработки
- Доступа к оригинальным функциям веб-интерфейса
- Использования как референсной реализации при объединении с методологией

## Структура компонента

```
it-compass/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── tracker.py              # Основная система отслеживания
│   │   ├── api_integration.py     # Интеграция с внешними API
│   │   └── mental-support.py     # Психологическая поддержка
│   ├── data/
│   │   ├── __init__.py
│   │   ├── markers/
│   │   │   ├── ai_applications.json
│   │   │   ├── cloud_computing.json
│   │   │   ├── cybersecurity.json
│   │   │   ├── data_analysis.json
│   │   │   ├── database.json
│   │   │   ├── devops.json
│   │   │   ├── frontend.json
│   │   │   ├── mobile_development.json
│   │   │   ├── python.json
│   │   │   └── system_design.json
│   │   └── user_progress.json
│   ├── ui/
│   │   └── app.py                 # Веб-интерфейс (упрощенный)
│   └── utils/
│       ├── __init__.py
│       └── portfolio_gen.py        # Генератор портфолио
├── examples/
│   └── usage_example.py          # Пример использования
├── docs/
│   ├── ARCHITECTURE.md             # Архитектура компонента
│   ├── METHODOLOGY.md              # Методология
│   ├── PROJECT_ANALYSIS.md         # Анализ проекта
│   ├── SUPPORT_GUIDE.md           # Руководство по поддержке
│   └── context_for_ai_analysis.md   # Контекст для анализа ИИ
├── support/
│   ├── community_guide.md          # Руководство сообщества
│   ├── low_energy_mode.py          # Режим низкой энергии
│   └── resources/
│       ├── crisis_contacts.json
│       └── motivational_quotes.json
├── tests/
│   └── test_tracker.py              # Тесты для трекера
├── config/
│   └── settings.json                # Настройки компонента
├── requirements.txt               # Зависимости Python
├── setup.py                        # Скрипт установки
├── setup.sh                        # Скрипт установки (Linux/Mac)
├── Dockerfile                      # Docker конфигурация
├── LICENSE                         # Лицензия
└── README.md                      # Этот файл
```

## Примечание

Для получения актуальной версии IT Compass с объединенной функциональностью обратитесь к основному компоненту `it-compass`.