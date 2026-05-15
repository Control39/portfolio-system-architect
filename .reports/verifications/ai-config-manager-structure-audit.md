# AI Config Manager - Структура и Верификация

**Дата:** 15 мая 2026 г.  
**Тип:** Аудит структуры папки  
**Статус:** ❌ Несоответствие обнаружено

---

## 📊 Ожидаемая структура (по README)

```
apps/ai-config-manager/
├── src/                    # Main application code
│   ├── __init__.py
│   └── main.py
├── config/                 # Configuration files
│   ├── __init__.py
│   └── default.yaml
├── tests/                  # Test files
│   ├── __init__.py
│   ├── test_basic.py       # 15 тестов
│   └── test_integration_ai_config_manager.py
├── docs/
├── README.md
├── requirements.txt        # Python dependencies
└── Dockerfile
```

**Тип:** Python-модуль (Shared Library)  
**Тесты:** 15 Python-тестов (pytest)  
**Статус:** Production Ready (по README)

---

## 🔍 Реальная структура (факт)

```
apps/ai-config-manager/
├── __tests__/              # JavaScript тесты
├── adapters/               # Адаптеры
├── ai-config-mobile/       # Мобильная версия?
├── api/                    # API слой
├── components/             # UI компоненты (Electron)
├── config/                 # Конфигурации
├── main/                   # Electron main process
│   └── index.js
├── models/                 # Модели данных
├── public/                 # Статические файлы
├── renderer/               # Electron renderer (GUI)
├── scripts/                # Скрипты
├── services/               # Сервисы
├── src/                    # Python + JavaScript микс
│   ├── __tests__/
│   ├── adapters/
│   ├── components/
│   ├── main/
│   ├── renderer/
│   └── preload.js
├── tests/                  # Смешанные тесты
│   ├── __init__.py
│   ├── config.test.js      # JavaScript тест
│   └── test_config.py      # Python тест
├── utils/                  # Утилиты
├── master-config.yaml      # Конфигурация
├── package.json            # Node.js зависимости
├── package-lock.json
├── preload.js              # Electron preload
└── README.md
```

**Тип:** Electron-приложение (Node.js + GUI)  
**Зависимости:** express, socket.io, electron, js-yaml  
**Тесты:** Смешанные (1 Python + несколько JS)

---

## ❌ Несоответствия

| Элемент | Ожидается (README) | Реальность | Статус |
|---------|-------------------|------------|--------|
| **Тип проекта** | Python-модуль | Electron-приложение (Node.js) | ❌ |
| **Зависимости** | pytest, requirements.txt | express, socket.io, electron, package.json | ❌ |
| **Тесты** | 15 Python-тестов | 1 Python + JS-тесты | ❌ |
| **Структура src/** | `src/main.py` | `src/` + `main/` + `renderer/` | ❌ |
| **Dockerfile** | Должен быть | Отсутствует | ❌ |
| **requirements.txt** | Должен быть | Отсутствует | ❌ |
| **docs/** | Должен быть | Отсутствует | ❌ |

---

## 🔴 Критические проблемы

### 1. **Неверный тип проекта**
- **README описывает:** Python-библиотеку для импорта в другие сервисы
- **Фактически:** Electron-приложение с GUI для управления конфигурациями

### 2. **Отсутствуют ключевые файлы**
- `requirements.txt` — нет Python-зависимостей
- `Dockerfile` — нет контейнеризации
- `docs/` — нет документации

### 3. **Смешанные технологии**
- `src/` содержит и Python (`__init__.py`), и JavaScript (`preload.js`)
- `tests/` содержит и `.py`, и `.js` файлы
- Нет четкого разделения между Python-библиотекой и Electron-GUI

### 4. **Тесты не соответствуют README**
- Обещано: 15 Python-тестов
- Факт: 1 Python-тест (`test_config.py`) + JS-тесты

---

## 📁 Детальная структура (факт)

### Корневые файлы:
| Файл | Назначение |
|------|------------|
| `package.json` | Node.js зависимости (express, socket.io, electron) |
| `package-lock.json` | Замороженные зависимости |
| `master-config.yaml` | Основная конфигурация |
| `preload.js` | Electron preload script |
| `README.md` | Документация (устарела) |

### Директории:
| Папка | Содержимое |
|-------|------------|
| `main/` | Electron main process (`index.js`) |
| `renderer/` | Electron GUI (renderer process) |
| `components/` | UI компоненты |
| `services/` | Бизнес-логика |
| `api/` | API слой |
| `models/` | Модели данных |
| `adapters/` | Адаптеры внешних сервисов |
| `config/` | Конфигурационные файлы |
| `utils/` | Утилиты |
| `scripts/` | Скрипты автоматизации |
| `tests/` | Тесты (1 Python + JS) |
| `__tests__/` | Дополнительные JS-тесты |
| `src/` | Смешанный код (Python + JS) |
| `ai-config-mobile/` | Мобильная версия (нужно проверить) |
| `public/` | Статические файлы |

---

## 🎯 Рекомендации

### Приоритет 1: Определить назначение
1. **Вариант А:** Оставить как Electron-GUI
   - Удалить Python-элементы из `src/`
   - Обновить README под Electron-приложение
   - Добавить `Dockerfile` для GUI (если нужно)

2. **Вариант Б:** Разделить на два проекта
   - `ai-config-core/` — Python-библиотека (из `config/`)
   - `ai-config-gui/` — Electron-приложение (остальное)

### Приоритет 2: Исправить документацию
- Обновить `README.md` с реальной структурой
- Добавить описание архитектуры (Electron + Node.js)
- Указать реальные команды запуска (`npm start`, `npm run dev`)

### Приоритет 3: Добавить недостающее
- `requirements.txt` (если есть Python-код)
- `Dockerfile` (для контейнеризации)
- `docs/` (архитектурная документация)
- Тесты (до 15+ для соответствия заявленному)

---

## 📊 Метрики

| Показатель | Значение |
|------------|----------|
| Файлов в корне | 15 |
| Директорий | 14 |
| Python-файлов | ~5 (оценка) |
| JavaScript-файлов | ~50+ (оценка) |
| Тестов Python | 1 |
| Тестов JavaScript | 5+ (оценка) |
| Покрытие тестами | <5% (оценка) |

---

## 🔗 Связанные файлы

- `.vscode/tasks.json` — задача `npm: start - apps/ai-config-manager` (устарела, перенесена в `client`)
- `docker-compose.yml` — нет сервиса для ai-config-manager
- `deployment/` — нет Kubernetes манифестов

---

*Отчет сгенерирован: 15 мая 2026 г.*  
*Версия: 1.0*  
*Расположение: .reports/verifications/ai-config-manager-structure-audit.md*
