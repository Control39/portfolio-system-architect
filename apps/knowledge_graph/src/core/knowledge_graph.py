"""
Ядро графа знаний - хранение и запросы к сущностям и отношениям.
"""

from ..entities import Entity, EntityType, GraphQuery, GraphResponse, Relationship, RelationshipType


class KnowledgeGraph:
    """Граф знаний для хранения и поиска сущностей и отношений."""

    def __init__(self):
        """Инициализация графа знаний."""
        self._entities: dict[str, Entity] = {}
        self._relationships: dict[str, Relationship] = {}
        self._entity_index: dict[EntityType, set[str]] = {}
        self._relationship_index: dict[str, set[str]] = {}  # source_id -> relationship_ids

    def add_entity(self, entity: Entity) -> str:
        """
        Добавить сущность в граф.

        Args:
            entity: Сущность для добавления

        Returns:
            ID сущности
        """
        self._entities[entity.id] = entity

        # Индексация по типу
        if entity.type not in self._entity_index:
            self._entity_index[entity.type] = set()
        self._entity_index[entity.type].add(entity.id)

        return entity.id

    def add_relationship(self, relationship: Relationship) -> str:
        """
        Добавить отношение в граф.

        Args:
            relationship: Отношение для добавления

        Returns:
            ID отношения
        """
        self._relationships[relationship.id] = relationship

        # Индексация по source_id
        if relationship.source_id not in self._relationship_index:
            self._relationship_index[relationship.source_id] = set()
        self._relationship_index[relationship.source_id].add(relationship.id)

        return relationship.id

    def get_entity(self, entity_id: str) -> Entity | None:
        """Получить сущность по ID."""
        return self._entities.get(entity_id)

    def get_relationship(self, relationship_id: str) -> Relationship | None:
        """Получить отношение по ID."""
        return self._relationships.get(relationship_id)

    def find_entities_by_type(self, entity_type: EntityType, limit: int = 100) -> list[Entity]:
        """Найти сущности по типу."""
        entity_ids = self._entity_index.get(entity_type, set())
        result = []
        for entity_id in list(entity_ids)[:limit]:
            if entity := self._entities.get(entity_id):
                result.append(entity)
        return result

    def find_relationships(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
        relationship_type: RelationshipType | None = None,
        limit: int = 100,
    ) -> list[Relationship]:
        """Найти отношения по критериям."""
        result = []

        for rel in self._relationships.values():
            # Фильтрация по source_id
            if source_id and rel.source_id != source_id:
                continue
            # Фильтрация по target_id
            if target_id and rel.target_id != target_id:
                continue
            # Фильтрация по типу
            if relationship_type and rel.type != relationship_type:
                continue

            result.append(rel)
            if len(result) >= limit:
                break

        return result

    def get_neighbors(self, entity_id: str) -> list[Entity]:
        """Получить соседние сущности (connected Entities)."""
        neighbors: dict[str, Entity] = {}

        # Отношения, где эта сущность - источник
        for rel_id in self._relationship_index.get(entity_id, set()):
            if rel := self._relationships.get(rel_id):  # noqa: SIM102
                if target := self._entities.get(rel.target_id):
                    neighbors[rel.target_id] = target

        # Отношения, где эта сущность - цель
        for rel in self._relationships.values():
            if rel.target_id == entity_id and (source := self._entities.get(rel.source_id)):
                neighbors[rel.source_id] = source

        return list(neighbors.values())

    def execute_query(self, query: GraphQuery) -> GraphResponse:
        """Выполнить запрос к графу знаний."""
        import time

        start_time = time.time()

        try:
            if query.query_type == "find_entities":
                entity_type_str = query.parameters.get("type")
                if entity_type_str:
                    try:
                        entity_type = EntityType(entity_type_str)
                        entities = self.find_entities_by_type(entity_type, query.limit or 100)
                    except ValueError:
                        entities = []
                else:
                    entities = list(self._entities.values())[: (query.limit or 100)]

                processing_time = (time.time() - start_time) * 1000
                return GraphResponse(
                    success=True,
                    entities=entities,
                    processing_time_ms=processing_time,
                )

            if query.query_type == "find_relationships":
                source_id = query.parameters.get("source_id")
                target_id = query.parameters.get("target_id")
                rel_type_str = query.parameters.get("type")

                rel_type = RelationshipType(rel_type_str) if rel_type_str else None
                relationships = self.find_relationships(
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=rel_type,
                    limit=query.limit or 100,
                )

                processing_time = (time.time() - start_time) * 1000
                return GraphResponse(
                    success=True,
                    relationships=relationships,
                    processing_time_ms=processing_time,
                )

            if query.query_type == "neighbors":
                entity_id = query.parameters.get("entity_id")
                if not entity_id:
                    return GraphResponse(
                        success=False,
                        message="entity_id required for neighbors query",
                        processing_time_ms=(time.time() - start_time) * 1000,
                    )

                neighbors = self.get_neighbors(entity_id)
                processing_time = (time.time() - start_time) * 1000
                return GraphResponse(
                    success=True,
                    entities=neighbors,
                    processing_time_ms=processing_time,
                )

            processing_time = (time.time() - start_time) * 1000
            return GraphResponse(
                success=False,
                message=f"Unknown query type: {query.query_type}",
                processing_time_ms=processing_time,
            )

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return GraphResponse(
                success=False,
                message=str(e),
                processing_time_ms=processing_time,
            )

    def clear(self) -> None:
        """Очистить граф."""
        self._entities.clear()
        self._relationships.clear()
        self._entity_index.clear()
        self._relationship_index.clear()

    @property
    def entity_count(self) -> int:
        """Количество сущностей."""
        return len(self._entities)

    @property
    def relationship_count(self) -> int:
        """Количество отношений."""
        return len(self._relationships)
