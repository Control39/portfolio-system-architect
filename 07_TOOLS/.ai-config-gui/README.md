# AI Config Manager

Графический интерфейс для управления конфигурациями AI-сервисов.

## 🚀 Возможности

- Управление локальными моделями (Ollama)
- Интеграция с GigaChat, YandexGPT, DeepSeek
- Мониторинг состояния сервисов в реальном времени
- Генерация конфигов для Continue, Cline, Koda
- Мобильное приложение для удалённого мониторинга

## 📦 Установка

`ash
cd 07_TOOLS/.ai-config-gui
npm install
npm start
🔧 Дополнительная настройка

### Адаптеры
Приложение поддерживает интеграцию с:
- **Azure Cognitive Services** — настройте `AZURE_ENDPOINT` и `AZURE_API_KEY`
- **Hugging Face** — настройте `HUGGINGFACE_API_KEY`

### Мониторинг
После запуска доступен по адресу: http://localhost:3000

### Настройка
Скопируйте .env.example в .env

Заполните API ключи

Запустите приложение

📱 Мобильное приложение
bash
cd ai-config-mobile
npm install
npm start
📄 Лицензия
MIT
