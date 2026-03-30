"""
Скрипт для запуска и проверки системы AI Архитектора.
"""

import subprocess
import time
import sys
import os
from pathlib import Path
import requests
import threading

def start_api_server():
    """Запустить API сервер в отдельном процессе."""
    print("🚀 Запуск API сервера...")
    
    # Команда для запуска API
    api_cmd = [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    
    # Запускаем в отдельном процессе
    api_process = subprocess.Popen(
        api_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    print(f"✅ API сервер запущен (PID: {api_process.pid})")
    print(f"   Документация: http://127.0.0.1:8000/docs")
    print(f"   Health check: http://127.0.0.1:8000/health")
    
    return api_process

def start_streamlit_ui():
    """Запустить Streamlit UI в отдельном процессе."""
    print("\n🚀 Запуск Streamlit UI...")
    
    # Команда для запуска Streamlit
    ui_cmd = [sys.executable, "-m", "streamlit", "run", "ui/app.py", "--server.port", "8501", "--server.address", "127.0.0.1"]
    
    # Запускаем в отдельном процессе
    ui_process = subprocess.Popen(
        ui_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    print(f"✅ Streamlit UI запущен (PID: {ui_process.pid})")
    print(f"   Интерфейс: http://127.0.0.1:8501")
    
    return ui_process

def wait_for_api(timeout=30):
    """Ожидать, пока API сервер станет доступен."""
    print("\n⏳ Ожидание запуска API сервера...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API сервер готов: {data}")
                return True
        except:
            time.sleep(1)
    
    print("❌ Таймаут ожидания API сервера")
    return False

def test_system():
    """Протестировать работу системы."""
    print("\n🧪 Тестирование системы...")
    
    # Тестовый вопрос
    test_question = "Что такое IT-Compass?"
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json={
                "query": test_question,
                "top_k": 2,
                "min_confidence": 0.1
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Система отвечает на вопросы!")
            print(f"   Вопрос: {test_question}")
            print(f"   Уверенность: {data.get('confidence', 0):.1%}")
            print(f"   Источников: {len(data.get('sources', []))}")
            
            # Краткий ответ
            answer = data.get('answer', '')
            if len(answer) > 100:
                answer = answer[:100] + "..."
            print(f"   Ответ: {answer}")
            
            return True
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def monitor_processes(api_process, ui_process):
    """Мониторинг процессов."""
    print("\n👁️  Мониторинг процессов (нажмите Ctrl+C для остановки)...")
    
    try:
        while True:
            # Проверяем статус процессов
            api_status = api_process.poll()
            ui_status = ui_process.poll()
            
            if api_status is not None:
                print(f"⚠️  API сервер остановлен (код: {api_status})")
                if api_process.stderr:
                    print(f"   Ошибка: {api_process.stderr.read()[:200]}")
            
            if ui_status is not None:
                print(f"⚠️  Streamlit UI остановлен (код: {ui_status})")
                if ui_process.stderr:
                    print(f"   Ошибка: {ui_process.stderr.read()[:200]}")
            
            if api_status is not None or ui_status is not None:
                break
                
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка системы...")
        
        # Останавливаем процессы
        if api_process.poll() is None:
            api_process.terminate()
            print("✅ API сервер остановлен")
        
        if ui_process.poll() is None:
            ui_process.terminate()
            print("✅ Streamlit UI остановлен")

def main():
    """Основная функция запуска системы."""
    print("=" * 60)
    print("🧠 ЗАПУСК СИСТЕМЫ AI АРХИТЕКТОРА")
    print("=" * 60)
    
    # Проверяем зависимости
    print("🔍 Проверка зависимостей...")
    try:
        import fastapi
        import uvicorn
        import streamlit
        import chromadb
        import sentence_transformers
        print("✅ Все зависимости установлены")
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("   Установите: pip install fastapi uvicorn streamlit chromadb sentence-transformers")
        return
    
    # Запускаем API сервер
    api_process = start_api_server()
    
    # Ждем запуска API
    if not wait_for_api():
        print("❌ Не удалось запустить API сервер")
        api_process.terminate()
        return
    
    # Тестируем систему
    if not test_system():
        print("⚠️  Система работает, но тестовый запрос не удался")
    
    # Запускаем UI
    ui_process = start_streamlit_ui()
    
    print("\n" + "=" * 60)
    print("✅ СИСТЕМА ЗАПУЩЕНА УСПЕШНО!")
    print("=" * 60)
    print("\n📊 ДОСТУПНЫЕ СЕРВИСЫ:")
    print("   • API сервер: http://127.0.0.1:8000")
    print("   • API документация: http://127.0.0.1:8000/docs")
    print("   • Streamlit UI: http://127.0.0.1:8501")
    print("   • Health check: http://127.0.0.1:8000/health")
    
    print("\n💡 КАК ИСПОЛЬЗОВАТЬ:")
    print("   1. Откройте http://localhost:8501 в браузере")
    print("   2. Задайте вопрос о проекте в поле ввода")
    print("   3. Получите ответ с источниками из документации")
    
    print("\n🛠️  ДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ:")
    print("   • Slack бот: python bot/slack_bot.py (требует настройки токенов)")
    print("   • Прямые API запросы: curl -X POST http://localhost:8000/ask ...")
    
    print("\n⚠️  Нажмите Ctrl+C для остановки системы")
    
    # Мониторим процессы
    monitor_processes(api_process, ui_process)
    
    print("\n👋 Система остановлена")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Завершение работы...")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)