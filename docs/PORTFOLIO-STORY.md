# Моя Эволюция: От Zero IT к Cognitive Systems Architect

## 📖 Глава 1: Проблема (точка А)
Я начинала с нуля в IT без трекера навыков, с выгоранием от хаоса обучения, без инструментов для архитектурных решений и планирования карьеры. Рынок предлагал разрозненные инструменты, но ничего целостного для solo-архитектора, строящего экосистему для себя. Я начала создавать систему, чтобы отслеживать прогресс, автоматизировать мышление и доказывать компетенции.

## 📖 Глава 2: Инструменты, которые я создала для себя

### 🧭 IT-Compass
**Проблема**: Не могла отслеживать прогресс в IT-навыках от Zero, плюс психологическая нагрузка разработки.  
**Решение**: Трекер компетенций с поддержкой и портфолио-генерацией.  
**Артефакт**:  
- Код: `apps/it-compass/src/`  
- Демо: `docker compose up it-compass` → localhost:8501  
- Документация: `apps/it-compass/README.md`  
**Компетенция**: Системное мышление, Python UI, карьерный трекинг ⭐⭐⭐⭐⭐.  
**Уверенность**: 🟢95% — доказана в production, coverage 98%.

### 🧭 Arch-Compass-Framework
**Проблема**: Нужно было оркестрировать архитектурные решения в PowerShell безопасно.  
**Решение**: Модульный PS-фреймворк с secrets/gitleaks.  
**Артефакт**:  
- Код: `apps/arch-compass-framework/ArchCompass.psm1`  
- Демо: `Import-Module ArchCompass.psm1; Start-ArchCompass`  
- Документация: `apps/arch-compass-framework/README.md`  
**Компетенция**: DevOps, scripting, security ⭐⭐⭐⭐.  
**Уверенность**: 🟢90% — gitleaks integration active.

### 🧭 Cloud-Reason
**Проблема**: Ручное рассуждение над кодом/доками для валидации архитектуры.  
**Решение**: RAG API на FastAPI.  
**Артефакт**:  
- Код: `apps/cloud-reason/cloud_reason/`  
- Демо: `docker compose up cloud-reason` → localhost:8000/docs  
- Документация: `apps/cloud-reason/README.md`  
**Компетенция**: AI RAG, API design ⭐⭐⭐⭐.  
**Уверенность**: 🟢92% — OpenAPI ready.

### 🧭 Career-Development
**Проблема**: Личная дорожная карта карьеры без DB-планировщика.  
**Решение**: Alembic/FastAPI planner.  
**Артефакт**:  
- Код: `apps/career-development/career-development-system/src/`  
- Демо: localhost:8000/docs  
- Документация: `apps/career-development/README.md`  
**Компетенция**: Backend, planning ⭐⭐⭐⭐.  
**Уверенность**: 🟢88% — migrations ready.

### 🧭 ML-Model-Registry
**Проблема**: Версионирование ML-моделей в solo-разработке.  
**Решение**: FastAPI registry.  
**Артефакт**:  
- Код: `apps/ml-model-registry/ml-model-registry/`  
- Демо: localhost:8001/docs  
- Документация: `apps/ml-model-registry/README.md`  
**Компетенция**: MLOps ⭐⭐⭐.  
**Уверенность**: 🟢90% — SQLite backend.

### 🧭 Portfolio-Organizer
**Проблема**: Хаос в организации портфолио.  
**Решение**: Автоматизатор с web/API.  
**Артефакт**:  
- Код: `apps/portfolio-organizer/portfolio-organizer/`  
- Демо: localhost:8004  
- Документация: `apps/portfolio-organizer/portfolio-organizer/README.md`  
**Компетенция**: Full-stack mgmt ⭐⭐⭐⭐.  
**Уверенность**: 🟢92% — demo ready.

### 🧭 System-Proof
**Проблема**: Доказательство системности через traces.  
**Решение**: Proof schema для GigaChain.  
**Артефакт**:  
- Код: `apps/system-proof/proof_schema.py`  
- Документация: `apps/system-proof/README.md`  
**Компетенция**: Verification ⭐⭐⭐⭐.  
**Уверенность**: 🟢90% — integrates with RAG.

## 📖 Глава 3: Архитектура как доказательство мышления
- **7 ADR**: Решения по интеграции/безопасности (docs/adr/).  
- **C4-диаграммы**: diagrams/ (ecosystem view).  
- **docker-compose**: Воспроизводимость (docker-compose.yml + monitoring).  
- **monitoring/**: Grafana/Prometheus для observability.

## 📖 Глава 4: Результаты (точка Б)
Аудит BLACKBOXAI: Product-minded Cognitive Systems Architect 🟢92%.  
**Что могу**: Systemic design ⭐⭐⭐⭐⭐, Docs ⭐⭐⭐⭐⭐, Python ⭐⭐⭐⭐ (см. docs/docs/SKILLS.md).  
**Дам работодателю**: Экосистему для cognitive architecture, $150-250K remote level.

## 📎 Приложения
- GitHub: https://github.com/Control39/cognitive-systems-architecture  
- Demo: `docker compose up -d` → localhost:8501 (IT-Compass)  
- Аудит: docs/audit-2026-03.md

