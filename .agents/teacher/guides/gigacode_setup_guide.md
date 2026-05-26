# Руководство по настройке GigaCode для VS Code

## Введение

GigaCode - это AI-ассистент для разработки на русском языке, который предоставляет:
- **Автодополнение кода** на основе контекста
- **Генерацию кода** по описанию на естественном языке
- **Рефакторинг** и оптимизацию существующего кода
- **Поиск ошибок** и предложения по исправлению
- **Документирование** кода на русском и английском языках

## Требования

1. **VS Code** версии 1.85 или выше
2. **Расширение GigaCode**: `GigaCode.gigacode-vscode`
3. **Токен GigaCode**: Получить можно на [gigachat.cloud](https://gigachat.cloud)
4. **Интернет-соединение** для работы с API

## Шаг 1: Установка расширения

### Автоматическая установка (рекомендуется)
```bash
# Используйте скрипт управления расширениями
python scripts/vscode-extensions-manager.py --install GigaCode.gigacode-vscode

# Или через PowerShell
.\scripts\vscode-extensions-manager.py --install GigaCode.gigacode-vscode
```

### Ручная установка
1. Откройте VS Code
2. Перейдите в Extensions (Ctrl+Shift+X)
3. Найдите "GigaCode"
4. Нажмите "Install"

## Шаг 2: Получение токена

### Вариант 1: Использование существующих токенов
Если у вас уже есть токены GigaCode:
- **GigaCode Pro**: 1000+ нейрокредитов
- **GigaCode Light**: 500 нейрокредитов  
- **Обычный токен**: 200 нейрокредитов

### Вариант 2: Регистрация нового аккаунта
1. Перейдите на [gigachat.cloud](https://gigachat.cloud)
2. Зарегистрируйтесь или войдите
3. Перейдите в раздел "API Keys"
4. Создайте новый токен
5. Скопируйте токен (он понадобится для настройки)

## Шаг 3: Настройка конфигурации

### Файл конфигурации VS Code
Создайте или отредактируйте файл `.vscode/settings.json`:

```json
{
  "gigacode.enabled": true,
  "gigacode.apiKey": "ваш_токен_здесь",
  "gigacode.model": "GigaChat",
  "gigacode.maxTokens": 4000,
  "gigacode.temperature": 0.7,
  "gigacode.enableCodeCompletion": true,
  "gigacode.enableChat": true,
  "gigacode.language": "ru",
  "gigacode.autoSuggest": true,
  "gigacode.suggestDelay": 300,
  "gigacode.contextWindow": 8000,
  
  // Настройки для конкретных языков
  "gigacode.python.enabled": true,
  "gigacode.typescript.enabled": true,
  "gigacode.javascript.enabled": true,
  "gigacode.yaml.enabled": true,
  "gigacode.markdown.enabled": true,
  
  // Интеграция с другими инструментами
  "gigacode.integrateWithCopilot": false,
  "gigacode.fallbackToSourceCraft": true,
  "gigacode.showTokenUsage": true
}
```

### Альтернативный вариант: Конфигурация через переменные окружения
Создайте файл `.env` в корне проекта:

```bash
GIGACODE_API_KEY=ваш_токен_здесь
GIGACODE_MODEL=GigaChat
GIGACODE_MAX_TOKENS=4000
```

## Шаг 4: Проверка работы

### Тест 1: Проверка подключения
1. Откройте командную палитру (Ctrl+Shift+P)
2. Введите "GigaCode: Check Connection"
3. Должно появиться сообщение "Connected successfully"

### Тест 2: Генерация кода
1. Создайте новый Python файл
2. Напишите комментарий на русском:
```python
# Напиши функцию для вычисления факториала с обработкой ошибок
```
3. Нажмите Ctrl+Space для автодополнения

### Тест 3: Чат с ассистентом
1. Откройте панель GigaCode (иконка в боковой панели)
2. Задайте вопрос на русском: "Как оптимизировать этот код?"
3. Получите развернутый ответ с примерами

## Шаг 5: Оптимизация использования токенов

### Стратегия экономии токенов
1. **Используйте локальные модели** для простых задач
2. **Включайте GigaCode только для сложных задач**
3. **Настройте контекстное окно** в зависимости от задачи
4. **Используйте кэширование** повторяющихся запросов

### Конфигурация для экономии
```json
{
  "gigacode.autoSuggest": false,  // Включать только по запросу
  "gigacode.suggestDelay": 1000,  // Увеличить задержку
  "gigacode.contextWindow": 2000, // Уменьшить контекст
  "gigacode.useForSimpleTasks": false  // Только для сложных
}
```

## Шаг 6: Интеграция с SourceCraft

### Fallback стратегия
При исчерпании токенов GigaCode можно автоматически переключаться на SourceCraft:

```json
{
  "gigacode.fallbackToSourceCraft": true,
  "gigacode.sourceCraftPriority": "after_gigacode",
  "gigacode.notifyOnFallback": true
}
```

### Совместное использование
1. **GigaCode** для:
   - Генерации кода на русском языке
   - Рефакторинга сложных структур
   - Документирования на русском
   
2. **SourceCraft** для:
   - CI/CD конфигурации
   - Инфраструктурного кода
   - Анализа безопасности

## Шаг 7: Мониторинг использования

### Просмотр статистики
```bash
# Через командную палитру VS Code
1. Ctrl+Shift+P
2. "GigaCode: Show Usage Statistics"
```

### Настройка уведомлений
```json
{
  "gigacode.notifyOnLowTokens": true,
  "gigacode.lowTokenThreshold": 50,
  "gigacode.dailyUsageLimit": 1000
}
```

## Шаг 8: Решение проблем

### Проблема 1: "Invalid API Key"
**Решение:**
1. Проверьте правильность токена
2. Обновите токен на gigachat.cloud
3. Перезапустите VS Code

### Проблема 2: Медленная работа
**Решение:**
```json
{
  "gigacode.suggestDelay": 500,
  "gigacode.useLightModel": true,
  "gigacode.cacheResponses": true
}
```

### Проблема 3: Высокое использование токенов
**Решение:**
1. Уменьшите `maxTokens` до 2000
2. Отключите автодополнение для больших файлов
3. Используйте локальные модели для форматирования

## Примеры использования

### Пример 1: Генерация FastAPI эндпоинта
```python
# Комментарий для GigaCode:
# Создай эндпоинт GET /health для проверки состояния сервиса
# с проверкой подключения к базе данных и кэшу

# GigaCode сгенерирует:
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.cache import get_cache

router = APIRouter()

@router.get("/health")
async def health_check(
    db: Session = Depends(get_db),
    cache = Depends(get_cache)
):
    """Проверка состояния сервиса"""
    try:
        # Проверка базы данных
        db.execute("SELECT 1")
        
        # Проверка кэша
        cache.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "cache": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )
```

### Пример 2: Рефакторинг кода
```python
# Исходный код:
def process_data(data):
    result = []
    for item in data:
        if item['active']:
            result.append(item['value'] * 2)
    return result

# Комментарий: "Рефактори эту функцию используя list comprehension"

# GigaCode сгенерирует:
def process_data(data):
    return [item['value'] * 2 for item in data if item['active']]
```

## Дополнительные ресурсы

### Официальная документация
- [GigaCode VS Code Extension](https://marketplace.visualstudio.com/items?itemName=GigaCode.gigacode-vscode)
- [GigaChat API Documentation](https://developers.sber.ru/docs/ru/gigachat/overview)
- [Примеры использования](https://github.com/GigaCode/vscode-extension-examples)

### Сообщество
- [Telegram канал GigaCode](https://t.me/gigacode_ru)
- [Форум разработчиков](https://developers.sber.ru/community)
- [Stack Overflow с тегом gigacode](https://stackoverflow.com/questions/tagged/gigacode)

## Заключение

GigaCode предоставляет мощные возможности для разработки на русском языке. При правильной настройке и оптимизации использования токенов, он может значительно ускорить процесс разработки и улучшить качество кода.

**Рекомендации для когнитивного архитектора:**
1. Используйте GigaCode для генерации документации на русском
2. Интегрируйте с локальными моделями Ollama для экономии токенов
3. Настройте автоматическое переключение между GigaCode и SourceCraft
4. Регулярно мониторьте использование токенов и оптимизируйте настройки

---

*Последнее обновление: 2026-04-10*  
*Автор: SourceCraft Code Assistant*  
*Для проекта: portfolio-system-architect*