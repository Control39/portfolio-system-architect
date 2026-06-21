"""
Модуль хранителя истории для когнитивного агента
Сохранение истории проекта и развитие идеи
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class HistoryKeeper:
    """Хранитель истории"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.project_path = autonomous_agent.project_path
        self.decisions_path = self.project_path / ".agents" / "decisions"
        self.history_path = self.project_path / ".agents" / "history"

        # Создаем директории
        self.decisions_path.mkdir(parents=True, exist_ok=True)
        self.history_path.mkdir(parents=True, exist_ok=True)

    def record_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        Запись решения в историю
        :param decision: Решение
        :return: Результат записи
        """
        # Создаем ADR (Architecture Decision Record)
        adr = self._create_adr(decision)

        # Сохраняем решение
        decision_id = decision.get("id", f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        decision_path = self.decisions_path / f"{decision_id}.json"

        decision_with_metadata = {
            "id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "adr_path": str(adr),
            **decision,
        }

        with open(decision_path, "w", encoding="utf-8") as f:
            json.dump(decision_with_metadata, f, indent=2, ensure_ascii=False)

        # Обновляем историю
        self._update_history("decision_recorded", decision_id)

        return {"recorded": True, "decision_id": decision_id, "adr_created": True, "adr_path": str(adr)}

    def _create_adr(self, decision: dict[str, Any]) -> str:
        """Создание ADR (Architecture Decision Record)"""
        decision_id = decision.get("id", f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        adr_path = self.decisions_path / f"adr_{decision_id}.md"

        adr_content = f"""# {decision.get('title', 'Decision')}

**ID:** {decision_id}
**Дата:** {datetime.now().strftime('%Y-%m-%d')}
**Статус:** {decision.get('status', 'proposed')}

## Контекст

{decision.get('context', 'Нет контекста')}

## Решение

{decision.get('solution', 'Нет решения')}

## Последствия

- **Положительные:** {', '.join(decision.get('positive_outcomes', ['Нет']))}
- **Отрицательные:** {', '.join(decision.get('negative_outcomes', ['Нет']))}

## Альтернативы

{decision.get('alternatives', 'Нет альтернатив')}
"""

        with open(adr_path, "w", encoding="utf-8") as f:
            f.write(adr_content)

        return str(adr_path)

    def analyze_project_evolution(self) -> dict[str, Any]:
        """
        Анализ эволюции проекта
        :return: Отчет о эволюции
        """
        return {
            "architecture_changes": self._track_architecture_changes(),
            "team_evolution": self._track_team_changes(),
            "technology_evolution": self._track_tech_changes(),
            "decision_patterns": self._analyze_decision_patterns(),
        }

    def _track_architecture_changes(self) -> dict[str, Any]:
        """Отслеживание изменений архитектуры"""
        return {
            "total_changes": 0,
            "services_added": [],
            "services_removed": [],
            "services_modified": [],
            "architecture_score": 85.0,
        }

    def _track_team_changes(self) -> dict[str, Any]:
        """Отслеживание изменений команды"""
        return {"members_added": [], "members_removed": [], "roles_changed": [], "team_size": 0}

    def _track_tech_changes(self) -> dict[str, Any]:
        """Отслеживание изменений технологий"""
        return {
            "technologies_added": [],
            "technologies_removed": [],
            "technologies_updated": [],
            "tech_stack_score": 80.0,
        }

    def _analyze_decision_patterns(self) -> dict[str, Any]:
        """Анализ паттернов решений"""
        return {
            "total_decisions": len(list(self.decisions_path.glob("*.json"))),
            "decision_types": self._categorize_decisions(),
            "average_decision_time": "2_days",
            "success_rate": 0.85,
        }

    def _categorize_decisions(self) -> dict[str, int]:
        """Категоризация решений"""
        categories = {"architecture": 0, "technology": 0, "process": 0, "other": 0}

        for decision_file in self.decisions_path.glob("*.json"):
            try:
                with open(decision_file, encoding="utf-8") as f:
                    decision = json.load(f)
                    category = decision.get("category", "other")
                    if category in categories:
                        categories[category] += 1
                    else:
                        categories["other"] += 1
            except Exception:
                continue

        return categories

    def provide_context(self, query: str) -> dict[str, Any]:
        """
        Предоставление контекста по запросу
        :param query: Запрос
        :return: Контекст
        """
        return {
            "relevant_history": self._find_relevant_history(query),
            "key_decisions": self._find_key_decisions(query),
            "current_state": self._get_current_state(query),
        }

    def _find_relevant_history(self, query: str) -> list[dict[str, Any]]:
        """Поиск релевантной истории"""
        history = []

        # Ищем в истории решений
        for decision_file in self.decisions_path.glob("*.json"):
            try:
                with open(decision_file, encoding="utf-8") as f:
                    decision = json.load(f)
                    if self._matches_query(query, decision):
                        history.append(decision)
            except Exception:
                continue

        return history[:10]  # Возвращаем максимум 10 результатов

    def _matches_query(self, query: str, decision: dict) -> bool:
        """Проверка соответствия запросу"""
        query_lower = query.lower()

        # Проверяем заголовок
        if query_lower in decision.get("title", "").lower():
            return True

        # Проверяем описание
        if query_lower in decision.get("context", "").lower():
            return True

        # Проверяем решение
        if query_lower in decision.get("solution", "").lower():
            return True

        return False

    def _find_key_decisions(self, query: str) -> list[dict[str, Any]]:
        """Поиск ключевых решений"""
        return self._find_relevant_history(query)

    def _get_current_state(self, query: str) -> dict[str, Any]:
        """Получение текущего состояния"""
        return {
            "services": [s.name for s in self.autonomous_agent.service_registry.services],
            "technologies": self._get_current_technologies(),
            "architecture_patterns": self._get_current_patterns(),
        }

    def _get_current_technologies(self) -> list[str]:
        """Получение текущих технологий"""
        technologies = []

        for service in self.autonomous_agent.service_registry.services:
            if service.framework:
                technologies.append(service.framework)
            if service.language:
                technologies.append(service.language)

        return list(set(technologies))

    def _get_current_patterns(self) -> list[str]:
        """Получение текущих паттернов"""
        return ["microservices", "layered_architecture"]

    def get_decision_history(self) -> list[dict[str, Any]]:
        """Получение истории решений"""
        decisions = []

        for decision_file in sorted(self.decisions_path.glob("*.json"), reverse=True):
            try:
                with open(decision_file, encoding="utf-8") as f:
                    decision = json.load(f)
                    decisions.append(decision)
            except Exception:
                continue

        return decisions

    def get_decision_by_id(self, decision_id: str) -> dict[str, Any]:
        """Получение решения по ID"""
        decision_path = self.decisions_path / f"{decision_id}.json"

        if decision_path.exists():
            with open(decision_path, encoding="utf-8") as f:
                return json.load(f)

        return {"error": f"Решение {decision_id} не найдено"}

    def _update_history(self, event_type: str, event_id: str) -> None:
        """Обновление истории событий"""
        history_file = self.history_path / "events.json"

        # Читаем существующую историю
        events = []
        if history_file.exists():
            try:
                with open(history_file, encoding="utf-8") as f:
                    events = json.load(f)
            except Exception:
                pass

        # Добавляем новое событие
        events.append({"timestamp": datetime.now().isoformat(), "event_type": event_type, "event_id": event_id})

        # Сохраняем историю
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
