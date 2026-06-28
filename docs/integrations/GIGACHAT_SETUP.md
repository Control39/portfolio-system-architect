# Инструкция по настройке GigaChat API

## Проблема

Ваш текущий ключ `GIGACHAT_API_KEY` содержит `client_id:client_secret` в base64 формате, но GigaChat API требует **access token**.

## Решение

### Вариант 1: Получить новый access token

1. **Зарегистрируйтесь на SberCloud**:
   - Перейдите на https://developers.sber.ru/docs/ru/gigachat
   - Зарегистрируйтесь и получите доступ к GigaChat API

2. **Получите credentials**:
   - Войдите в консоль разработчика
   - Перейдите в раздел GigaChat API
   - Получите `client_id` и `client_secret`

3. **Обновите `.env` файл**:

```env
GIGACHAT_CLIENT_ID=ваш_client_id
GIGACHAT_CLIENT_SECRET=ваш_client_secret
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_AUTH_URL=https://ngw.devices.sberbank.ru:9443/api/v2/oauth
GIGACHAT_VERIFY_SSL=false
```

4. **Получите access token**:

```bash
python get_gigachat_token.py
```

Этот скрипт автоматически получит access token через OAuth и покажет его вам.

5. **Скопируйте токен и обновите `.env`**:

```env
GIGACHAT_API_KEY=<скопированный_access_token>
```

### Вариант 2: Использовать только client_id/client_secret

Если вы не хотите хранить access token в `.env`, просто оставьте `GIGACHAT_API_KEY` закомментированным:

```env
#GIGACHAT_API_KEY=
GIGACHAT_CLIENT_ID=ваш_client_id
GIGACHAT_CLIENT_SECRET=ваш_client_secret
```

Система автоматически получит access token через `ConfigManager.get_gigachat_token()`.

## Проверка

Запустите диагностику:

```bash
python diagnose_gigachat.py
```

Если всё настроено правильно, вы увидите:

```
✅ GigaChat работает! Можно приступать к генерации тестов.
```

## Запуск генерации тестов

Когда настроено подключение к GigaChat:

```bash
# Через демонстрационный скрипт
python test_generation_demo.py

# Для всех файлов в src/
python run_test_generation.py

# Через Autonomous Agent
python run_autonomous_test_gen.py
```

##常见 проблемы

### 401 Unauthorized
- Устаревший access token - получите новый
- Неверный API ключ

### 400 Bad Request
- Неверный client_id или client_secret
- Неверный scope

### SSL Certificate Error
- Корпоративная сеть с самоподписанными сертификатами
- Установите `GIGACHAT_VERIFY_SSL=false` в `.env`

### Connection Timeout
- Корпоративный прокси блокирует доступ
- Проверьте сетевые настройки

## Документация

- https://developers.sber.ru/docs/ru/gigachat/api/oauth
- https://developers.sber.ru/docs/ru/gigachat/api/auth
