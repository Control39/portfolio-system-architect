"""
Knowledge Graph API — управление графом знаний
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.knowledge_graph.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    kg_config = config_manager.get_config()
    print("✅ Knowledge Graph: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(
        f"⚠️  Knowledge Graph: AI Config Manager недоступен ({e}), используется локальный конфиг"
    )
    kg_config = {}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Инициализация приложения
app = FastAPI(
    title="Knowledge Graph API",
    version="1.0.0",
    description="API для управления графом знаний: сущности, отношения, запросы",
)


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "knowledge-graph",
        "version": "1.0.0",
        "ai_config_available": AI_CONFIG_AVAILABLE,
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
class Entity(BaseModel):
    """Сущность графа знаний"""

    entity_id: str
    entity_type: str
    properties: Dict[str, Any] = {}
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class Relationship(BaseModel):
    """Отношение между сущностями"""

    relationship_id: str
    source_entity: str
    target_entity: str
    relationship_type: str
    properties: Dict[str, Any] = {}
    created_at: datetime = datetime.now()


# Временное хранилище
entities_db: dict[str, Entity] = {}
relationships_db: dict[str, Relationship] = {}


# CRUD для сущностей
@app.get("/entities", response_model=List[Entity])
async def list_entities(entity_type: Optional[str] = None):
    """Получить список сущностей"""
    entities = list(entities_db.values())
    if entity_type:
        entities = [e for e in entities if e.entity_type == entity_type]
    return entities


@app.post("/entities", response_model=Entity)
async def create_entity(entity: Entity):
    """Создать сущность"""
    if entity.entity_id in entities_db:
        raise HTTPException(status_code=400, detail="Entity already exists")

    entity.created_at = datetime.now()
    entity.updated_at = datetime.now()
    entities_db[entity.entity_id] = entity
    return entity


@app.get("/entities/{entity_id}", response_model=Entity)
async def get_entity(entity_id: str):
    """Получить сущность по ID"""
    if entity_id not in entities_db:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entities_db[entity_id]


@app.put("/entities/{entity_id}", response_model=Entity)
async def update_entity(entity_id: str, entity: Entity):
    """Обновить сущность"""
    if entity_id not in entities_db:
        raise HTTPException(status_code=404, detail="Entity not found")

    entity.updated_at = datetime.now()
    entities_db[entity_id] = entity
    return entity


@app.delete("/entities/{entity_id}")
async def delete_entity(entity_id: str):
    """Удалить сущность"""
    if entity_id not in entities_db:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Удалить связанные отношения
    relationships_to_delete = [
        r.relationship_id
        for r in relationships_db.values()
        if r.source_entity == entity_id or r.target_entity == entity_id
    ]
    for rel_id in relationships_to_delete:
        del relationships_db[rel_id]

    del entities_db[entity_id]
    return {"message": "Entity deleted"}


# CRUD для отношений
@app.get("/relationships", response_model=List[Relationship])
async def list_relationships(
    source: Optional[str] = None,
    target: Optional[str] = None,
    relationship_type: Optional[str] = None,
):
    """Получить список отношений"""
    relationships = list(relationships_db.values())

    if source:
        relationships = [r for r in relationships if r.source_entity == source]
    if target:
        relationships = [r for r in relationships if r.target_entity == target]
    if relationship_type:
        relationships = [r for r in relationships if r.relationship_type == relationship_type]

    return relationships


@app.post("/relationships", response_model=Relationship)
async def create_relationship(relationship: Relationship):
    """Создать отношение"""
    if relationship.relationship_id in relationships_db:
        raise HTTPException(status_code=400, detail="Relationship already exists")

    # Проверить существование сущностей
    if relationship.source_entity not in entities_db:
        raise HTTPException(status_code=404, detail="Source entity not found")
    if relationship.target_entity not in entities_db:
        raise HTTPException(status_code=404, detail="Target entity not found")

    relationships_db[relationship.relationship_id] = relationship
    return relationship


@app.get("/relationships/{relationship_id}", response_model=Relationship)
async def get_relationship(relationship_id: str):
    """Получить отношение по ID"""
    if relationship_id not in relationships_db:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return relationships_db[relationship_id]


@app.delete("/relationships/{relationship_id}")
async def delete_relationship(relationship_id: str):
    """Удалить отношение"""
    if relationship_id not in relationships_db:
        raise HTTPException(status_code=404, detail="Relationship not found")

    del relationships_db[relationship_id]
    return {"message": "Relationship deleted"}


# Графовые запросы
@app.get("/entities/{entity_id}/neighbors")
async def get_neighbors(entity_id: str, limit: int = 100):
    """Получить соседей сущности"""
    if entity_id not in entities_db:
        raise HTTPException(status_code=404, detail="Entity not found")

    neighbors = set()
    for rel in relationships_db.values():
        if rel.source_entity == entity_id:
            neighbors.add(rel.target_entity)
        elif rel.target_entity == entity_id:
            neighbors.add(rel.source_entity)

    neighbor_entities = [entities_db[nid] for nid in list(neighbors)[:limit] if nid in entities_db]

    return {"entity_id": entity_id, "neighbors": neighbor_entities, "count": len(neighbor_entities)}


@app.get("/query")
async def execute_query(
    entity_type: Optional[str] = None, relationship_type: Optional[str] = None, limit: int = 100
):
    """Выполнить графовый запрос"""
    results = {"entities": [], "relationships": []}

    # Фильтрация сущностей
    entities = list(entities_db.values())
    if entity_type:
        entities = [e for e in entities if e.entity_type == entity_type]
    results["entities"] = entities[:limit]

    # Фильтрация отношений
    relationships = list(relationships_db.values())
    if relationship_type:
        relationships = [r for r in relationships if r.relationship_type == relationship_type]
    results["relationships"] = relationships[:limit]

    return results


# Статистика
@app.get("/statistics")
async def get_statistics():
    """Получить статистику графа"""
    entity_types = {}
    for entity in entities_db.values():
        etype = entity.entity_type
        entity_types[etype] = entity_types.get(etype, 0) + 1

    relationship_types = {}
    for rel in relationships_db.values():
        rtype = rel.relationship_type
        relationship_types[rtype] = relationship_types.get(rtype, 0) + 1

    return {
        "total_entities": len(entities_db),
        "total_relationships": len(relationships_db),
        "entity_types": entity_types,
        "relationship_types": relationship_types,
    }
