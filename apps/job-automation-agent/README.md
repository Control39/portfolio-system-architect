# Job Automation Agent - AI Карьерный Копилот

**Максимальная автоматизация поиска работы**: Core Agent оркестрирует JobSearch (hh.ru), Resume (Jinja2+LLM), Analysis (pandas+DB).

## 🚀 Quickstart
1. `cd apps/job-automation-agent`
2. `pip install -r ../career-development/requirements.txt`
3. `export OPENAI_API_KEY=sk-...` (or .env)
4. `cd src/api && uvicorn main:app --reload` → http://localhost:8001/docs

## API Endpoints
- `POST /core/run`: "Найди Python вакансии и резюме"
- `GET /jobs/search/{query}`: hh.ru search
- `POST /resume/generate`: { "title": "job" }

## Docker
```
docker compose -f docker-compose.agent.yml up
```

## Профилирование (cProfile)
```
python -m cProfile -s time src/core/orchestrator.py
```

## Troubleshooting
- No API key: Mock LLM (edit orchestrator.py)
- DB: Use postgres/ or docker.
- Errors: Check TODO.md

**Интеграция**: career-development skills → analysis.

See TODO.md for roadmap.
