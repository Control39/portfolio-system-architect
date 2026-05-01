"""Streamlit UI для AI-консультанта по архитектуре.
Позволяет не-техническим пользователям задавать вопросы о проекте.
"""

import time
from datetime import datetime

import requests
import streamlit as st

# Настройка страницы
st.set_page_config(
    page_title="AI Архитектор - Консультант по проекту",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS для улучшения внешнего вида
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .answer-box {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
        margin-bottom: 1.5rem;
    }
    .source-box {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #F59E0B;
        margin-bottom: 0.5rem;
    }
    .confidence-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .confidence-high {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .confidence-medium {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .confidence-low {
        background-color: #FEE2E2;
        color: #991B1B;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Заголовок
st.markdown('<h1 class="main-header">🧠 AI Архитектор</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Задайте вопрос о системе — получите точный ответ с источниками из документации проекта</p>',
    unsafe_allow_html=True,
)

# Боковая панель с настройками
with st.sidebar:
    st.header("⚙️ Настройки")

    api_url = st.text_input(
        "URL API сервера:",
        value="http://127.0.0.1:8000",
        help="Адрес FastAPI сервера с RAG-консультантом",
    )

    top_k = st.slider(
        "Количество источников:",
        min_value=1,
        max_value=10,
        value=3,
        help="Сколько источников использовать для ответа",
    )

    min_confidence = st.slider(
        "Минимальная уверенность:",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
        help="Минимальный порог уверенности для включения в ответ",
    )

    st.divider()

    # Проверка подключения
    if st.button("🔍 Проверить подключение к API"):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ API доступен: {data.get('status', 'unknown')}")
                st.info(f"Индекс готов: {data.get('index_ready', False)}")
            else:
                st.error(f"❌ API недоступен: статус {response.status_code}")
        except Exception as e:
            st.error(f"❌ Ошибка подключения: {e!s}")
            st.info("Запустите API сервер: `uvicorn api.main:app --reload`")

# Основная область
col1, col2 = st.columns([3, 1])

with col1:
    # Поле для вопроса
    query = st.text_area(
        "**Ваш вопрос о проекте:**",
        placeholder="Например: Как работает аутентификация в системе? Какие технологии используются для масштабирования? Как устроена архитектура микросервисов?",
        height=100,
        key="query_input",
    )

    # Кнопка отправки
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

    with col_btn1:
        ask_button = st.button("🚀 Задать вопрос", type="primary", use_container_width=True)

    with col_btn2:
        example_button = st.button("📋 Примеры вопросов", use_container_width=True)

    with col_btn3:
        clear_button = st.button("🗑️ Очистить", use_container_width=True)

# Обработка кнопки примеров
if example_button:
    examples = [
        "Как работает система аутентификации?",
        "Какие технологии используются для мониторинга?",
        "Как устроена архитектура микросервисов?",
        "Какие базы данных используются в проекте?",
        "Как настроено CI/CD для развертывания?",
        "Какие security меры реализованы?",
        "Как работает RAG-система поиска?",
        "Какие метрики собираются для анализа производительности?",
    ]

    example_cols = st.columns(2)
    for i, example in enumerate(examples):
        with example_cols[i % 2]:
            if st.button(example, use_container_width=True):
                st.session_state.last_query = example
                st.rerun()

# Обработка очистки
if clear_button:
    st.session_state.clear()
    st.rerun()

# Обработка вопроса
if ask_button and query:
    with st.spinner("🔍 Ищу ответ в документации проекта..."):
        try:
            start_time = time.time()

            # Отправляем запрос к API
            response = requests.post(
                f"{api_url}/ask",
                json={
                    "query": query,
                    "top_k": top_k,
                    "min_confidence": min_confidence,
                },
                timeout=30,
            )

            processing_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                # Отображаем ответ
                st.markdown("---")
                st.markdown("### 📝 Ответ")

                # Бейдж уверенности
                confidence = data.get("confidence", 0.0)
                if confidence >= 0.7:
                    confidence_class = "confidence-high"
                    confidence_text = "Высокая уверенность"
                elif confidence >= 0.4:
                    confidence_class = "confidence-medium"
                    confidence_text = "Средняя уверенность"
                else:
                    confidence_class = "confidence-low"
                    confidence_text = "Низкая уверенность"

                st.markdown(
                    f'<div class="confidence-badge {confidence_class}">🤖 {confidence_text}: {confidence:.2%}</div>',
                    unsafe_allow_html=True,
                )

                # Ответ
                st.markdown(
                    f'<div class="answer-box">{data["answer"]}</div>',
                    unsafe_allow_html=True,
                )

                # Источники
                if data.get("sources"):
                    st.markdown("### 📚 Источники")
                    st.caption(f"Найдено {len(data['sources'])} релевантных документа(ов)")

                    for i, source in enumerate(data["sources"]):
                        with st.expander(
                            f"📄 {source.get('file', 'unknown')} (релевантность: {source.get('score', 0):.2%})",
                            expanded=i < 2,
                        ):
                            st.markdown(
                                f'<div class="source-box">{source.get("text", "")}</div>',
                                unsafe_allow_html=True,
                            )

                            # Метаданные
                            col_s1, col_s2 = st.columns(2)
                            with col_s1:
                                if source.get("line_start"):
                                    st.caption(
                                        f"Строки: {source.get('line_start')}-{source.get('line_end', source.get('line_start'))}"
                                    )
                            with col_s2:
                                st.caption(f"Уверенность: {source.get('score', 0):.2%}")

                # Статистика
                with st.expander("📊 Статистика запроса"):
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric(
                            "Время обработки",
                            f"{data.get('processing_time_ms', 0):.0f} мс",
                        )
                    with col_stat2:
                        st.metric("Уверенность", f"{confidence:.2%}")
                    with col_stat3:
                        st.metric("Источников", len(data.get("sources", [])))

                # Сохраняем историю
                if "history" not in st.session_state:
                    st.session_state.history = []

                st.session_state.history.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "question": query,
                        "answer": data["answer"],
                        "confidence": confidence,
                        "sources_count": len(data.get("sources", [])),
                    }
                )

            else:
                st.error(f"❌ Ошибка API: {response.status_code}")
                st.code(response.text[:500])

        except requests.exceptions.ConnectionError:
            st.error("❌ Не удалось подключиться к API серверу.")
            st.info(
                """
            **Решение:**
            1. Убедитесь, что API сервер запущен: `uvicorn api.main:app --reload`
            2. Проверьте URL в настройках (по умолчанию: http://127.0.0.1:8000)
            3. Убедитесь, что порт 8000 не занят другим приложением
            """
            )
        except Exception as e:
            st.error(f"❌ Неожиданная ошибка: {e!s}")

# История запросов
if "history" in st.session_state and st.session_state.history:
    st.markdown("---")
    st.markdown("### 📜 История запросов")

    for i, item in enumerate(reversed(st.session_state.history[-5:])):  # Последние 5 запросов
        with st.expander(f"❓ {item['question'][:50]}...", expanded=False):
            st.markdown(f"**Время:** {item['timestamp']}")
            st.markdown(f"**Уверенность:** {item['confidence']:.2%}")
            st.markdown(f"**Ответ:** {item['answer'][:200]}...")
            st.markdown(f"**Источников:** {item['sources_count']}")

# Инструкция по запуску
with st.expander("🛠️ Инструкция по запуску", expanded=False):
    st.markdown(
        """
    ### Шаги для запуска системы:

    1. **Запустите API сервер:**
    ```bash
    cd portfolio-system-architect
    uvicorn api.main:app --reload
    ```

    2. **В отдельном терминале запустите Streamlit UI:**
    ```bash
    streamlit run ui/app.py
    ```

    3. **Откройте браузер:**
    - Streamlit UI: http://localhost:8501
    - API документация: http://localhost:8000/docs

    4. **Проверьте, что индекс построен:**
    ```bash
    curl http://localhost:8000/health
    ```

    ### Требования:
    - Python 3.9+
    - Установленные зависимости: `pip install fastapi uvicorn streamlit requests`
    - Построенный RAG-индекс (автоматически при первом запросе)
    """
    )

# Футер
st.markdown("---")
st.caption(
    "🧠 AI Архитектор v1.0 | Система консультаций по архитектуре проекта | [Документация](https://github.com/leadarchitect-ai/portfolio-system-architect)"
)
