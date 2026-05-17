# Consolidation of Duplicated Skills

> **Дата:** 18 мая 2026
> **Приоритет:** TIER 2
> **Статус:** Анализ завершён

---

## 📊 Текущее состояние

### Skills в 3 местах:

| Инструмент | Путь | Количество | Назначение |
|------------|------|------------|------------|
| **Koda** | `.koda/skills/` | 5 | IDE code intelligence |
| **Sourcecraft** | `.sourcecraft/skills/` | 1 (YAML) | Repo audit assistant |
| **Codeassistant** | `codeassistant/skills/` | 18 | Code automation & analysis |

---

## 🔍 Дублирование

### Skills в .koda/skills/ (5):
1. `code-security-auditor`
2. `devops-ci-cd`
3. `git-health-check`
4. `performance-profiler`
5. `repo-quality-auditor`

### Дубликаты в codeassistant/skills/ (5):
1. `code-security-auditor` ❌
2. `devops-ci-cd` ❌
3. `git-health-check` ❌
4. `performance-profiler` ❌
5. `repo-quality-auditor` ❌

**Итого:** 5 дублирующихся skills (26% от общего количества)

---

## 🎯 Уникальные skills в codeassistant/

| Skill | Назначение | Переносить? |
|-------|------------|-------------|
| `architect-analize` | Анализ архитектуры | ✅ Да |
| `caa-audit` | Audit CAA | ✅ Да |
| `career` | Карьерное развитие | ✅ Да |
| `code` | Общая кодовая помощь | ✅ Да |
| `extension-stack-analyzer` | Анализ стека | ✅ Да |
| `integrity-checker` | Проверка целостности | ✅ Да |
| `it-compass` | Методология IT-compass | ✅ Да |
| `job-market` | Анализ рынка труда | ✅ Да |
| `knowledge` | Управление знаниями | ✅ Да |
| `personal-branding` | Личный бренд | ✅ Да |
| `security` | Безопасность (общая) | ✅ Да |
| `seo` | SEO оптимизация | ✅ Да |
| `teacher` | Обучение | ✅ Да |
| `vscode-health-check` | Проверка VS Code | ⚠️ Дубликат git-health-check? |

---

## 📋 План консолидации

### Шаг 1: Создать `shared-skills/` (1 час)

```
shared-skills/
├── code-security-auditor/
├── devops-ci-cd/
├── git-health-check/
├── performance-profiler/
├── repo-quality-auditor/
└── README.md (документация всех навыков)
```

**Действия:**
- Перенести 5 дублирующихся skills в `shared-skills/`
- Создать симлинки в `.koda/skills/` и `codeassistant/skills/`
- Или использовать один источник для обоих

---

### Шаг 2: Определить роли (30 мин)

| Инструмент | Роль | Skills |
|------------|------|--------|
| **Koda** | IDE code intelligence | 5 общих + 15 уникальных |
| **Codeassistant** | Code automation | 18 уникальных + 5 общих |
| **Sourcecraft** | Repo audit (устаревает?) | 1 (объединить с codeassistant) |

---

### Шаг 3: Удалить дубликаты (1 час)

```bash
# Удалить дубликаты из codeassistant/
rm -rf codeassistant/skills/code-security-auditor
rm -rf codeassistant/skills/devops-ci-cd
rm -rf codeassistant/skills/git-health-check
rm -rf codeassistant/skills/performance-profiler
rm -rf codeassistant/skills/repo-quality-auditor

# Создать симлинки или использовать shared-skills
ln -s ../../shared-skills/code-security-auditor codeassistant/skills/
```

---

### Шаг 4: Обработать Sourcecraft (30 мин)

**Вариант A:** Объединить с codeassistant
```bash
mv .sourcecraft/skills/repo-audit-assistant.yml codeassistant/skills/
rm -rf .sourcecraft/skills/
```

**Вариант B:** Удалить (если не используется)
```bash
rm -rf .sourcecraft/
```

---

## 🎯 Ожидаемый результат

| Метрика | До | После |
|---------|-----|-------|
| Общее количество skills | 24 | 19 |
| Дубликаты | 5 | 0 |
| Мест хранения | 3 | 2 (shared + unique) |
| Сложность поддержки | Высокая | Средняя |

---

## ⏱️ Оценка времени

| Задача | Время |
|--------|-------|
| Анализ | ✅ Готово |
| Создание shared-skills/ | 1 час |
| Перенос дубликатов | 30 мин |
| Создание симлинков | 30 мин |
| Удаление дубликатов | 30 мин |
| Обработка Sourcecraft | 30 мин |
| Тестирование | 30 мин |
| **Всего** | **~4 часа** |

---

## 🚀 Следующие шаги

1. [ ] Создать `shared-skills/`
2. [ ] Перенести 5 дублирующихся skills
3. [ ] Создать симлинки в .koda/ и codeassistant/
4. [ ] Удалить дубликаты из codeassistant/
5. [ ] Решить судьбу Sourcecraft
6. [ ] Обновить документацию
7. [ ] Протестировать работу всех инструментов

---

*Last updated: 18 мая 2026*
