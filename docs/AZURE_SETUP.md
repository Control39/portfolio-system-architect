# ☁️ Настройка Azure Storage (опционально)

> **Примечание:** Этот документ описывает опциональную настройку для production-деплоя.
> Проект полностью работает **без Azure** в локальном режиме (memory store).

---

## 📋 Предварительные требования

- Аккаунт Azure (можно создать бесплатно: https://azure.microsoft.com/free/)
- Azure CLI (`az`) установлен
- Доступ к порталу Azure

---

## 🚀 Создание Azure Storage Account

### 1. Регистрация и создание ресурса

```bash
# Войти в Azure
az login

# Создать ресурсную группу
az group create \
  --name portfolio-rg \
  --location eastus

# Создать Storage Account
az storage account create \
  --name portfolio<uniqueid> \
  --resource-group portfolio-rg \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2
```

### 2. Получить connection string

```bash
az storage account show-connection-string \
  --name portfolio<uniqueid> \
  --resource-group portfolio-rg
```

### 3. Создать Azure Table для хранения данных

```bash
az storage table create \
  --name RoomMetadata \
  --account-name portfolio<uniqueid> \
  --account-key <key>

az storage table create \
  --name ChatMessages \
  --account-name portfolio<uniqueid> \
  --account-key <key>
```

---

## ⚙️ Настройка окружения

### Переменные окружения

Создайте `.env` в корне проекта:

```bash
STORAGE_MODE=table
AZURE_STORAGE_ACCOUNT=portfolio<uniqueid>
AZURE_STORAGE_KEY=<your-key>
# Или альтернативно:
# AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;..."
```

### Docker Compose

```bash
# Запуск с Azure
docker-compose -f docker-compose.yml -f docker-compose.azure.yml up -d
```

---

## 🔒 Безопасность

### Рекомендации для production:

1. **Managed Identity** (предпочтительно)
   - Используйте Managed Identity вместо connection strings
   - См. [Azure Documentation](https://docs.microsoft.com/azure/storage/common/storage-auth-aad-rbac-portal)

2. **Key Vault**
   - Храните секреты в Azure Key Vault
   - См. [`docs/SECURITY.md`](SECURITY.md)

3. **Network Rules**
   - Ограничьте доступ по IP
   - Используйте Private Endpoints

---

## 🧪 Тестирование

### Проверка подключения

```bash
# Проверка Azure Storage
az storage table list \
  --account-name portfolio<uniqueid> \
  --account-key <key>

# Локальный тест
STORAGE_MODE=table python -m pytest python_server/tests -k "azure"
```

---

## 📊 Сравнение режимов

| Режим | Storage | Требует Azure | Покрытие тестами | Скорость |
|-------|---------|---------------|------------------|----------|
| **memory** | Local RAM | ❌ Нет | 96% | ⚡ Быстро |
| **table** | Azure Tables | ✅ Да | 25% | 🐌 Медленнее |

---

## 🚧 Roadmap

- [ ] Добавить Managed Identity support
- [ ] Интеграция с Azure Key Vault
- [ ] CI/CD для Azure деплоя
- [ ] Нагрузочное тестирование Azure Tables

---

*Документ создан 15 мая 2026 г., в разработке*
