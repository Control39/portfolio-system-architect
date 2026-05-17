# Configuration Files

> **Централизованное хранилище конфигураций**
> **Single Source of Truth для всех сервисов**
> **Обновлено:** 18 мая 2026

---

## 📁 Структура

```
config/
├── ai-config.yaml              # ✅ AI Config Manager (глобальная)
├── ai/                         # AI модели, промпты, RAG настройки
├── base/                       # Общие настройки (dev/staging/prod)
│   ├── dev/                    # Dev environment
│   ├── staging/                # Staging environment
│   └── prod/                   # Production environment
├── services/                   # Пер-сервис конфигурации
│   ├── cognitive-agent/
│   ├── decision-engine/
│   └── ... (все 15 сервисов)
├── deployment/                 # Docker, K8s, Cloud
│   ├── docker/                 # Docker Compose, Dockerfiles
│   ├── k8s/                    # Kubernetes manifests
│   └── cloud/                  # AWS, GCP, Azure
├── tools/                      # Tool-specific (Koda, VSCode, Continue)
├── ci-cd/                      # CI/CD пайплайны (GitHub Actions)
├── settings/                   # Глобальные настройки
├── docker/                     # Docker-конфигурации
└── secrets/                    # ⚠️ Секреты (НЕ в git!)
    ├── .gitignore
    └── templates/              # Шаблони секрета
```

---

## 🎯 Правила

### 1. Иерархия приоритетов

```
config/secrets/*.yaml     (самый высокий)
config/services/<name>/   (пер-сервис)
config/base/<env>/        (окружение)
config/ai-config.yaml     (глобальный AI)
```

### 2. Форматы файлов

| Формат | Использование | Примеры |
|--------|---------------|---------|
| **YAML** | Основные конфиги | `*.yaml`, `*.yml` |
| **JSON** | Машинно-читаемые | `*.json` |
| **.env** | Переменные окружения | `.env` (в secrets/) |

### 3. Именование

```
<service-name>-<config-type>.yaml
# Пример:
cognitive-agent-dev.yaml
decision-engine-prod.yaml
docker-compose.yml
```

---

## 🚀 Использование

### В сервисах

```python
from apps.YOUR_SERVICE.src.config_integration import get_config

config = get_config()
# Получает:
# 1. config/ai-config.yaml (глобальный)
# 2. config/services/<service>/ (пер-сервис)
# 3. config/base/<env>/ (окружение)
```

### Через переменные окружения

```bash
export CONFIG_ENV=dev
export CONFIG_SERVICE=cognitive-agent
python main.py
```

---

## 📋 Добавление нового конфига

### 1. Определить тип

| Тип | Куда | Пример |
|-----|------|--------|
| Глобальный AI | `config/ai-config.yaml` | Модели, rate limits |
| Пер-сервис | `config/services/<name>/` | Настройки сервиса |
| Окружение | `config/base/<env>/` | Dev/Prod настройки |
| Deployment | `config/deployment/` | Docker, K8s |
| Инструменты | `config/tools/` | Koda, VSCode |

### 2. Создать файл

```yaml
# config/services/<service>/<name>.yaml
service:
  setting1: value
  setting2: value
```

### 3. Обновить сервис

```python
from config.integration import get_config
config = get_config().get("services", {}).get("YOUR_SERVICE", {})
```

### 4. Закоммитить

```bash
git add config/
git commit -m "config: add <service> configuration"
```

---

## 🔒 Секреты

### НЕ коммитить:
- API ключи
- Пароли
- Private keys
- Database credentials

### Хранить в:
- `config/secrets/` (локально)
- Azure Key Vault
- AWS Secrets Manager
- Kubernetes Secrets

### Шаблон:
```bash
# config/secrets/templates/.env.template
DATABASE_URL="postgresql://user:pass@localhost/db"  # pragma: allowlist secret
API_KEY="your-api-key-here"  # pragma: allowlist secret
```

---

## 📊 Текущий статус

| Компонент | Статус | Примечание |
|-----------|--------|------------|
| **AI Config Manager** | ✅ Готово | `config/ai-config.yaml` |
| **14 сервисов интегрированы** | ✅ Готово | Singleton + hot reload |
| **9 сервисов активно** | ✅ Готово | Используют центральный конфиг |
| **5 сервисов в работе** | ⏳ В работе | Нет main.py/app.py |
| **Пер-сервис конфиги** | 🔄 В процессе | Миграция продолжается |
| **Secrets management** | ⚠️ Частично | Есть `.secrets.baseline` |

---

## 🔗 Ссылки

- [AI Config Integration Guide](../docs/AI_CONFIG_INTEGRATION.md)
- [Config Consolidation Plan](../plans/config-consolidation.md)
- [Skills Consolidation Plan](../plans/skills-consolidation.md)
- [Next Steps](../NEXT_STEPS.md)

---

*Last updated: 18 мая 2026*
