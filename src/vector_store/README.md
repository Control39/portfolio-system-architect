# Vector Store Module

## Overview

Модуль `src/vector_store/` предоставляет унифицированный интерфейс для работы с векторными хранилищами в системе Cognitive Agent.

## Архитектура

```
src/vector_store/
├── __init__.py          # Публичный API и factory function
├── base.py              # Абстрактный интерфейс VectorStoreInterface
├── chroma_impl.py       # ChromaDB реализация
├── config.py            # Конфигурация (Pydantic models)
├── document_utils.py    # Утилиты для загрузки и чанкинга
├── embedder.py          # Sentence-transformers embedder
├── ollama_embedder.py   # Ollama fallback embedder
└── examples.py          # Примеры использования
```

## Компоненты

### 1. **VectorStoreInterface** (base.py)
Абстрактный интерфейс для всех реализаций векторных хранилищ.

**Методы:**
- `add_document(text, metadata)` — добавить документ
- `add_documents(documents)` — добавить множественные документы
- `search(query, top_k, where_filter)` — поиск похожих документов
- `get_stats()` — статистика хранилища
- `close()` — закрыть соединение
- `delete_all()` — удалить все документы

### 2. **ChromaVectorStore** (chroma_impl.py)
Реализация на базе ChromaDB для локального persistent storage.

**Преимущества:**
- ✅ Полностью локальное, не требует сети
- ✅ Persistent storage (данные сохраняются между запусками)
- ✅ Встроенная фильтрация по метаданным
- ✅ Простая установка (`pip install chromadb`)

**Инициализация:**
```python
from src.vector_store import ChromaVectorStore

store = ChromaVectorStore(
    persist_directory="./chroma_db",
    collection_name="cognitive_agent_docs",
)
```

### 3. **DocumentEmbedder** (embedder.py)
Embedding модель на базе sentence-transformers.

**Используемая модель:** `all-MiniLM-L6-v2` (384 измерения)

**Преимущества:**
- ✅ Быстрая инференс (~1ms на документ)
- ✅ Не требует API ключей
- ✅ Работает offline

### 4. **OllamaEmbedder** (ollama_embedder.py)
Fallback embedder для использования с Ollama.

**Используемые модели:**
- `nomic-embed-text` (768 измерений)
- `mxbai-embed-large` (1024 измерения)

**Требует:** Ollama запущена локально (`http://localhost:11434`)

### 5. **DocumentLoader + DocumentChunker** (document_utils.py)
Утилиты для загрузки и чанкинга документов.

**DocumentLoader:**
```python
from src.vector_store import DocumentLoader

# Загрузить все markdown файлы
docs = DocumentLoader.load_files(file_pattern="**/*.md", root_dir=".")
```

**DocumentChunker:**
```python
from src.vector_store import DocumentChunker

chunker = DocumentChunker(max_chunk_size=1000, overlap=100)
chunks = chunker.chunk_text(long_text)
```

### 6. **VectorStoreConfig** (config.py)
Конфигурация через Pydantic.

```python
from src.vector_store import VectorStoreConfig, VectorStoreType

config = VectorStoreConfig(
    store_type=VectorStoreType.CHROMA,
    persist_directory="./chroma_db",
    collection_name="project_docs",
    embedding_model="all-MiniLM-L6-v2",
)
```

## Использование

### Быстрый старт

```python
from src.vector_store import get_vector_store, DocumentLoader, DocumentChunker

# 1. Инициализировать хранилище
store = get_vector_store("chroma")

# 2. Загрузить документы
docs = DocumentLoader.load_files(file_pattern="**/*.md", root_dir=".")

# 3. Чанкировать и индексировать
chunker = DocumentChunker(max_chunk_size=1000)
for doc in docs:
    chunks = chunker.chunk_text(doc["text"])
    for chunk in chunks:
        store.add_document(chunk, metadata=doc["metadata"])

# 4. Искать
results = store.search("Как использовать GigaChat?", top_k=5)
for r in results:
    print(f"Score: {r['score']:.3f}, Text: {r['text'][:100]}")

# 5. Закрыть
store.close()
```

### Factory function

```python
from src.vector_store import get_vector_store, VectorStoreConfig

# Автоматически выбирает реализацию на основе config
config = VectorStoreConfig(store_type="chroma")
store = get_vector_store("chroma", config)
```

### Интеграция с Cognitive Agent

```python
# apps/cognitive_agent/scripts/planner_main.py
from src.vector_store import get_vector_store

class CognitivePlanner:
    def __init__(self):
        self.vector_store = get_vector_store("chroma")
        self.gigachat = GigaMCPBridge()

    def plan_task(self, task_description: str):
        # 1. Найти релевантный контекст
        context = self.vector_store.search(task_description, top_k=5)

        # 2. Использовать GigaChat для планирования
        prompt = self._build_prompt(task_description, context)
        plan = self.gigachat.generate(prompt)

        return plan
```

## Примеры

Запустить демо:

```bash
# Индексация документов
python -m src.vector_store.examples --index

# Поиск
python -m src.vector_store.examples --search

# Оба действия
python -m src.vector_store.examples --both
```

## Установка зависимостей

```bash
# Основные зависимости
pip install chromadb>=0.4.22
pip install sentence-transformers

# Опционально: Ollama (требуется запущенный Ollama сервер)
# Скачать с https://ollama.ai
# docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

## Расширения

### Добавить новую реализацию

1. Создать файл `src/vector_store/<name>_impl.py`
2. Наследоваться от `VectorStoreInterface`
3. Реализовать все абстрактные методы
4. Добавить в `get_vector_store()` factory function

```python
# src/vector_store/my_store_impl.py
from .base import VectorStoreInterface

class MyVectorStore(VectorStoreInterface):
    def add_document(self, text, metadata=None):
        # Your implementation
        pass

    # ... остальные методы
```

## Сравнение реализаций

| Критерий | ChromaDB | OpenAI | Ollama |
|----------|----------|--------|--------|
| **Локальное** | ✅ | ❌ | ✅ |
| **Требуется API ключ** | ❌ | ✅ | ❌ |
| **Offline режим** | ✅ | ❌ | ✅ |
| **Скорость** | Быстрая | Средняя | Зависит от модели |
| **Качество эмбеддингов** | Среднее | Высокое | Высокое |
| **Стоимость** | Бесплатно | Платно | Бесплатно |

## Тестирование

```bash
# Unit тесты
pytest apps/cognitive_agent/tests/test_vector_store.py -v

# Интеграционные тесты
pytest apps/cognitive_agent/tests/integration/test_rag.py -v
```

## Будущие улучшения

- [ ] Поддержка OpenAI Vector Stores
- [ ] Batch operations для производительности
- [ ] Асинхронный API
- [ ] Кэширование эмбеддингов
- [ ] Поддержка дополнительных форматов (PDF, DOCX)
- [ ] Автоматическая ротация старых документов

## Контакты

**Автор:** Екатерина Куделя (@Control39)
**Репозиторий:** https://github.com/Control39/portfolio-system-architect
