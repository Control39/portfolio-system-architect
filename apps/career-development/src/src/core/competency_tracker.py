from typing import List
from .models import UserProfile, CompetencyMarker


class CompetencyTracker:
    """Бизнес‑логика для работы с маркерами."""

    def __init__(self, profile: UserProfile):
        self.profile = profile

    # -----------------------------------------------------------------
    def update_marker(self, marker_id: str, new_status: str) -> bool:
        """
        Обновить статус маркера.
        Возвращает True, если маркер найден и обновлён.
        """
        for skill in self.profile.skills:
            for marker in skill.markers:
                if marker.id == marker_id:
                    marker.status = new_status
                    return True
        return False

    # -----------------------------------------------------------------
    def calculate_progress(self) -> float:
        """
        Рассчитать процент завершения всех маркеров.
        """
        total = 0
        completed = 0
        for skill in self.profile.skills:
            total += len(skill.markers)
            completed += sum(m.status == "completed" for m in skill.markers)

        return (completed / total * 100) if total else 0.0

    # -----------------------------------------------------------------
    def list_pending_markers(self) -> List[CompetencyMarker]:
        """Вернуть список всех маркеров, которые ещё не завершены."""
        pending = []
        for skill in self.profile.skills:
            pending.extend([m for m in skill.markers if m.status != "completed"])
        return pending


