"""
System Proof API — валидация критериев производственной готовности
"""

import os
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.system_proof.src.config_integration import get_config
    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    sp_config = config_manager.get_config()
    print("✅ System Proof: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  System Proof: AI Config Manager недоступен ({e}), используется локальный конфиг")
    sp_config = {}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Инициализация приложения
app = FastAPI(
    title="System Proof API",
    version="1.0.0",
    description="API для валидации критериев производственной готовности и генерации доказательств"
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "system-proof",
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

# Модели данных
class ProofStep(BaseModel):
    """Шаг доказательства"""
    step_id: str
    description: str
    evidence: str
    verified: bool = False
    verified_at: Optional[datetime] = None

class ProofRecord(BaseModel):
    """Запись доказательства"""
    proof_id: str
    architecture: str
    chain_id: str
    title: str
    description: str
    steps: List[ProofStep] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    status: str = "draft"  # draft, in_progress, verified, rejected

# Временное хранилище (для демонстрации)
proofs_db: dict[str, ProofRecord] = {}

# CRUD endpoints
@app.get("/proofs", response_model=List[ProofRecord])
async def list_proofs(
    architecture: Optional[str] = None,
    status: Optional[str] = None
):
    """Получить список доказательств"""
    proofs = list(proofs_db.values())
    
    if architecture:
        proofs = [p for p in proofs if p.architecture == architecture]
    if status:
        proofs = [p for p in proofs if p.status == status]
    
    return proofs

@app.post("/proofs", response_model=ProofRecord)
async def create_proof(proof: ProofRecord):
    """Создать новое доказательство"""
    if proof.proof_id in proofs_db:
        raise HTTPException(status_code=400, detail="Proof already exists")
    
    proof.created_at = datetime.now()
    proof.updated_at = datetime.now()
    proofs_db[proof.proof_id] = proof
    return proof

@app.get("/proofs/{proof_id}", response_model=ProofRecord)
async def get_proof(proof_id: str):
    """Получить доказательство по ID"""
    if proof_id not in proofs_db:
        raise HTTPException(status_code=404, detail="Proof not found")
    return proofs_db[proof_id]

@app.put("/proofs/{proof_id}", response_model=ProofRecord)
async def update_proof(proof_id: str, proof: ProofRecord):
    """Обновить доказательство"""
    if proof_id not in proofs_db:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    proof.updated_at = datetime.now()
    proofs_db[proof_id] = proof
    return proof

@app.delete("/proofs/{proof_id}")
async def delete_proof(proof_id: str):
    """Удалить доказательство"""
    if proof_id not in proofs_db:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    del proofs_db[proof_id]
    return {"message": "Proof deleted"}

# Business logic endpoints
@app.post("/proofs/{proof_id}/steps")
async def add_step(proof_id: str, step: ProofStep):
    """Добавить шаг к доказательству"""
    if proof_id not in proofs_db:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    proof = proofs_db[proof_id]
    proof.steps.append(step)
    proof.updated_at = datetime.now()
    return proof

@app.post("/proofs/{proof_id}/verify")
async def verify_proof(proof_id: str):
    """Верифицировать все шаги доказательства"""
    if proof_id not in proofs_db:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    proof = proofs_db[proof_id]
    for step in proof.steps:
        if not step.verified:
            step.verified = True
            step.verified_at = datetime.now()
    
    proof.status = "verified"
    proof.updated_at = datetime.now()
    return proof

# Statistics
@app.get("/statistics")
async def get_statistics():
    """Получить статистику по доказательствам"""
    total = len(proofs_db)
    verified = len([p for p in proofs_db.values() if p.status == "verified"])
    in_progress = len([p for p in proofs_db.values() if p.status == "in_progress"])
    draft = len([p for p in proofs_db.values() if p.status == "draft"])
    
    return {
        "total": total,
        "verified": verified,
        "in_progress": in_progress,
        "draft": draft
    }
