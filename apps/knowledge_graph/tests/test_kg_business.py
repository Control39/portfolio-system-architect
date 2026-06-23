"""
Тесты для бизнес-логики Knowledge Graph.

Test Coverage:
- Entity CRUD operations
- Relationship management
- Entity indexing and searching
- Neighbor discovery
- Query execution
- Edge cases and validation
"""

import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apps.knowledge_graph.src.core.knowledge_graph import KnowledgeGraph  # noqa: E402
from apps.knowledge_graph.src.entities import (  # noqa: E402
    Entity,
    EntityType,
    Relationship,
    RelationshipType,
)


class TestKnowledgeGraphCRUD:
    """Тесты для базовых операций CRUD."""

    @pytest.fixture
    def kg(self):
        """Создать чистый граф знаний."""
        return KnowledgeGraph()

    def test_add_entity(self, kg):
        """Тест добавления сущности."""
        entity = Entity(
            id="test-001",
            name="Test Entity",
            type=EntityType.PROJECT,
            description="Test project",
        )

        result_id = kg.add_entity(entity)

        assert result_id == "test-001"
        assert kg.get_entity("test-001") == entity
        assert kg.entity_count == 1

    def test_get_nonexistent_entity(self, kg):
        """Тест получения несуществующей сущности."""
        entity = kg.get_entity("nonexistent")
        assert entity is None

    def test_add_relationship(self, kg):
        """Тест добавления отношения."""
        # Создаем сущности
        entity1 = Entity(
            id="entity-1",
            name="Entity 1",
            type=EntityType.PROJECT,
        )
        entity2 = Entity(
            id="entity-2",
            name="Entity 2",
            type=EntityType.TECHNOLOGY,
        )
        kg.add_entity(entity1)
        kg.add_entity(entity2)

        # Создаем отношение
        relationship = Relationship(
            id="rel-001",
            source_id="entity-1",
            target_id="entity-2",
            type=RelationshipType.USES,
        )

        result_id = kg.add_relationship(relationship)

        assert result_id == "rel-001"
        assert kg.get_relationship("rel-001") == relationship
        assert kg.relationship_count == 1

    def test_get_nonexistent_relationship(self, kg):
        """Тест получения несуществующего отношения."""
        relationship = kg.get_relationship("nonexistent")
        assert relationship is None

    def test_clear_graph(self, kg):
        """Тест очистки графа."""
        # Добавляем данные
        entity = Entity(id="e1", name="Test", type=EntityType.PROJECT)
        kg.add_entity(entity)
        kg.add_relationship(
            Relationship(
                id="r1",
                source_id="e1",
                target_id="e2",
                type=RelationshipType.USES,
            )
        )

        assert kg.entity_count == 1
        assert kg.relationship_count == 1

        kg.clear()

        assert kg.entity_count == 0
        assert kg.relationship_count == 0


class TestEntityIndexing:
    """Тесты индексации и поиска сущностей."""

    @pytest.fixture
    def kg_with_data(self):
        """Граф с тестовыми данными."""
        kg = KnowledgeGraph()

        # Добавляем сущности разных типов
        entities = [
            Entity(id="proj-1", name="Project A", type=EntityType.PROJECT),
            Entity(id="proj-2", name="Project B", type=EntityType.PROJECT),
            Entity(id="tech-1", name="FastAPI", type=EntityType.TECHNOLOGY),
            Entity(id="tech-2", name="Docker", type=EntityType.TECHNOLOGY),
            Entity(id="tech-3", name="Kubernetes", type=EntityType.TECHNOLOGY),
        ]

        for entity in entities:
            kg.add_entity(entity)

        return kg

    def test_find_entities_by_type(self, kg_with_data):
        """Тест поиска сущностей по типу."""
        projects = kg_with_data.find_entities_by_type(EntityType.PROJECT)
        assert len(projects) == 2

        technologies = kg_with_data.find_entities_by_type(EntityType.TECHNOLOGY)
        assert len(technologies) == 3

    def test_find_entities_limit(self, kg_with_data):
        """Тест ограничения результатов поиска."""
        technologies = kg_with_data.find_entities_by_type(EntityType.TECHNOLOGY, limit=2)
        assert len(technologies) == 2

    def test_find_nonexistent_type(self, kg_with_data):
        """Тест поиска несуществующего типа."""
        result = kg_with_data.find_entities_by_type(EntityType.DOCUMENT)
        assert len(result) == 0


class TestRelationshipQueries:
    """Тесты запросов к отношениям."""

    @pytest.fixture
    def kg_with_relationships(self):
        """Граф с отношениями."""
        kg = KnowledgeGraph()

        # Создаем сущности
        entities = [
            Entity(id="proj-1", name="Project A", type=EntityType.PROJECT),
            Entity(id="tech-1", name="FastAPI", type=EntityType.TECHNOLOGY),
            Entity(id="tech-2", name="Docker", type=EntityType.TECHNOLOGY),
        ]

        for entity in entities:
            kg.add_entity(entity)

        # Создаем отношения
        relationships = [
            Relationship(
                id="rel-1",
                source_id="proj-1",
                target_id="tech-1",
                type=RelationshipType.USES,
            ),
            Relationship(
                id="rel-2",
                source_id="proj-1",
                target_id="tech-2",
                type=RelationshipType.USES,
            ),
        ]

        for rel in relationships:
            kg.add_relationship(rel)

        return kg

    def test_find_relationships_by_source(self, kg_with_relationships):
        """Тест поиска отношений по source_id."""
        relations = kg_with_relationships.find_relationships(source_id="proj-1")
        assert len(relations) == 2

    def test_find_relationships_by_target(self, kg_with_relationships):
        """Тест поиска отношений по target_id."""
        relations = kg_with_relationships.find_relationships(target_id="tech-1")
        assert len(relations) == 1
        assert relations[0].id == "rel-1"

    def test_find_relationships_by_type(self, kg_with_relationships):
        """Тест поиска отношений по типу."""
        relations = kg_with_relationships.find_relationships(
            relationship_type=RelationshipType.USES
        )
        assert len(relations) == 2

    def test_find_relationships_combined_filters(self, kg_with_relationships):
        """Тест фильтрации по нескольким критериям."""
        relations = kg_with_relationships.find_relationships(
            source_id="proj-1",
            relationship_type=RelationshipType.USES,
        )
        assert len(relations) == 2

        # Фильтр, который не найдет ничего
        relations = kg_with_relationships.find_relationships(
            source_id="nonexistent",
            relationship_type=RelationshipType.USES,
        )
        assert len(relations) == 0


class TestNeighborDiscovery:
    """Тесты поиска соседних сущностей."""

    @pytest.fixture
    def kg_with_graph(self):
        """Граф с 연결ями."""
        kg = KnowledgeGraph()

        # Создаем сущности
        entities = [
            Entity(id="center", name="Center Project", type=EntityType.PROJECT),
            Entity(id="tech-1", name="FastAPI", type=EntityType.TECHNOLOGY),
            Entity(id="tech-2", name="Docker", type=EntityType.TECHNOLOGY),
            Entity(id="db-1", name="PostgreSQL", type=EntityType.DATABASE),
        ]

        for entity in entities:
            kg.add_entity(entity)

        # Создаем отношения (center использует все технологии)
        kg.add_relationship(
            Relationship(
                id="rel-1",
                source_id="center",
                target_id="tech-1",
                type=RelationshipType.USES,
            )
        )
        kg.add_relationship(
            Relationship(
                id="rel-2",
                source_id="center",
                target_id="tech-2",
                type=RelationshipType.USES,
            )
        )

        return kg

    def test_get_neighbors(self, kg_with_graph):
        """Тест получения соседних сущностей."""
        neighbors = kg_with_graph.get_neighbors("center")
        assert len(neighbors) == 2

        neighbor_names = {n.name for n in neighbors}
        assert "FastAPI" in neighbor_names
        assert "Docker" in neighbor_names

    def test_get_neighbors_isolated_entity(self, kg_with_graph):
        """Тест получения соседей для изолированной сущности."""
        neighbors = kg_with_graph.get_neighbors("db-1")
        assert len(neighbors) == 0

    def test_get_neighbors_nonexistent(self, kg_with_graph):
        """Тест получения соседей для несуществующей сущности."""
        neighbors = kg_with_graph.get_neighbors("nonexistent")
        assert len(neighbors) == 0


class TestGraphQueries:
    """Тесты выполнения запросов к графу."""

    @pytest.fixture
    def kg_with_data(self):
        """Граф с данными."""
        kg = KnowledgeGraph()

        # Добавляем сущности
        kg.add_entity(Entity(id="proj-1", name="Project A", type=EntityType.PROJECT))
        kg.add_entity(Entity(id="tech-1", name="FastAPI", type=EntityType.TECHNOLOGY))

        return kg

    def test_execute_find_entities_query(self, kg_with_data):
        """Тест выполнения запроса find_entities."""
        from apps.knowledge_graph.src.entities import GraphQuery

        query = GraphQuery(
            query_type="find_entities",
            parameters={"type": "project"},
            limit=10,
        )

        response = kg_with_data.execute_query(query)

        assert response.success is True
        assert len(response.entities or []) == 1
        assert response.entities[0].name == "Project A"

    def test_execute_find_relationships_query(self, kg_with_data):
        """Тест выполнения запроса find_relationships."""
        from apps.knowledge_graph.src.entities import GraphQuery

        query = GraphQuery(
            query_type="find_relationships",
            parameters={"source_id": "proj-1"},
            limit=10,
        )

        response = kg_with_data.execute_query(query)

        assert response.success is True
        assert response.relationships is not None

    def test_execute_unknown_query_type(self, kg_with_data):
        """Тест выполнения запроса с неизвестным типом."""
        from apps.knowledge_graph.src.entities import GraphQuery

        query = GraphQuery(
            query_type="unknown_type",
            parameters={},
        )

        response = kg_with_data.execute_query(query)

        assert response.success is False
        assert "Unknown query type" in response.message or ""

    def test_execute_neighbors_query(self, kg_with_data):
        """Тест выполнения запроса neighbors."""
        from apps.knowledge_graph.src.entities import GraphQuery

        query = GraphQuery(
            query_type="neighbors",
            parameters={"entity_id": "proj-1"},
        )

        response = kg_with_data.execute_query(query)

        assert response.success is True


class TestEdgeCases:
    """Тесты граничных случаев."""

    def test_empty_graph_operations(self):
        """Тест операций с пустым графом."""
        kg = KnowledgeGraph()

        assert kg.entity_count == 0
        assert kg.relationship_count == 0

        entities = kg.find_entities_by_type(EntityType.PROJECT)
        assert len(entities) == 0

        relations = kg.find_relationships(source_id="any")
        assert len(relations) == 0

    def test_entity_with_empty_description(self):
        """Тест сущности без описания."""
        kg = KnowledgeGraph()
        entity = Entity(
            id="test-1",
            name="Test",
            type=EntityType.PROJECT,
            description=None,
        )

        kg.add_entity(entity)
        retrieved = kg.get_entity("test-1")

        assert retrieved is not None
        assert retrieved.description is None

    def test_entity_with_metadata(self):
        """Тест сущности с метаданными."""
        kg = KnowledgeGraph()
        entity = Entity(
            id="test-1",
            name="Test",
            type=EntityType.PROJECT,
            metadata={"key1": "value1", "key2": 123},
        )

        kg.add_entity(entity)
        retrieved = kg.get_entity("test-1")

        assert retrieved.metadata["key1"] == "value1"
        assert retrieved.metadata["key2"] == 123

    def test_relationship_with_zero_weight(self):
        """Тест отношения с нулевым весом."""
        kg = KnowledgeGraph()
        kg.add_entity(Entity(id="e1", name="E1", type=EntityType.PROJECT))
        kg.add_entity(Entity(id="e2", name="E2", type=EntityType.TECHNOLOGY))

        relationship = Relationship(
            id="rel-1",
            source_id="e1",
            target_id="e2",
            type=RelationshipType.USES,
            weight=0.0,
        )

        kg.add_relationship(relationship)
        retrieved = kg.get_relationship("rel-1")

        assert retrieved is not None
        assert retrieved.weight == 0.0

    def test_duplicate_entity_id(self):
        """Тест добавления сущности с дублирующимся ID."""
        kg = KnowledgeGraph()

        entity1 = Entity(id="dup-1", name="First", type=EntityType.PROJECT)
        entity2 = Entity(id="dup-1", name="Second", type=EntityType.TECHNOLOGY)

        kg.add_entity(entity1)
        kg.add_entity(entity2)  # Должен перезаписать

        retrieved = kg.get_entity("dup-1")
        assert retrieved.name == "Second"  # Последняя запись
