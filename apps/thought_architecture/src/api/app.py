"""FastAPI app for thought_architecture."""

from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Моки для БД
decisions_db: dict[str, dict] = {}
records_db: dict[str, dict] = {}


# Модели
class Decision(BaseModel):
    id: str
    title: str
    description: str
    status: str
    created_at: datetime
    approver: str | None = None
    rejection_reason: str | None = None


class DecisionCreate(BaseModel):
    title: str
    description: str


class DecisionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


app = FastAPI(title="Thought Architecture API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ready")
async def ready():
    return {"status": "ready"}


@app.get("/live")
async def live():
    return {"status": "alive"}


# Эндпоинты для decisions
@app.post("/decisions")
async def create_decision(decision: DecisionCreate):
    decision_id = f"dec-{str(uuid4())[:8]}"
    new_decision = {
        "id": decision_id,
        "title": decision.title,
        "description": decision.description,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    decisions_db[decision_id] = new_decision
    return new_decision


@app.get("/decisions")
async def list_decisions():
    return list(decisions_db.values())


@app.get("/decisions/{decision_id}")
async def get_decision(decision_id: str):
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decisions_db[decision_id]


@app.put("/decisions/{decision_id}")
async def update_decision(decision_id: str, update: DecisionUpdate):
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    if update.title:
        decisions_db[decision_id]["title"] = update.title
    if update.description:
        decisions_db[decision_id]["description"] = update.description
    return decisions_db[decision_id]


@app.delete("/decisions/{decision_id}")
async def delete_decision(decision_id: str):
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    del decisions_db[decision_id]
    return {"status": "deleted"}


@app.put("/decisions/{decision_id}/approve")
async def approve_decision(decision_id: str, approver: str):
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    decisions_db[decision_id]["status"] = "approved"
    decisions_db[decision_id]["approver"] = approver
    return decisions_db[decision_id]


@app.put("/decisions/{decision_id}/reject")
async def reject_decision(decision_id: str, reason: str):
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    decisions_db[decision_id]["status"] = "rejected"
    decisions_db[decision_id]["rejection_reason"] = reason
    return decisions_db[decision_id]


__all__ = ["app", "decisions_db", "records_db"]
