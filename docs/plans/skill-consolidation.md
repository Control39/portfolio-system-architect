# Карта навыков и анализ дублирования

> **Дата:** 18 мая 2026 г.  
> **Цель:** Выявить дублирование навыков между инструментами и консолидировать

---

## 📊 Обзор инструментов

| Инструмент | Расположение | Кол-во навыков | Назначение |
|------------|--------------|----------------|------------|
| **SourceCraft** | `.sourcecraft/skills/` | 1 | YAML-конфигурация для CI/CD |
| **Codeassistant** | `codeassistant/skills/` | 14 | Специализированные навыки для ИИ-агента |
| **Koda** | `.koda/skills/` | 0 | (удалены/перемещены) |

---

## 🔍 Детальный анализ навыков

### Codeassistant Skills (14 навыков)

| Навык | Описание | Дублируется? | Примечание |
|-------|----------|--------------|------------|
| **architect-analize** | Анализ архитектуры | ⚠️ Частично | Аналог: repo-audit-assistant |
| **caa-audit** | Аудит Cognitive Agent | ❌ Нет | Уникальный |
| **career** | Карьерное развитие | ❌ Нет | Уникальный |
| **code** | Качество кода | ⚠️ Частично | Аналог: security + repo-audit |
| **extension-stack-analyzer** | Анализ стека расширений | ❌ Нет | Уникальный |
| **integrity-checker** | Проверка целостности | ⚠️ Частично | Аналог: repo-audit |
| **it-compass** | Методология IT-Compass | ❌ Нет | Уникальный |
| **job-market** | Анализ рынка труда | ❌ Нет | Уникальный |
| **knowledge** | RAG-поиск по знаниям | ❌ Нет | Уникальный |
| **personal-branding** | Личный бренд | ❌ Нет | Уникальный |
| **security** | Безопасность | ⚠️ Частично | Аналог: code (частично) |
| **seo** | SEO-оптимизация | ❌ Нет | Уникальный |
| **teacher** | Обучение и наставничество | ❌ Нет | Уникальный |
| **vscode-health-check** | Проверка VS Code | ❌ Нет | Уникальный |

### SourceCraft Skills (1 навык)

| Навык | Описание | Дублируется? | Примечание |
|-------|----------|--------------|------------|
| **repo-audit-assistant** | Аудит репозитория | ⚠️ Да | Дублирует: architect-analize, integrity-checker, code, security |

---

## 🚨 Выявленные дублирования

### 1. Аудит репозитория (HIGH PRIORITY)

**Дублирующиеся навыки:**
- `codeassistant/architect-analize` — анализ архитектуры
- `codeassistant/integrity-checker` — проверка целостности
- `codeassistant/code` — качество кода (частично)
- `codeassistant/security` — безопасность (частично)
- `.sourcecraft/repo-audit-assistant` — полный аудит

**Проблема:**
- Разные форматы (YAML vs Markdown)
- Разные триггеры (CI/CD vs IDE)
- Перекрытие функциональности (60-70%)

**Решение:**
```
Консолидация в единый модуль:
shared-skills/repository-audit/
├── README.md           # Документация
├── config.yaml         # Конфигурация (YAML для CI/CD)
├── instructions.md     # Инструкции для ИИ (Markdown)
├── tools/
│   ├── analyzer.py     # Анализ архитектуры
│   ├── integrity.py    # Проверка целостности
│   ├── code-quality.py # Качество кода
│   └── security.py     # Безопасность
└── templates/
    ├── pr-comment.md   # Шаблон комментария к PR
    └── audit-report.md # Шаблон отчёта
```

### 2. Качество кода и безопасность (MEDIUM PRIORITY)

**Дублирующиеся навыки:**
- `codeassistant/code` — качество кода (включает безопасность)
- `codeassistant/security` — безопасность (включает качество)

**Проблема:**
- Перекрытие в проверках SQL injection, валидации, секретах
- Разные акценты (архитектура vs безопасность)

**Решение:**
```
Разделение ответственности:
shared-skills/code-quality/
├── instructions.md      # Архитектурные аспекты, ADR, контракты
└── tools/
    ├── architecture.py  # Проверка соответствия ADR
    ├── contracts.py     # Проверка интерфейсов
    └── observability.py # Логирование, метрики, health checks

shared-skills/security/
├── instructions.md      # Security by Design, CI/CD, Network
└── tools/
    ├── secrets.py       # Проверка секретов
    ├── dependencies.py  # Сканирование зависимостей
    └── network.py       # Network policies, TLS
```

---

## 🎯 Стратегия консолидации

### Phase 1: Создание shared-skills (1-2 недели)

**Цель:** Единая библиотека навыков, используемая всеми инструментами

**Структура:**
```
shared-skills/
├── repository-audit/        # Консолидированный аудит
├── code-quality/            # Качество кода (архитектура)
├── security/                # Безопасность
├── it-compass/              # Методология (уже уникальная)
├── career/                  # Карьера (уже уникальная)
├── teacher/                 # Обучение (уже уникальная)
└── ... (остальные уникальные)
```

**Преимущества:**
- Один источник правды (Single Source of Truth)
- Легко поддерживать
- Все инструменты используют одинаковую логику
- Уменьшение дублирования на 60%

### Phase 2: Миграция инструментов (2-3 недели)

**Codeassistant:**
```yaml
# codeassistant/mcp.json
{
  "skills": {
    "repository-audit": {
      "source": "shared-skills/repository-audit",
      "enabled": true
    },
    "code-quality": {
      "source": "shared-skills/code-quality",
      "enabled": true
    },
    "security": {
      "source": "shared-skills/security",
      "enabled": true
    }
  }
}
```

**SourceCraft:**
```yaml
# .sourcecraft/skills/repository-audit.yml
# Ссылается на shared-skills/repository-audit/config.yaml
```

**Koda:**
```yaml
# .koda/profiles/default.yaml
{
  "skills": [
    {"name": "repository-audit", "source": "shared-skills/repository-audit"},
    {"name": "code-quality", "source": "shared-skills/code-quality"}
  ]
}
```

### Phase 3: Удаление дубликатов (1 неделя)

**Удалить:**
- `codeassistant/skills/architect-analize/` → переместить в shared-skills
- `codeassistant/skills/integrity-checker/` → переместить в shared-skills
- `codeassistant/skills/code/` → переработать в shared-skills/code-quality
- `codeassistant/skills/security/` → переработать в shared-skills/security
- `.sourcecraft/skills/repo-audit-assistant.yml` → переместить в shared-skills

**Сохранить (уникальные):**
- `caa-audit/`
- `career/`
- `extension-stack-analyzer/`
- `it-compass/`
- `job-market/`
- `knowledge/`
- `personal-branding/`
- `seo/`
- `teacher/`
- `vscode-health-check/`

---

## 📈 Ожидаемые результаты

| Метрика | До | После | Изменение |
|---------|-----|-------|-----------|
| **Общее кол-во навыков** | 15 | 10 | -33% |
| **Дублирование** | 4 навыка (27%) | 0 | -100% |
| **Время на поддержку** | Высокое | Низкое | -50% |
| **Консистентность** | Средняя | Высокая | +100% |
| **Время на добавление навыка** | 2-3 дня | 1 день | -50% |

---

## 🛠️ План действий

### Week 1: Подготовка

- [ ] Создать структуру `shared-skills/`
- [ ] Выделить общие компоненты из дублирующих навыков
- [ ] Создать `repository-audit/` (консолидация 4 навыков)
- [ ] Создать `code-quality/` и `security/` (разделение)
- [ ] Написать документацию для новых модулей

### Week 2: Миграция

- [ ] Обновить `codeassistant/mcp.json` для использования shared-skills
- [ ] Обновить `.sourcecraft/skills/` для использования shared-skills
- [ ] Обновить `.koda/profiles/` для использования shared-skills
- [ ] Протестировать все инструменты с новыми навыками

### Week 3: Очистка

- [ ] Удалить дублирующиеся навыки из `codeassistant/skills/`
- [ ] Удалить `.sourcecraft/skills/repo-audit-assistant.yml`
- [ ] Обновить README и документацию
- [ ] Запустить регрессионное тестирование

---

## 📝 Примечания

**Риски:**
- Временное нарушение работы инструментов во время миграции
- Необходимость обновления конфигураций во всех местах

**Митигация:**
- Мигрировать по одному модулю за раз
- Тестировать после каждого шага
- Сохранить бэкапы старых навыков

**Приоритет:**
1. **HIGH:** `repository-audit` — biggest duplication (4 навыка)
2. **MEDIUM:** `code-quality` + `security` — частичное перекрытие
3. **LOW:** Уникальные навыки — не трогать

---

*Последнее обновление: 18 мая 2026 г.*
