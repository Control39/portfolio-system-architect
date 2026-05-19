# Рекомендации по оптимизации GitHub Actions

## 🎯 Цель: Сократить с 27 до 10 workflow файлов

---

## ❌ **Удалить сразу (9 файлов)**

| Файл | Причина |
|------|---------|
| `mirror-to-sourcecraft.yml.disabled` | Устарел, есть новый `mirror-to-sourcecraft.yml` |
| `codeql.yml.disabled` | Неактивен, дублирует `security-scan.yml` |
| `monitoring-alerts.yml.disabled` | Неактивен, не используется |
| `rag-update.yml.disabled` | Неактивен, не используется |
| `agents-codeassistant-compatibility.yml` | Экспериментальный, не критичен |
| `ai-configs.yaml` | Не workflow (расширение .yaml, не .yml) |
| `duplicate-check.yml` | Лишний, есть pre-commit hooks |
| `vscode-extensions-check.yml` | Не критичен для CI/CD |
| `test-decision-engine.yml` | Дублирует `cognitive-agent-ci.yml` |

---

## ⚠️ **Объединить или удалить (8 файлов)**

| Файл | Решение |
|------|---------|
| `mirror-sync-enhanced.yml` | **Заменить** новым простым workflow (уже создан) |
| `monitor-mirror-discrepancies.yml` | Дублирует mirror-sync, удалить после включения нового |
| `deploy-k8s.yml` | Объединить с `deploy.yml` (уже есть K8s деплой) |
| `deploy-dashboard.yml` | Проверить, дублирует ли `update-metrics.yml` |
| `update-metrics.yml` | Проверить, дублирует ли `deploy-dashboard.yml` |
| `update.yml` | Проверить назначение (возможно, дублирует `update-metrics.yml`) |
| `docs.yml` | Дублирует `deploy.yml` (оба деплоят MkDocs) |
| `service-structure.yml` | Проверить, нужен ли отдельно от `ci.yml` |

---

## ✅ **Оставить (10 файлов)**

| Файл | Назначение |
|------|------------|
| `ci.yml` | Основной тест & coverage |
| `security-scan.yml` | Trivy, Bandit, Sealed Secrets |
| `code-quality.yml` | Ruff, Black, MyPy |
| `deploy.yml` | Deploy MkDocs + K8s (по тегам) |
| `mirror-to-sourcecraft.yml` | **НОВЫЙ** — зеркало на SourceCraft |
| `release.yml` | Релизы и GitHub Releases |
| `dependabot-auto-merge.yml` | Автоматический merge dependabot PR |
| `cognitive-agent-ci.yml` | **Упрощённый** — только на push к cognitive-agent |
| `badge-health-monitor.yml` | Мониторинг health badges |
| `archive/` | Переместить удалённые workflow в `archive/` |

---

## 📋 **План действий**

### Шаг 1: Удалить 9 очевидных дубликатов
```powershell
# Переместить в archive (для безопасности)
New-Item -ItemType Directory -Force .github\workflows\archive
Move-Item .github\workflows\mirror-to-sourcecraft.yml.disabled .github\workflows\archive\
Move-Item .github\workflows\codeql.yml.disabled .github\workflows\archive\
Move-Item .github\workflows\monitoring-alerts.yml.disabled .github\workflows\archive\
Move-Item .github\workflows\rag-update.yml.disabled .github\workflows\archive\
Move-Item .github\workflows\agents-codeassistant-compatibility.yml .github\workflows\archive\
Move-Item .github\workflows\ai-configs.yaml .github\workflows\archive\
Move-Item .github\workflows\duplicate-check.yml .github\workflows\archive\
Move-Item .github\workflows\vscode-extensions-check.yml .github\workflows\archive\
Move-Item .github\workflows\test-decision-engine.yml .github\workflows\archive\
```

### Шаг 2: Удалить mirror-sync-enhanced.yml (заменён новым)
```powershell
Move-Item .github\workflows\mirror-sync-enhanced.yml .github\workflows\archive\
Move-Item .github\workflows\monitor-mirror-discrepancies.yml .github\workflows\archive\
```

### Шаг 3: Проверить дубликаты деплоя
```powershell
# Сравнить deploy.yml и docs.yml
git diff .github/workflows/deploy.yml .github/workflows/docs.yml

# Сравнить deploy-dashboard.yml и update-metrics.yml
git diff .github/workflows/deploy-dashboard.yml .github/workflows/update-metrics.yml
```

### Шаг 4: Упростить cognitive-agent-ci.yml
- Убрать schedule trigger
- Убрать monitor-quotas job
- Оставить только тесты на push/pull_request

---

## 🔍 **Детальный анализ оставшихся workflow**

### deploy.yml vs docs.yml
**deploy.yml:**
- Деплоит MkDocs на GitHub Pages
- Деплоит K8s по тегам

**docs.yml:**
- Нужно проверить содержимое

**Рекомендация:** Если docs.yml тоже деплоит MkDocs — удалить, оставить deploy.yml

### deploy-dashboard.yml vs update-metrics.yml
**Нужно проверить:**
- Что делает deploy-dashboard.yml?
- Что делает update-metrics.yml?
- Есть ли overlap?

### update.yml
**Нужно проверить:**
- Назначение файла
- Дублирует ли update-metrics.yml?

### service-structure.yml
**Нужно проверить:**
- Проверяет ли структуру сервисов?
- Можно ли объединить с ci.yml?

---

## 📊 **Ожидаемый результат**

| До оптимизации | После оптимизации |
|----------------|-------------------|
| 27 workflow | 10 workflow |
| 4 disabled | 0 disabled |
| 2 mirror workflow | 1 mirror workflow |
| ~500 строк YAML | ~250 строк YAML |

---

## ⚡ **Быстрая проверка**

```powershell
# Подсчитать workflow
Get-ChildItem .github\workflows\*.yml | Measure-Object | Select-Object -ExpandProperty Count

# Показать все workflow
Get-ChildItem .github\workflows\*.yml | Select-Object Name

# Показать disabled
Get-ChildItem .github\workflows\*.disabled | Select-Object Name
```

---

*Создано: 19 мая 2026 г.*
*Автор: Koda AI Assistant*