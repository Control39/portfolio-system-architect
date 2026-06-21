"""
Менеджер графа знаний для Cognitive Agent
"""

import hashlib
from datetime import datetime
from typing import Any

import networkx as nx

from ..common.base_logger import BaseLogger
from ..common.base_security import BaseSecurityChecker
from ..common.exceptions import DataProcessingError, ValidationError


class KnowledgeGraphNode:
    """
    Узел графа знаний
    """

    def __init__(self, node_id: str, node_type: str, properties: dict[str, Any]):
        """
        Инициализировать узел графа знаний

        Args:
            node_id: Уникальный ID узла
            node_type: Тип узла (например, 'file', 'function', 'class', 'module', 'dependency')
            properties: Свойства узла
        """
        self.id = node_id
        self.type = node_type
        self.properties = properties
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update_properties(self, properties: dict[str, Any]):
        """
        Обновить свойства узла

        Args:
            properties: Новые свойства
        """
        self.properties.update(properties)
        self.updated_at = datetime.now()


class KnowledgeGraphEdge:
    """
    Ребро графа знаний
    """

    def __init__(self, source_id: str, target_id: str, relation_type: str, properties: dict[str, Any]):
        """
        Инициализировать ребро графа знаний

        Args:
            source_id: ID исходного узла
            target_id: ID целевого узла
            relation_type: Тип отношения (например, 'calls', 'imports', 'inherits', 'uses')
            properties: Свойства ребра
        """
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.properties = properties
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class KnowledgeGraphManager:
    """
    Менеджер графа знаний для Cognitive Agent
    """

    def __init__(self, logger: BaseLogger | None = None, security_checker: BaseSecurityChecker | None = None):
        """
        Инициализировать менеджер графа знаний

        Args:
            logger: Логгер для записи событий
            security_checker: Проверяльщик безопасности
        """
        self.logger = logger or BaseLogger("KnowledgeGraphManager")
        self.security_checker = security_checker or BaseSecurityChecker()

        # Используем NetworkX для внутреннего представления графа
        self.graph = nx.MultiDiGraph()

        self.logger.info("Менеджер графа знаний инициализирован")

    def add_node(self, node_id: str, node_type: str, properties: dict[str, Any]) -> bool:
        """
        Добавить узел в граф

        Args:
            node_id: Уникальный ID узла
            node_type: Тип узла
            properties: Свойства узла

        Returns:
            Успешно ли добавлен узел
        """
        try:
            # Проверить безопасность ID узла
            is_safe, message = self.security_checker.validate_path(node_id)
            if not is_safe:
                raise ValidationError(f"Небезопасный ID узла: {message}", details={"node_id": node_id})

            node = KnowledgeGraphNode(node_id, node_type, properties)

            # Добавить узел в граф NetworkX
            self.graph.add_node(
                node_id, type=node_type, properties=properties, created_at=node.created_at, updated_at=node.updated_at
            )

            self.logger.debug(f"Добавлен узел в граф знаний: {node_id} (тип: {node_type})")
            return True
        except Exception as e:
            self.logger.error(
                f"Ошибка при добавлении узла в граф знаний: {str(e)}", node_id=node_id, node_type=node_type
            )
            raise DataProcessingError(
                f"Ошибка добавления узла: {str(e)}", details={"node_id": node_id, "node_type": node_type}
            )

    def add_edge(
        self, source_id: str, target_id: str, relation_type: str, properties: dict[str, Any] | None = None
    ) -> bool:
        """
        Добавить ребро в граф

        Args:
            source_id: ID исходного узла
            target_id: ID целевого узла
            relation_type: Тип отношения
            properties: Свойства ребра

        Returns:
            Успешно ли добавлено ребро
        """
        try:
            # Проверить существование узлов
            if not self.graph.has_node(source_id):
                raise ValidationError(f"Исходный узел не существует: {source_id}", details={"source_id": source_id})
            if not self.graph.has_node(target_id):
                raise ValidationError(f"Целевой узел не существует: {target_id}", details={"target_id": target_id})

            # Проверить безопасность ID
            for node_id in [source_id, target_id]:
                is_safe, message = self.security_checker.validate_path(node_id)
                if not is_safe:
                    raise ValidationError(f"Небезопасный ID узла: {message}", details={"node_id": node_id})

            properties = properties or {}
            edge = KnowledgeGraphEdge(source_id, target_id, relation_type, properties)

            # Добавить ребро в граф NetworkX
            self.graph.add_edge(
                source_id,
                target_id,
                relation_type=relation_type,
                properties=properties,
                created_at=edge.created_at,
                updated_at=edge.updated_at,
            )

            self.logger.debug(f"Добавлено ребро в граф знаний: {source_id} -> {target_id} ({relation_type})")
            return True
        except Exception as e:
            self.logger.error(
                f"Ошибка при добавлении ребра в граф знаний: {str(e)}",
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
            )
            raise DataProcessingError(
                f"Ошибка добавления ребра: {str(e)}",
                details={"source_id": source_id, "target_id": target_id, "relation_type": relation_type},
            )

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """
        Получить узел по ID

        Args:
            node_id: ID узла

        Returns:
            Информация об узле или None, если узел не найден
        """
        try:
            if self.graph.has_node(node_id):
                node_data = self.graph.nodes[node_id]
                return {
                    "id": node_id,
                    "type": node_data.get("type"),
                    "properties": node_data.get("properties", {}),
                    "created_at": node_data.get("created_at"),
                    "updated_at": node_data.get("updated_at"),
                }
            return None
        except Exception as e:
            self.logger.error(f"Ошибка при получении узла из графа знаний: {str(e)}", node_id=node_id)
            return None

    def get_neighbors(self, node_id: str, direction: str = "both") -> list[dict[str, Any]]:
        """
        Получить соседей узла

        Args:
            node_id: ID узла
            direction: Направление ('in', 'out', 'both')

        Returns:
            Список соседних узлов
        """
        try:
            neighbors = []

            if direction in ["out", "both"]:
                # Исходящие ребра
                for neighbor_id in self.graph.successors(node_id):
                    edge_data = self.graph.get_edge_data(node_id, neighbor_id)
                    neighbors.append(
                        {
                            "neighbor_id": neighbor_id,
                            "relation_type": list(edge_data.keys())[0] if edge_data else "unknown",
                            "direction": "out",
                        }
                    )

            if direction in ["in", "both"]:
                # Входящие ребра
                for neighbor_id in self.graph.predecessors(node_id):
                    edge_data = self.graph.get_edge_data(neighbor_id, node_id)
                    neighbors.append(
                        {
                            "neighbor_id": neighbor_id,
                            "relation_type": list(edge_data.keys())[0] if edge_data else "unknown",
                            "direction": "in",
                        }
                    )

            return neighbors
        except Exception as e:
            self.logger.error(f"Ошибка при получении соседей узла: {str(e)}", node_id=node_id)
            return []

    def find_nodes_by_type(self, node_type: str) -> list[dict[str, Any]]:
        """
        Найти узлы по типу

        Args:
            node_type: Тип узла для поиска

        Returns:
            Список узлов заданного типа
        """
        try:
            nodes = []
            for node_id in self.graph.nodes():
                node_data = self.graph.nodes[node_id]
                if node_data.get("type") == node_type:
                    nodes.append(
                        {
                            "id": node_id,
                            "type": node_data.get("type"),
                            "properties": node_data.get("properties", {}),
                            "created_at": node_data.get("created_at"),
                            "updated_at": node_data.get("updated_at"),
                        }
                    )
            return nodes
        except Exception as e:
            self.logger.error(f"Ошибка при поиске узлов по типу: {str(e)}", node_type=node_type)
            return []

    def find_path(self, source_id: str, target_id: str) -> list[str] | None:
        """
        Найти путь между двумя узлами

        Args:
            source_id: ID исходного узла
            target_id: ID целевого узла

        Returns:
            Список ID узлов в пути или None, если путь не найден
        """
        try:
            if nx.has_path(self.graph, source_id, target_id):
                path = nx.shortest_path(self.graph, source_id, target_id)
                return path
            return None
        except Exception as e:
            self.logger.error(
                f"Ошибка при поиске пути между узлами: {str(e)}", source_id=source_id, target_id=target_id
            )
            return None

    def get_subgraph(self, center_node: str, radius: int = 2) -> dict[str, Any]:
        """
        Получить подграф вокруг центрального узла

        Args:
            center_node: Центральный узел
            radius: Радиус подграфа (количество шагов от центрального узла)

        Returns:
            Подграф в виде словаря
        """
        try:
            subgraph_nodes = nx.ego_graph(self.graph, center_node, radius=radius)
            subgraph = self.graph.subgraph(subgraph_nodes)

            result = {"center_node": center_node, "nodes": [], "edges": []}

            for node_id in subgraph.nodes():
                node_data = subgraph.nodes[node_id]
                result["nodes"].append(
                    {"id": node_id, "type": node_data.get("type"), "properties": node_data.get("properties", {})}
                )

            for source_id, target_id, edge_data in subgraph.edges(data=True):
                result["edges"].append(
                    {
                        "source": source_id,
                        "target": target_id,
                        "relation_type": edge_data.get("relation_type"),
                        "properties": edge_data.get("properties", {}),
                    }
                )

            return result
        except Exception as e:
            self.logger.error(f"Ошибка при получении подграфа: {str(e)}", center_node=center_node, radius=radius)
            return {"center_node": center_node, "nodes": [], "edges": []}

    def update_node_properties(self, node_id: str, properties: dict[str, Any]) -> bool:
        """
        Обновить свойства узла

        Args:
            node_id: ID узла
            properties: Новые свойства

        Returns:
            Успешно ли обновлены свойства
        """
        try:
            if not self.graph.has_node(node_id):
                return False

            # Обновить свойства в графе
            current_data = self.graph.nodes[node_id]
            current_data["properties"].update(properties)
            current_data["updated_at"] = datetime.now()

            self.logger.debug(f"Обновлены свойства узла: {node_id}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении свойств узла: {str(e)}", node_id=node_id)
            return False

    def remove_node(self, node_id: str) -> bool:
        """
        Удалить узел из графа

        Args:
            node_id: ID узла для удаления

        Returns:
            Успешно ли удален узел
        """
        try:
            if self.graph.has_node(node_id):
                self.graph.remove_node(node_id)
                self.logger.debug(f"Удален узел из графа: {node_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при удалении узла из графа: {str(e)}", node_id=node_id)
            return False

    def get_statistics(self) -> dict[str, Any]:
        """
        Получить статистику графа

        Returns:
            Статистика графа
        """
        try:
            return {
                "node_count": self.graph.number_of_nodes(),
                "edge_count": self.graph.number_of_edges(),
                "density": nx.density(self.graph),
                "connected_components": nx.number_weakly_connected_components(self.graph),
                "node_types": {
                    data.get("type"): sum(
                        1 for n, nd in self.graph.nodes(data=True) if nd.get("type") == data.get("type")
                    )
                    for data in [self.graph.nodes[n] for n in self.graph.nodes()]
                },
                "relation_types": {
                    key: sum(1 for u, v, d in self.graph.edges(data=True) if d.get("relation_type") == key)
                    for key in set(d.get("relation_type") for u, v, d in self.graph.edges(data=True))
                },
            }
        except Exception as e:
            self.logger.error(f"Ошибка при получении статистики графа: {str(e)}")
            return {
                "node_count": 0,
                "edge_count": 0,
                "density": 0,
                "connected_components": 0,
                "node_types": {},
                "relation_types": {},
            }

    def export_to_dict(self) -> dict[str, Any]:
        """
        Экспортировать граф в словарь

        Returns:
            Граф в виде словаря
        """
        try:
            result = {
                "nodes": [],
                "edges": [],
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "node_count": self.graph.number_of_nodes(),
                    "edge_count": self.graph.number_of_edges(),
                },
            }

            for node_id in self.graph.nodes():
                node_data = self.graph.nodes[node_id]
                result["nodes"].append(
                    {
                        "id": node_id,
                        "type": node_data.get("type"),
                        "properties": node_data.get("properties", {}),
                        "created_at": node_data.get("created_at").isoformat() if node_data.get("created_at") else None,
                        "updated_at": node_data.get("updated_at").isoformat() if node_data.get("updated_at") else None,
                    }
                )

            for source_id, target_id, key, edge_data in self.graph.edges(data=True, keys=True):
                result["edges"].append(
                    {
                        "source": source_id,
                        "target": target_id,
                        "relation_type": edge_data.get("relation_type"),
                        "properties": edge_data.get("properties", {}),
                        "created_at": edge_data.get("created_at").isoformat() if edge_data.get("created_at") else None,
                        "updated_at": edge_data.get("updated_at").isoformat() if edge_data.get("updated_at") else None,
                    }
                )

            return result
        except Exception as e:
            self.logger.error(f"Ошибка при экспорте графа: {str(e)}")
            return {"nodes": [], "edges": [], "metadata": {}}


class KnowledgeGraphIntegrator:
    """
    Интегратор графа знаний с другими компонентами агента
    """

    def __init__(self, kg_manager: KnowledgeGraphManager, logger: BaseLogger | None = None):
        """
        Инициализировать интегратор графа знаний

        Args:
            kg_manager: Менеджер графа знаний
            logger: Логгер для записи событий
        """
        self.kg_manager = kg_manager
        self.logger = logger or BaseLogger("KnowledgeGraphIntegrator")

        self.logger.info("Интегратор графа знаний инициализирован")

    def enrich_with_project_data(self, project_context: dict[str, Any]) -> bool:
        """
        Обогатить граф знаний данными проекта

        Args:
            project_context: Контекст проекта

        Returns:
            Успешно ли выполнено обогащение
        """
        try:
            scan_results = project_context.get("scan_results", {})
            files = scan_results.get("files", [])

            # Добавить файлы как узлы
            for file_info in files:
                file_path = file_info.get("path", "")
                file_id = hashlib.md5(file_path.encode()).hexdigest()

                self.kg_manager.add_node(
                    node_id=f"file_{file_id}",
                    node_type="file",
                    properties={
                        "path": file_path,
                        "absolute_path": file_info.get("absolute_path"),
                        "size": file_info.get("size"),
                        "extension": file_info.get("extension"),
                        "modified": file_info.get("modified"),
                    },
                )

            # Добавить зависимости между файлами
            tech_stack = scan_results.get("tech_stack", {})
            for tech, tech_info in tech_stack.items():
                tech_id = hashlib.md5(tech.encode()).hexdigest()

                self.kg_manager.add_node(
                    node_id=f"tech_{tech_id}",
                    node_type="technology",
                    properties={
                        "name": tech,
                        "confidence": tech_info.get("confidence"),
                        "extensions": tech_info.get("extensions"),
                    },
                )

                # Связать технологию с файлами
                for file_path in tech_info.get("files", []):
                    file_id = hashlib.md5(file_path.encode()).hexdigest()
                    self.kg_manager.add_edge(
                        source_id=f"tech_{tech_id}", target_id=f"file_{file_id}", relation_type="uses"
                    )

            self.logger.info("Граф знаний обогащен данными проекта", file_count=len(files), tech_count=len(tech_stack))
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при обогащении графа знаний данными проекта: {str(e)}")
            return False

    def query_related_entities(self, entity_id: str, relation_types: list[str] = None) -> list[dict[str, Any]]:
        """
        Запросить связанные сущности

        Args:
            entity_id: ID сущности
            relation_types: Типы отношений для фильтрации

        Returns:
            Список связанных сущностей
        """
        try:
            neighbors = self.kg_manager.get_neighbors(entity_id)

            if relation_types:
                neighbors = [n for n in neighbors if n["relation_type"] in relation_types]

            related_entities = []
            for neighbor in neighbors:
                node_info = self.kg_manager.get_node(neighbor["neighbor_id"])
                if node_info:
                    related_entities.append(
                        {"entity": node_info, "relation": neighbor["relation_type"], "direction": neighbor["direction"]}
                    )

            return related_entities
        except Exception as e:
            self.logger.error(f"Ошибка при запросе связанных сущностей: {str(e)}", entity_id=entity_id)
            return []

    def find_architectural_patterns(self) -> list[dict[str, Any]]:
        """
        Найти архитектурные паттерны в графе знаний

        Returns:
            Список найденных архитектурных паттернов
        """
        try:
            patterns = []

            # Найти потенциальные зависимости между модулями
            module_nodes = self.kg_manager.find_nodes_by_type("file")

            for node in module_nodes:
                neighbors = self.kg_manager.get_neighbors(node["id"])

                # Проверить наличие циклических зависимостей
                for neighbor in neighbors:
                    if neighbor["direction"] == "out":  # Исходящие зависимости
                        path_back = self.kg_manager.find_path(neighbor["neighbor_id"], node["id"])
                        if path_back and len(path_back) > 1:
                            patterns.append(
                                {
                                    "type": "circular_dependency",
                                    "entities": [node["id"], neighbor["neighbor_id"]],
                                    "path": path_back,
                                    "severity": "high",
                                }
                            )

            self.logger.info("Поиск архитектурных паттернов завершен", pattern_count=len(patterns))
            return patterns
        except Exception as e:
            self.logger.error(f"Ошибка при поиске архитектурных паттернов: {str(e)}")
            return []
