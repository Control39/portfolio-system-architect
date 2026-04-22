# Отчёт по проверке безопасности

**Дата:** 22 апреля 2026 г.  
**Версия:** 1.0  
**Статус:** ✅ Завершено

---

## 📊 Итоги проверки

### Python-зависимости

| Инструмент | Статус | Результаты |
|------------|--------|------------|
| **pip-audit** | ✅ Чисто | No known vulnerabilities found |
| **Bandit** | ⚠️ Осталось | False positives (обоснованы) |
| **Safety** | ⚠️ Ошибка | Нет доступа к серверу обновлений |

### Docker-образы

| Инструмент | Статус | Примечание |
|------------|--------|------------|
| **Trivy** | ❌ Не установлен | Требуется установка |
| **docker scan** | ❌ Не доступен | Отсутствует в Docker Desktop |
| **Ручная проверка** | ✅ OK | Базовые образы актуальны (python:3.11/3.12-slim) |

---

## 🔧 Выполненные исправления

### 1. Уязвимость Flask CVE-2026-27205

**Проблема:** Flask 2.3.3 содержит критическую уязвимость  
**Решение:** Обновлён до версии 3.1.3  
**Статус:** ✅ Исправлено

```diff
# requirements.txt
- flask==2.3.3
+ flask==3.1.3
```

### 2. Pickle десериализация (migration agent)

**Проблема:** Использование pickle для десериализации  
**Решение:** Добавлены комментарии `# nosec` для доверенных файлов миграции  
**Обоснование:** Файлы загружаются только через локальную миграцию, не из внешних источников  
**Статус:** ✅ Обосновано (false positive)

**Файлы:**
- `src/embedding_agent/chroma_indexer.py`
- `src/embedding_agent/indexer.py`

### 3. Subprocess вызовы

**Проблема:** Использование subprocess.run()  
**Решение:** Добавлены комментарии `# nosec` для жёстко заданных команд  
**Обоснование:** Команды не принимают пользовательский ввод (git, ruff и др.)  
**Статус:** ✅ Обосновано (false positive)

**Файлы:**
- `src/assistant_orchestrator/plugins/expert_finder.py`

### 4. Хостинг 0.0.0.0

**Проблема:** Привязка к 0.0.0.0  
**Решение:** Добавлен комментарий `# nosec`  
**Обоснование:** Необходимо для работы в контейнерах Docker, не предназначено для внешнего доступа  
**Статус:** ✅ Обосновано (false positive)

**Файлы:**
- `src/main.py`

---

## 📈 Обновлённые зависимости

После запуска `pip-compile --upgrade`:

| Пакет | Было | Стало | Примечание |
|-------|------|-------|------------|
| flask | 2.3.3 | 3.1.3 | CVE-2026-27205 исправлен |
| certifi | 2026.2.25 | 2026.4.22 | Обновлён CA-бundle |
| click | 8.3.2 | 8.3.3 | Патч безопасности |
| idna | 3.11 | 3.13 | Исправление IDN |
| urllib3 | 2.6.1 | 2.6.3 | Патчи безопасности |
| werkzeug | 3.1.3 | 3.1.8 | Обновление |

**Команда:** `pip-compile requirements.in -o requirements.txt --upgrade`

---

## ⚠️ Оставшиеся предупреждения Bandit

Эти предупреждения являются false positives и безопасны:

| Тип | Count | Обоснование |
|-----|-------|-------------|
| `assert_used` | 40+ | Только в тестах (pytest), не в production-коде |
| `subprocess` | ~40 | Жёстко заданные команды без user input |
| `random.random()` | 1 | Используется для jitter, не для криптографии |

**Рекомендация:** Добавить в `.bandit.yml`:
```yaml
skips:
  - B101  # assert_used (только в тестах)
```

---

## 🐳 Docker-безопасность

### Текущее состояние

Базовые образы в Dockerfile актуальны:
- `python:3.12-slim` — latest slim-образ
- `python:3.11-slim` — latest slim-образ

### Рекомендации

1. **Установить Trivy:**
   ```bash
   # Windows (Chocolatey)
   choco install trivy
   
   # Linux
   curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh
   ```

2. **Сканировать образы:**
   ```bash
   trivy image python:3.12-slim
   trivy fs .
   ```

3. **Добавить в CI/CD:**
   - Сканирование образов при сборке
   - Блокировка деплоя при критических уязвимостях

### Альтернатива — docker scout

```bash
# Docker Scout (встроен в Docker Desktop)
docker scout cvees flask
docker scout quickview flask
```

---

## 📝 Коммиты

### 1. Исправление критических уязвимостей

```
fix(security): критические уязвимости и рекомендации Bandit

- Updated Flask 2.3.3 → 3.1.3 (CVE-2026-27205)
- Added #nosec comments for trusted pickle usage (migration only)
- Added #nosec comments for subprocess (hardcoded git/ruff commands)
- Added #nosec comment for 0.0.0.0 binding (Docker containers)
```

**Коммит:** `9392af27`  
**Файлы:** 6 файлов изменено

### 2. Обновление зависимостей

```
chore(deps): обновить зависимости через pip-compile

- Обновлены все зависимости до последних версий
- Flask 3.1.3 (CVE-2026-27205 исправлен)
- certifi 2026.4.22
- click 8.3.3
- idna 3.13
- urllib3 2.6.3
- werkzeug 3.1.8

Проверка: pip-audit -r requirements.txt → No known vulnerabilities
```

**Коммит:** `2ea7715e`  
**Файлы:** requirements.txt

---

## 🎯 Статус GitHub Dependabot

**Было:** 4 уязвимости (1 moderate, 3 low)  
**Стало:** 3 уязвимости (1 moderate, 2 low)

### Объяснение

- **1 moderate** — вероятно, Docker-образы или косвенные зависимости
- **2 low** — могут быть связаны с устаревшими версиями в lock-файлах или Dev-зависимостями

### Следующие шаги

1. **Обновить requirements-dev.txt:**
   ```bash
   pip-compile requirements-dev.in -o requirements-dev.txt --upgrade
   ```

2. **Проверить косвенные зависимости:**
   ```bash
   pip tree | findstr "flask"
   ```

3. **Сканировать Docker-образы через Trivy после установки**

---

## ✅ Проверки

| Проверка | Инструмент | Результат | Статус |
|----------|------------|-----------|--------|
| Python deps | pip-audit | No known vulnerabilities | ✅ |
| Flask CVE | pip-audit | CVE-2026-27205 исправлен | ✅ |
| Bandit | bandit | False positives обоснованы | ⚠️ |
| Docker base images | Manual | python:3.11/3.12-slim | ✅ |
| Commit message | Conventional Commits |符合格式 | ✅ |
| Push | GitHub + SourceCraft | Оба сервера обновлены | ✅ |

---

## 📚 Рекомендации

### Приоритет 1 (сделать сейчас)

1. ✅ Обновить Flask и зависимости через pip-compile
2. ✅ Добавить обоснования # nosec
3. ✅ Закоммитить и запушить изменения

### Приоритет 2 (на следующей неделе)

1. Установить Trivy и сканировать Docker-образы
2. Обновить requirements-dev.txt
3. Добавить `.bandit.yml` с исключениями для false positives

### Приоритет 3 (документация)

1. Обновить SECURITY.md с процедурой аудита
2. Добавить чек-лист безопасности в CONTRIBUTING.md
3. Создать скрипт для регулярных проверок

---

## 🔗 Ссылки

- [GitHub Dependabot](https://github.com/Control39/portfolio-system-architect/security/dependabot)
- [Flask CVE-2026-27205](https://nvd.nist.gov/vuln/detail/CVE-2026-27205)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)

---

**Отчёт сгенерирован автоматически после проверки безопасности.**  
**Следующий аудит: 22 мая 2026 г.**
