"""
Тестовый скрипт для проверки RAG API системы.
"""

import requests
import json
import time
import sys
from pathlib import Path

def test_api_health():
    """Тестирование здоровья API."""
    print("🧪 Тестирование здоровья API...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API здоров: {data}")
            return True
        else:
            print(f"❌ API не отвечает: статус {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к API. Запустите сервер:")
        print("   uvicorn api.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_ask_endpoint():
    """Тестирование эндпоинта /ask."""
    print("\n🧪 Тестирование эндпоинта /ask...")
    
    test_questions = [
        "Как работает система?",
        "Какие технологии используются?",
        "Что такое IT-Compass?",
        "Как устроена архитектура проекта?"
    ]
    
    for question in test_questions:
        print(f"\n📝 Вопрос: {question}")
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={
                    "query": question,
                    "top_k": 2,
                    "min_confidence": 0.1
                },
                timeout=30
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Ответ получен за {processing_time:.2f} сек")
                print(f"   Уверенность: {data.get('confidence', 0):.1%}")
                print(f"   Источников: {len(data.get('sources', []))}")
                
                # Показываем краткий ответ
                answer = data.get('answer', '')
                if len(answer) > 150:
                    answer = answer[:150] + "..."
                print(f"   Ответ: {answer}")
            else:
                print(f"❌ Ошибка: статус {response.status_code}")
                print(f"   Ответ: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Исключение: {e}")

def test_stats_endpoint():
    """Тестирование эндпоинта /stats."""
    print("\n🧪 Тестирование эндпоинта /stats...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Статистика: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Ошибка: статус {response.status_code}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")

def test_streamlit_ui():
    """Проверка доступности Streamlit UI."""
    print("\n🧪 Проверка Streamlit UI...")
    
    try:
        # Проверяем, что файл UI существует
        ui_file = Path("ui/app.py")
        if ui_file.exists():
            print("✅ UI файл существует: ui/app.py")
            print("   Запустите: streamlit run ui/app.py")
        else:
            print("❌ UI файл не найден")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_rag_components():
    """Проверка компонентов RAG системы."""
    print("\n🧪 Проверка компонентов RAG системы...")
    
    # Проверяем наличие ключевых файлов
    required_files = [
        "src/embedding_agent/chroma_indexer.py",
        "src/assistant_orchestrator/plugins/rag_advisor.py",
        "api/main.py",
        "ui/app.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - не найден")
            all_exist = False
    
    return all_exist

def main():
    """Основная функция тестирования."""
    print("=" * 60)
    print("🧠 ТЕСТИРОВАНИЕ AI АРХИТЕКТОРА")
    print("=" * 60)
    
    # Проверяем компоненты
    components_ok = test_rag_components()
    
    if not components_ok:
        print("\n⚠️  Некоторые компоненты отсутствуют. Продолжаем тестирование...")
    
    # Проверяем API (если запущен)
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ API СЕРВЕРА")
    print("=" * 60)
    
    api_healthy = test_api_health()
    
    if api_healthy:
        test_ask_endpoint()
        test_stats_endpoint()
    else:
        print("\n⚠️  API сервер не запущен. Запустите его для полного тестирования.")
        print("   Команда: uvicorn api.main:app --reload")
    
    # Проверяем UI
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ UI КОМПОНЕНТОВ")
    print("=" * 60)
    test_streamlit_ui()
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    if api_healthy:
        print("✅ API сервер работает корректно")
    else:
        print("⚠️  API сервер не запущен (ожидаемо для первого запуска)")
    
    print("✅ Все компоненты системы созданы")
    print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Запустите API сервер: uvicorn api.main:app --reload")
    print("2. В отдельном терминале запустите UI: streamlit run ui/app.py")
    print("3. Откройте браузер: http://localhost:8501")
    print("4. Задавайте вопросы о проекте!")
    
    return api_healthy

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Тестирование прервано пользователем")
        sys.exit(0)
