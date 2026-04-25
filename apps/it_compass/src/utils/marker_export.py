"""Модуль экспорта маркеров для интеграции с LLM и RAG-системами.
"""

import json
import logging
from pathlib import Path

from ..core.tracker import CareerTracker, Marker

logger = logging.getLogger(__name__)


class MarkerExporter:
    """Класс для экспорта маркеров в различные форматы для LLM и RAG-поиска."""

    def __init__(self, tracker: CareerTracker):
        self.tracker = tracker

    def export_to_llm_format(self, output_path: str) -> bool:
        """Экспортирует маркеры в формат, понятный LLM (JSON Schema).

        Args:
            output_path: Путь к файлу для сохранения экспорта

        Returns:
            bool: True если экспорт успешен, False в случае ошибки

        """
        try:
            # Собираем все маркеры в формате, удобном для LLM
            llm_data = {
                "competency_markers": [],
                "metadata": {
                    "export_timestamp": str(Path(__file__).stat().st_mtime),
                    "total_markers": 0,
                    "total_skills": len(self.tracker.markers),
                },
            }

            # Добавляем маркеры по навыкам
            for skill_name, skill_data in self.tracker.markers.items():
                skill_markers = []
                for level_name, level_markers in skill_data.levels.items():
                    for marker in level_markers:
                        marker_dict = {
                            "id": marker.id,
                            "skill": skill_name,
                            "level": level_name,
                            "description": marker.marker,
                            "validation_criteria": marker.validation,
                            "priority": marker.priority,
                            "resources": marker.resources,
                            "smart_criteria": marker.smart_criteria,
                            "tags": self._generate_tags(marker, skill_name, level_name),
                            "estimated_time": marker.smart_criteria.get("time_bound", ""),
                            "methodology": {
                                "author": marker.methodology_author,
                                "license": marker.methodology_license,
                            },
                        }
                        skill_markers.append(marker_dict)

                llm_data["competency_markers"].extend(skill_markers)

            llm_data["metadata"]["total_markers"] = len(llm_data["competency_markers"])

            # Сохраняем в файл
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(llm_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Экспорт маркеров в формат LLM сохранен в {output_path}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при экспорте маркеров в формат LLM: {e}")
            return False

    def export_for_rag_search(self, output_path: str) -> bool:
        """Экспортирует маркеры с метаданными для RAG-поиска.

        Args:
            output_path: Путь к файлу для сохранения экспорта

        Returns:
            bool: True если экспорт успешен, False в случае ошибки

        """
        try:
            # Формат для RAG-поиска с расширенными метаданными
            rag_data = {
                "documents": [],
                "index_metadata": {
                    "export_timestamp": str(Path(__file__).stat().st_mtime),
                    "document_count": 0,
                    "tags_index": {},
                    "skills_index": {},
                },
            }

            # Создаем отдельные документы для каждого маркера
            for skill_name, skill_data in self.tracker.markers.items():
                for level_name, level_markers in skill_data.levels.items():
                    for marker in level_markers:
                        # Создаем документ для RAG
                        document = {
                            "id": f"{marker.id}",
                            "content": self._create_rag_content(marker, skill_name, level_name),
                            "metadata": {
                                "marker_id": marker.id,
                                "skill": skill_name,
                                "level": level_name,
                                "priority": marker.priority,
                                "tags": self._generate_tags(marker, skill_name, level_name),
                                "estimated_time": marker.smart_criteria.get("time_bound", ""),
                                "complexity": self._estimate_complexity(marker),
                                "author": marker.methodology_author,
                                "license": marker.methodology_license,
                            },
                        }

                        rag_data["documents"].append(document)

            # Создаем индексы для быстрого поиска
            rag_data["index_metadata"]["document_count"] = len(rag_data["documents"])
            rag_data["index_metadata"]["tags_index"] = self._create_tags_index(rag_data["documents"])
            rag_data["index_metadata"]["skills_index"] = self._create_skills_index(rag_data["documents"])

            # Сохраняем в файл
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(rag_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Экспорт маркеров для RAG-поиска сохранен в {output_path}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при экспорте маркеров для RAG-поиска: {e}")
            return False

    def _generate_tags(self, marker: Marker, skill_name: str, level_name: str) -> list[str]:
        """Генерирует теги для маркера."""
        tags = [
            f"skill:{skill_name.lower()}",
            f"level:{level_name.lower()}",
            f"priority:{marker.priority.lower()}",
            f"author:{marker.methodology_author.lower().replace(' ', '_')}",
        ]

        # Добавляем теги на основе ресурсов
        for resource in marker.resources:
            if "python" in resource.lower():
                tags.append("language:python")
            elif "docker" in resource.lower():
                tags.append("technology:docker")
            elif "git" in resource.lower():
                tags.append("tool:git")

        # Добавляем теги на основе SMART критериев
        if marker.smart_criteria.get("measurable"):
            tags.append("measurable")
        if marker.smart_criteria.get("time_bound"):
            tags.append("time_bound")

        return list(set(tags))  # Убираем дубликаты

    def _estimate_complexity(self, marker: Marker) -> str:
        """Оценивает сложность маркера."""
        # Простая эвристика на основе количества ресурсов и длины описания
        resource_count = len(marker.resources)
        description_length = len(marker.marker)

        if resource_count > 5 or description_length > 200:
            return "high"
        if resource_count > 2 or description_length > 100:
            return "medium"
        return "low"

    def _create_rag_content(self, marker: Marker, skill_name: str, level_name: str) -> str:
        """Создает контент документа для RAG-поиска."""
        content = f"""
# Компетенция: {skill_name} - Уровень {level_name}

## Описание
{marker.marker}

## Критерии валидации
{marker.validation}

## Ресурсы для изучения
""" + "\n".join([f"- {resource}" for resource in marker.resources]) + """

## SMART критерии
""" + "\n".join([f"- {key}: {value}" for key, value in marker.smart_criteria.items()]) + f"""

## Метаданные
- ID маркера: {marker.id}
- Приоритет: {marker.priority}
- Автор методологии: {marker.methodology_author}
- Лицензия: {marker.methodology_license}
"""
        return content.strip()

    def _create_tags_index(self, documents: list[dict]) -> dict[str, list[str]]:
        """Создает индекс тегов."""
        tags_index = {}
        for doc in documents:
            for tag in doc["metadata"]["tags"]:
                if tag not in tags_index:
                    tags_index[tag] = []
                tags_index[tag].append(doc["id"])
        return tags_index

    def _create_skills_index(self, documents: list[dict]) -> dict[str, list[str]]:
        """Создает индекс навыков."""
        skills_index = {}
        for doc in documents:
            skill = doc["metadata"]["skill"]
            if skill not in skills_index:
                skills_index[skill] = []
            skills_index[skill].append(doc["id"])
        return skills_index


def main():
    """Основная функция для демонстрации экспорта."""
    # Создаем трекер
    tracker = CareerTracker()

    # Создаем экспортер
    exporter = MarkerExporter(tracker)

    # Экспортируем в формат LLM
    exporter.export_to_llm_format("exports/llm_markers.json")

    # Экспортируем для RAG-поиска
    exporter.export_for_rag_search("exports/rag_markers.json")


if __name__ == "__main__":
    main()

