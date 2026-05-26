"""
Thought Architecture API — управление архитектурными решениями
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.thought_architecture.src.config_integration import get_config
    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    ta_config = config_manager.get_config()
    print("✅ Thought Architecture: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  Thought Architecture: AI Config Manager недоступен ({e}), используется локальный конфиг")
    ta_config = {}

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Инициализация приложения
app = FastAPI(
    title="Thought Architecture API",
    version="1.0.0",
    description="API для управления архитектурными решениями и решениями (ADRs)"
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "thought-architecture",
        "version": "1.0.0",
        "ai_config_available": AI_CONFIG_AVAILABLE
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe"""
    return {"status": "ready"}

@app.get("/live")
async def liveness_check():
    """Liveness probe"""
    return {"status": "alive"}

# Enums
class DecisionStatus(str, Enum):
    proposed = "proposed"
    accepted = "accepted"
    rejected = "rejected"
    superseded = "superseded"

class DecisionLevel(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

# Модели данных
class Decision(BaseModel):
    """Архитектурное решение"""
    decision_id: str
    title: str
    description: str
    status: DecisionStatus = DecisionStatus.proposed
    level: DecisionLevel = DecisionLevel.medium
    context: Optional[str] = None
    consequences: Optional[str] = None
    tags: List[str] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class ArchitectureRecord(BaseModel):
    """Запись архитектуры (содержит решения)"""
    record_id: str
    title: str
    description: str
    decisions: List[Decision] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

# Временное хранилище
decisions_db: dict[str, Decision] = {}
records_db: dict[str, ArchitectureRecord] = {}

# CRUD для решений
@app.get("/decisions", response_model=List[Decision])
async def list_decisions(
    status: Optional[DecisionStatus] = None,
    level: Optional[DecisionLevel] = None,
    tag: Optional[str] = None
):
    """Получить список решений"""
    decisions = list(decisions_db.values())
    
    if status:
        decisions = [d for d in decisions if d.status == status]
    if level:
        decisions = [d for d in decisions if d.level == level]
    if tag:
        decisions = [d for d in decisions if tag in d.tags]
    
    return decisions

@app.post("/decisions", response_model=Decision)
async def create_decision(decision: Decision):
    """Создать решение"""
    if decision.decision_id in decisions_db:
        raise HTTPException(status_code=400, detail="Decision already exists")
    
    decision.created_at = datetime.now()
    decision.updated_at = datetime.now()
    decisions_db[decision.decision_id] = decision
    return decision

@app.get("/decisions/search")
async def search_decisions(query: str = Query(..., description="Текст для поиска")):
    """Поиск решений по тексту"""
    results = []
    query_lower = query.lower()
    
    for decision in decisions_db.values():
        if (query_lower in decision.title.lower() or
            query_lower in decision.description.lower() or
            query_lower in (decision.context or "").lower() or
            any(query_lower in tag.lower() for tag in decision.tags)):
            results.append(decision)
    
    return results

@app.get("/decisions/{decision_id}", response_model=Decision)
async def get_decision(decision_id: str):
    """Получить решение по ID"""
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decisions_db[decision_id]

@app.put("/decisions/{decision_id}", response_model=Decision)
async def update_decision(decision_id: str, decision: Decision):
    """Обновить решение"""
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    decision.updated_at = datetime.now()
    decisions_db[decision_id] = decision
    return decision

@app.delete("/decisions/{decision_id}")
async def delete_decision(decision_id: str):
    """Удалить решение"""
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    del decisions_db[decision_id]
    return {"message": "Decision deleted"}

# Lifecycle operations
@app.put("/decisions/{decision_id}/approve")
async def approve_decision(decision_id: str, approver: str):
    """Одобрить решение"""
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    decision = decisions_db[decision_id]
    if decision.status != DecisionStatus.proposed:
        raise HTTPException(status_code=400, detail="Decision is not in proposed status")
    
    decision.status = DecisionStatus.accepted
    decision.approved_by = approver
    decision.approved_at = datetime.now()
    decision.updated_at = datetime.now()
    return decision

@app.put("/decisions/{decision_id}/reject")
async def reject_decision(decision_id: str, reason: str):
    """Отклонить решение"""
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    decision = decisions_db[decision_id]
    if decision.status != DecisionStatus.proposed:
        raise HTTPException(status_code=400, detail="Decision is not in proposed status")
    
    decision.status = DecisionStatus.rejected
    decision.consequences = f"Rejected: {reason}"
    decision.updated_at = datetime.now()
    return decision

@app.put("/decisions/{decision_id}/supersede")
async def supersede_decision(decision_id: str, new_decision_id: str):
    """Заменить решение новым"""
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    if new_decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="New decision not found")
    
    old_decision = decisions_db[decision_id]
    new_decision = decisions_db[new_decision_id]
    
    old_decision.status = DecisionStatus.superseded
    old_decision.updated_at = datetime.now()
    
    new_decision.updated_at = datetime.now()
    
    return {
        "superseded": old_decision,
        "replaced_by": new_decision
    }


# Statistics
@app.get("/statistics")
async def get_statistics():
    """Получить статистику по решениям"""
    status_counts = {}
    level_counts = {}
    tag_counts = {}
    
    for decision in decisions_db.values():
        # Status
        status = decision.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Level
        level = decision.level.value
        level_counts[level] = level_counts.get(level, 0) + 1
        
        # Tags
        for tag in decision.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    return {
        "total": len(decisions_db),
        "by_status": status_counts,
        "by_level": level_counts,
        "by_tag": tag_counts
    }

# CRUD для записей архитектуры
@app.get("/records", response_model=List[ArchitectureRecord])
async def list_records():
    """Получить список записей архитектуры"""
    return list(records_db.values())

@app.post("/records", response_model=ArchitectureRecord)
async def create_record(record: ArchitectureRecord):
    """Создать запись архитектуры"""
    if record.record_id in records_db:
        raise HTTPException(status_code=400, detail="Record already exists")
    
    record.created_at = datetime.now()
    record.updated_at = datetime.now()
    records_db[record.record_id] = record
    return record

@app.get("/records/{record_id}", response_model=ArchitectureRecord)
async def get_record(record_id: str):
    """Получить запись по ID"""
    if record_id not in records_db:
        raise HTTPException(status_code=404, detail="Record not found")
    return records_db[record_id]

@app.put("/records/{record_id}/add_decision")
async def add_decision_to_record(record_id: str, decision_id: str):
    """Добавить решение к записи"""
    if record_id not in records_db:
        raise HTTPException(status_code=404, detail="Record not found")
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    record = records_db[record_id]
    decision = decisions_db[decision_id]
    
    # Проверить, что решение ещё не добавлено
    if not any(d.decision_id == decision_id for d in record.decisions):
        record.decisions.append(decision)
        record.updated_at = datetime.now()
    
    return record

@app.delete("/records/{record_id}")
async def delete_record(record_id: str):
    """Удалить запись"""
    if record_id not in records_db:
        raise HTTPException(status_code=404, detail="Record not found")
    
    del records_db[record_id]
    return {"message": "Record deleted"}
