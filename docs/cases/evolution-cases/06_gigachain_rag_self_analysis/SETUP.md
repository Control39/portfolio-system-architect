# Setup Instructions (Template)

## Prerequisites
- Python 3.13 venv
- GigaChat API key (.env)

## Install
```
pip install langchain-gigachat langchain-chroma langchain-huggingface sentence-transformers langchain-community
```

## .env Template
```
GIGACHAT_API_KEY=your_key_here
```

## Run
1. Index: `python index_all_folders.py`
2. Search: `python search_deep.py`
3. Analyze: `python analyze_thinking_patterns.py`
4. Portfolio: `python export_to_portfolio.py`
5. Watch: `python 🧠_brain_sync.py --watch`

## Docker (Optional)
```
docker-compose up  # Includes Jupyter for exploration
```

Scripts in scripts/ dir. Full watcher for watched/ folder.

*Demo: Query "systemic thinking" finds 111+ evidences.*
