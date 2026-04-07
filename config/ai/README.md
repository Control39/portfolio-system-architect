# Конфигурации AI-агентов для российского стека

## Ваш стек технологий

### Бесплатные и доступные инструменты:
1. **GigaChat** (Сбер) - токены Pro Light и Normal
2. **YandexGPT** (Яндекс) - грант 6000 руб в Яндекс.Облаке
3. **SourceCraft агенты** - еженедельная квота в VS Code
4. **Локальные модели** - Ollama, Llama, другие open-source модели
5. **Open-source альтернативы** - бесплатные облачные опции

## Структура конфигураций

### Для Continue.dev:
- `config/ai/continue/` - шаблоны конфигураций Continue.dev
- Использовать переменные окружения для секретов

### Для Code Assistant:
- `config/ai/codeassistant/` - навыки и конфигурации Code Assistant
- Публичные навыки можно хранить в Git

### Для MCP серверов:
- `config/ai/mcp/` - конфигурации MCP серверов
- Интеграция с вашими инструментами

## Шаблоны конфигураций

### 1. Continue.dev конфигурация (без GPT-5)
```yaml
# config/ai/continue/template.yaml
name: "Российский стек AI"
version: 1.0.0
schema: v1

models:
  # GigaChat (Сбер)
  - title: "GigaChat Pro Light"
    provider: "gigachat"
    model: "GigaChat-Pro-Light"
    apiKey: "${GIGACHAT_API_KEY}"
    apiBase: "https://gigachat.devices.sberbank.ru/api/v1"
  
  - title: "GigaChat Normal" 
    provider: "gigachat"
    model: "GigaChat"
    apiKey: "${GIGACHAT_API_KEY}"
    apiBase: "https://gigachat.devices.sberbank.ru/api/v1"
  
  # YandexGPT (Яндекс)
  - title: "YandexGPT Lite"
    provider: "yandex"
    model: "yandexgpt-lite"
    apiKey: "${YANDEX_API_KEY}"
    folderId: "${YANDEX_FOLDER_ID}"
  
  - title: "YandexGPT Pro"
    provider: "yandex"
    model: "yandexgpt"
    apiKey: "${YANDEX_API_KEY}"
    folderId: "${YANDEX_FOLDER_ID}"
  
  # Локальные модели (Ollama)
  - title: "Llama 3.1 Russian"
    provider: "ollama"
    model: "llama3.1:latest"
    apiBase: "http://localhost:11434"
  
  - title: "Qwen2.5 Coder"
    provider: "ollama"
    model: "qwen2.5-coder:7b"
    apiBase: "http://localhost:11434"
  
  # SourceCraft агенты
  - title: "SourceCraft Agent"
    provider: "sourcecraft"
    model: "sourcecraft-agent"
    # Использует встроенную интеграцию в VS Code

mcpServers:
  career-autopilot:
    command: "python"
    args:
      - "apps/mcp-server/src/main.py"
    env:
      MCP_ENV: "development"
```

### 2. Code Assistant конфигурация
```yaml
# config/ai/codeassistant/ai-models.template.yaml
ai_models:
  gigachat:
    enabled: true
    api_key_env: "GIGACHAT_API_KEY"
    models:
      - name: "GigaChat-Pro-Light"
        context_window: 8192
      
      - name: "GigaChat"
        context_window: 16384
  
  yandexgpt:
    enabled: true
    api_key_env: "YANDEX_API_KEY"
    folder_id_env: "YANDEX_FOLDER_ID"
    models:
      - name: "yandexgpt-lite"
        context_window: 4096
      
      - name: "yandexgpt"
        context_window: 8192
  
  ollama:
    enabled: true
    base_url: "http://localhost:11434"
    models:
      - name: "llama3.1:latest"
        context_window: 32768
      
      - name: "qwen2.5-coder:7b"
        context_window: 32768
      
      - name: "codellama:7b"
        context_window: 16384
  
  sourcecraft:
    enabled: true
    # Использует встроенную интеграцию
```

### 3. MCP сервер конфигурация
```yaml
# config/ai/mcp/mcp-config.template.yaml
version: "1.0.0"
name: "Career Autopilot MCP Server"

ai_models:
  default: "gigachat-pro-light"
  
  available:
    - name: "gigachat-pro-light"
      provider: "gigachat"
      max_tokens: 4000
    
    - name: "yandexgpt-lite"
      provider: "yandex"
      max_tokens: 2000
    
    - name: "llama3.1"
      provider: "ollama"
      max_tokens: 32768
    
    - name: "sourcecraft-agent"
      provider: "sourcecraft"
      max_tokens: 8000
```

## Настройка переменных окружения

Создайте файл `.env.local` (в .gitignore):

```bash
# .env.local
# GigaChat (Сбер)
GIGACHAT_API_KEY=your_gigachat_api_key_here
GIGACHAT_API_BASE=https://gigachat.devices.sberbank.ru/api/v1

# YandexGPT (Яндекс)
YANDEX_API_KEY=your_yandex_api_key_here
YANDEX_FOLDER_ID=your_folder_id_here

# Локальные модели
OLLAMA_BASE_URL=http://localhost:11434
```

## Скрипт инициализации

```python
# scripts/setup-ai-configs.py
#!/usr/bin/env python3
"""
Скрипт для настройки AI конфигураций
"""

import os
import shutil
from pathlib import Path

def setup_configs():
    """Настройка конфигураций AI-агентов"""
    project_root = Path(__file__).parent.parent
    
    # 1. Continue.dev конфигурация
    continue_template = project_root / "config" / "ai" / "continue" / "template.yaml"
    continue_dest = project_root / ".continue" / "config.yaml"
    
    if continue_template.exists() and not continue_dest.exists():
        shutil.copy(continue_template, continue_dest)
        print(f"Создана конфигурация Continue.dev: {continue_dest}")
    
    # 2. Code Assistant конфигурация
    ca_template = project_root / "config" / "ai" / "codeassistant" / "ai-models.template.yaml"
    ca_dest = project_root / ".codeassistant" / "ai-models.yaml"
    
    if ca_template.exists() and not ca_dest.exists():
        shutil.copy(ca_template, ca_dest)
        print(f"Создана конфигурация Code Assistant: {ca_dest}")
    
    # 3. Создаем .env.example если нет .env.local
    env_example = project_root / ".env.example"
    env_local = project_root / ".env.local"
    
    if not env_local.exists() and not env_example.exists():
        with open(env_example, 'w', encoding='utf-8') as f:
            f.write("""# Пример файла переменных окружения
# Скопируйте в .env.local и заполните своими значениями

# GigaChat (Сбер)
GIGACHAT_API_KEY=your_gigachat_api_key_here

# YandexGPT (Яндекс)
YANDEX_API_KEY=your_yandex_api_key_here
YANDEX_FOLDER_ID=your_folder_id_here

# Локальные модели
OLLAMA_BASE_URL=http://localhost:11434
""")
        print(f"Создан пример файла переменных окружения: {env_example}")
    
    print("\nНастройка завершена!")
    print("1. Заполните .env.local своими API ключами")
    print("2. Запустите MCP сервер: python apps/mcp-server/src/main.py")
    print("3. Настройте VS Code расширения с использованием созданных конфигураций")

if __name__ == "__main__":
    setup_configs()
```

## Инструкция по настройке

### Шаг 1: Клонируйте шаблоны
```bash
python scripts/setup-ai-configs.py
```

### Шаг 2: Настройте переменные окружения
```bash
# Скопируйте пример
cp .env.example .env.local

# Отредактируйте .env.local своими API ключами
```

### Шаг 3: Настройте инструменты
1. **Continue.dev**: Конфигурация автоматически скопируется в `.continue/config.yaml`
2. **Code Assistant**: Конфигурация в `.codeassistant/ai-models.yaml`
3. **MCP сервер**: Использует конфигурацию из `config/ai/mcp/`

### Шаг 4: Запустите MCP сервер
```bash
cd apps/mcp-server
python src/main.py
```

## Решение проблемы с GPT-5

Если в ваших текущих конфигурациях есть упоминания GPT-5 или других недоступных моделей:

1. **Временное решение**: Замените GPT-5 на GigaChat или YandexGPT
2. **Постоянное решение**: Используйте наши шаблоны конфигураций

## Безопасность

### Что можно хранить в Git:
- Шаблоны конфигураций (с `${VARIABLE}` подстановкой)
- Документацию по настройке
- Скрипты инициализации

### Что НЕЛЬЗЯ хранить в Git:
- Файлы `.env.local` с API ключами
- Персональные access tokens
- Локальные абсолютные пути

## Поддержка и обновления

### Регулярные проверки:
1. **Актуальность API**: Проверяйте актуальность API endpoints
2. **Квоты и лимиты**: Следите за использованием квот
3. **Новые модели**: Добавляйте поддержку новых локальных моделей

### Обновление конфигураций:
```bash
# Получите последние шаблоны
git pull origin main

# Обновите конфигурации
python scripts/setup-ai-configs.py --update
```

## Полезные ссылки

### Документация:
- [GigaChat API](https://developers.sber.ru/docs/ru/gigachat/api/overview)
- [YandexGPT API](https://cloud.yandex.ru/docs/yandexgpt/)
- [Ollama](https://ollama.com/)
- [SourceCraft](https://sourcecraft.io/)

### Примеры использования:
- `examples/gigachat-integration.py` - интеграция с GigaChat
- `examples/yandexgpt-batch.py` - пакетная обработка через YandexGPT
- `examples/local-models-setup.md` - настройка локальных моделей

---

**Примечание:** Эти конфигурации созданы специально для вашего российского стека и учитывают доступные вам бесплатные ресурсы.