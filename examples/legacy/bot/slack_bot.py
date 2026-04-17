"""
Slack бот для AI-консультанта по архитектуре.
Позволяет задавать вопросы о проекте прямо в Slack.
"""

import os
import logging
from typing import Any
from pathlib import Path
import sys

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.assistant_orchestrator.plugins.rag_advisor import RAGAdvisor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackArchitectBot:
    """Slack бот для консультаций по архитектуре."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.rag_advisor = RAGAdvisor(self.project_root)
        
        # Проверяем доступность Slack SDK
        try:
            from slack_bolt import App
            from slack_bolt.adapter.socket_mode import SocketModeHandler
            self.SLACK_AVAILABLE = True
            self.App = App
            self.SocketModeHandler = SocketModeHandler
        except ImportError:
            self.SLACK_AVAILABLE = False
            logger.warning("Slack SDK not available. Install with: pip install slack_bolt")
    
    def create_app(self) -> Any:
        """Создать Slack приложение."""
        if not self.SLACK_AVAILABLE:
            raise ImportError("Slack SDK is not available. Install slack_bolt")
        
        # Получаем токены из переменных окружения
        slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
        slack_app_token = os.environ.get("SLACK_APP_TOKEN")
        
        if not slack_bot_token or not slack_app_token:
            logger.error("SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in environment")
            raise ValueError("Missing Slack tokens")
        
        # Создаем приложение
        app = self.App(token=slack_bot_token)
        
        # Обработчик сообщений с триггером "архитектор:"
        @app.message("архитектор:")
        def handle_architect_question(message, say):
            """Обработать вопрос к архитектору."""
            try:
                # Извлекаем вопрос (убираем триггер)
                question = message["text"].replace("архитектор:", "").strip()
                user = message.get("user", "unknown")
                
                logger.info(f"Question from {user}: {question}")
                
                # Отправляем сообщение о обработке
                say(f"🧠 *{user} спрашивает:* {question}\n_Ищу ответ в документации..._")
                
                # Получаем ответ от RAG
                result = self.rag_advisor.ask(
                    question=question,
                    top_k=3,
                    min_confidence=0.3
                )
                
                # Форматируем ответ
                answer = result.get("answer", "Не удалось получить ответ.")
                confidence = result.get("confidence", 0.0)
                sources = result.get("sources", [])
                
                # Форматируем ответ для Slack
                response_text = f"🔍 *Ответ:* {answer}\n\n"
                
                if confidence >= 0.7:
                    confidence_emoji = "✅"
                elif confidence >= 0.4:
                    confidence_emoji = "⚠️"
                else:
                    confidence_emoji = "❓"
                
                response_text += f"{confidence_emoji} *Уверенность:* {confidence:.1%}\n\n"
                
                if sources:
                    response_text += f"📚 *Источники ({len(sources)}):*\n"
                    for i, src in enumerate(sources[:3], 1):
                        file_name = src.get("file", "unknown")
                        preview = src.get("text", "")[:100].replace("\n", " ")
                        response_text += f"{i}. `{file_name}`: {preview}...\n"
                
                # Отправляем ответ
                say(response_text)
                
                logger.info(f"Answered question from {user} with confidence {confidence:.1%}")
                
            except Exception as e:
                logger.error(f"Error processing question: {e}")
                say(f"❌ Ошибка при обработке вопроса: {str(e)}")
        
        # Команда /architect
        @app.command("/architect")
        def handle_architect_command(ack, say, command):
            """Обработать команду /architect."""
            ack()
            
            question = command.get("text", "").strip()
            if not question:
                say("""
🧠 *AI Архитектор - помощник по проекту*

Использование:
• `/architect <ваш вопрос>` - задать вопрос о проекте
• Или упомяните `архитектор:` в любом сообщении

Примеры:
• `/architect Как работает аутентификация?`
• `/architect Какие технологии используются для мониторинга?`
• `архитектор: Как устроена архитектура микросервисов?`
                """)
                return
            
            user = command.get("user_name", "unknown")
            logger.info(f"Command from {user}: {question}")
            
            # Получаем ответ
            result = self.rag_advisor.ask(
                question=question,
                top_k=3,
                min_confidence=0.3
            )
            
            # Форматируем ответ
            answer = result.get("answer", "Не удалось получить ответ.")
            confidence = result.get("confidence", 0.0)
            
            response_text = f"🧠 *Вопрос от {user}:* {question}\n\n"
            response_text += f"🔍 *Ответ:* {answer}\n\n"
            response_text += f"📊 *Уверенность:* {confidence:.1%}"
            
            say(response_text)
        
        # Проверка здоровья
        @app.command("/architect-health")
        def handle_health_check(ack, say, command):
            """Проверить здоровье сервиса."""
            ack()
            
            try:
                index_ready = self.rag_advisor.is_index_ready()
                stats = self.rag_advisor.get_index_stats()
                
                health_text = "✅ *AI Архитектор работает нормально*\n\n"
                health_text += f"• Индекс готов: {'Да' if index_ready else 'Нет'}\n"
                
                if stats:
                    health_text += f"• Документов в индексе: {stats.get('total_documents', 0)}\n"
                    health_text += f"• Модель: {stats.get('model_name', 'unknown')}\n"
                
                health_text += "\n💡 Используйте `/architect <вопрос>` для консультаций"
                
                say(health_text)
                
            except Exception as e:
                say(f"❌ *Ошибка проверки здоровья:* {str(e)}")
        
        return app, slack_app_token
    
    def run(self):
        """Запустить Slack бота."""
        try:
            app, app_token = self.create_app()
            
            logger.info("Starting Slack Architect Bot...")
            logger.info("Bot will respond to:")
            logger.info("  1. Messages containing 'архитектор:'")
            logger.info("  2. /architect command")
            logger.info("  3. /architect-health command")
            
            # Запускаем в режиме Socket Mode
            handler = self.SocketModeHandler(app, app_token)
            handler.start()
            
        except Exception as e:
            logger.error(f"Failed to start Slack bot: {e}")
            raise

def main():
    """Основная функция запуска бота."""
    bot = SlackArchitectBot()
    
    # Проверяем доступность зависимостей
    if not bot.SLACK_AVAILABLE:
        print("❌ Slack SDK не установлен.")
        print("Установите зависимости:")
        print("  pip install slack_bolt")
        print("\nТакже установите RAG зависимости:")
        print("  pip install sentence-transformers chromadb")
        return
    
    # Проверяем переменные окружения
    if not os.environ.get("SLACK_BOT_TOKEN") or not os.environ.get("SLACK_APP_TOKEN"):
        print("❌ Не заданы Slack токены.")
        print("Установите переменные окружения:")
        print("  export SLACK_BOT_TOKEN=xoxb-your-bot-token")
        print("  export SLACK_APP_TOKEN=xapp-your-app-token")
        print("\nПолучите токены на https://api.slack.com/apps")
        return
    
    print("🚀 Запуск Slack Architect Bot...")
    print("Бот будет отвечать на:")
    print("  • Сообщения с 'архитектор:'")
    print("  • Команду /architect")
    print("  • Команду /architect-health")
    print("\nДля остановки нажмите Ctrl+C")
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
