# Consolidation of Configuration Files

> **Дата:** 18 мая 2026
> **Приоритет:** TIER 2 #2
> **Статус:** Анализ завершён

---

## 📊 Текущее состояние

### Конфигурации в 8 местах:

| Путь | Назначение | Количество файлов | Примеры |
|------|------------|-------------------|---------|
| **`config/`** | ✅ AI Config Manager | 1 (ai-config.yaml) | Центральная AI конфиг |
| **`src/config/`** | Shared config (устаревает) | ~5 | Base settings |
| **`apps/*/config/`** | Локальные конфиги сервисов | 8+ | Docker, K8s, app configs |
| **`scripts/dev/config/`** | Dev скрипты | 3 | Dev environment |
| **`tools/utilities/configs/`** | Tools | 4 | Tool-specific |

---

## 🎯 Цель

**Single Source of Truth:**
```
config/
├── base/              # Общие настройки для всех
├── services/          # Пер-сервис конфиги (ссылаются на base/)
├── deployment/        # Docker, K8s, Cloud
├── tools/             # Tool-specific (Koda, Continue, VSCode)
├── ai/                # AI модели, промпты, RAG
└── secrets/           # Sealed secrets (не в git)
```

---

## 🔍 Анализ дублирования

### Типы конфигураций:

| Тип | Где сейчас | Куда перенести | Статус |
|-----|------------|----------------|--------|
| **AI/LLM** | `config/ai-config.yaml` | `config/ai/` | ✅ Уже в центре |
| **CI/CD** | Разбросано | `config/ci-cd/` | ⚠️ Частично |
| **Docker** | `apps/*/Dockerfile` | `config/docker/` | ⚠️ Частично |
| **K8s** | `deployment/k8s/` | `config/deployment/k8s/` | ⚠️ Частично |
| **Dev env** | `scripts/dev/config/` | `config/base/dev/` | ❌ Нужно |
| **Tools** | `.koda/`, `.vscode/`, `codeassistant/` | `config/tools/` | ❌ Нужно |
| **Secrets** | `.env*`, `.secrets.baseline` | `config/secrets/` | ⚠️ Есть baseline |

---

## 📋 План консолидации

### Шаг 1: Создать структуру (30 мин)

```bash
mkdir -p config/{base,services,deployment,tools,ai,secrets}
mkdir -p config/base/{dev,staging,prod}
mkdir -p config/services/{cognitive-agent,decision-engine,etc}
mkdir -p config/deployment/{docker,k8s,cloud}
```

---

### Шаг 2: Перенести существующие конфиги (1 час)

**Из `src/config/`:**
```bash
mv src/config/*.yaml config/base/
mv src/config/*.json config/base/
```

**Из `apps/*/config/` (общие):**
```bash
# Для каждого сервиса копировать только уникальные
cp apps/*/config/docker-compose.yml config/deployment/docker/
cp apps/*/config/k8s/*.yaml config/deployment/k8s/
```

**Из `scripts/dev/config/`:**
```bash
mv scripts/dev/config/* config/base/dev/
```

**Из `tools/utilities/configs/`:**
```bash
mv tools/utilities/configs/* config/tools/
```

---

### Шаг 3: Обновить ссылки в сервисах (2 часа)

**До:**
```python
from apps.service_x.config import settings
```

**После:**
```python
from config.integration import get_service_config
config = get_service_config("service_x")
```

Или через симлинки:
```bash
ln -s ../../config/services/service_x apps/service_x/config
```

---

### Шаг 4: Создать `.gitignore` для secrets (15 мин)

```gitignore
# Secrets
config/secrets/*.yaml
config/secrets/*.json
.env
.env.local
*.key
```

---

### Шаг 5: Документация (30 мин)

Создать `config/README.md` с:
- Структурой директорий
- Правилами именования
- Примерами использования
- Процессом добавления новых конфигов

---

## 🎯 Ожидаемый результат

| Метрика | До | После | Улучшение |
|---------|-----|-------|-----------|
| Мест хранения конфигов | 8 | 1 | -88% |
| Дублирование конфигов | 15+ | 0 | -100% |
| Время поиска конфига | 10 мин | <1 мин | -90% |
| Сложность поддержки | Высокая | Низкая | ✅ |

---

## ⏱️ Оценка времени

| Задача | Время |
|--------|-------|
| Анализ | ✅ Готово |
| Создание структуры | 30 мин |
| Перенос конфигов | 1 час |
| Обновление ссылок | 2 часа |
| Настройка .gitignore | 15 мин |
| Документация | 30 мин |
| Тестирование | 1 час |
| **Всего** | **~5.5 часов** |

---

## 🚀 Следующие шаги

1. [ ] Создать структуру `config/{base,services,deployment,tools,ai,secrets}`
2. [ ] Перенести конфиги из `src/config/`, `apps/*/config/`, `scripts/dev/config/`
3. [ ] Обновить импорты в сервисах
4. [ ] Создать симлинки для обратной совместимости
5. [ ] Обновить `.gitignore`
6. [ ] Написать `config/README.md`
7. [ ] Протестировать все сервисы

---

## 📝 Примечания

- **AI Config Manager** уже использует `config/ai-config.yaml` как центральный источник
- **9/14 сервисов** уже мигрированы на использование AI Config Manager
- **Остальные 5** требуют доделывания main.py/app.py
- **Секреты** должны храниться в `config/secrets/` и **НЕ** коммититься в git

---

*Last updated: 18 мая 2026*
