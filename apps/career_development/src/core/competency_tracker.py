from typing import Any, cast

from .models import CompetencyMarker, UserProfile


class CompetencyTracker:
    """Бизнес‑логика для работы с маркерами."""

    def __init__(self, profile: UserProfile):
        self.profile = profile
        self.users: dict[str, dict[str, Any]] = {}
        self.competency_markers: dict[str, dict[str, Any]] = {}

    # -----------------------------------------------------------------
    def add_user(self, user_id: str, username: str, email: str) -> None:
        """Добавить пользователя в трекер."""
        self.users[user_id] = {
            "username": username,
            "email": email,
            "skills": {},
            "progress_history": [],
        }

    # -----------------------------------------------------------------
    def add_skill(self, user_id: str, skill_name: str, level: int) -> None:
        """Добавить навык пользователю."""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        self.users[user_id]["skills"][skill_name] = level
        self.users[user_id]["progress_history"].append({"skill": skill_name, "level": level, "action": "add"})

    # -----------------------------------------------------------------
    def update_skill_level(self, user_id: str, skill_name: str, new_level: int) -> None:
        """Обновить уровень навыка пользователя."""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        if skill_name not in self.users[user_id]["skills"]:
            raise ValueError(f"Skill {skill_name} not found for user {user_id}")
        self.users[user_id]["skills"][skill_name] = new_level
        self.users[user_id]["progress_history"].append({"skill": skill_name, "level": new_level, "action": "update"})

    # -----------------------------------------------------------------
    def add_competency_marker(self, marker_id: str, title: str, description: str, required_level: int) -> None:
        """Добавить маркер компетенции."""
        self.competency_markers[marker_id] = {
            "id": marker_id,
            "title": title,
            "description": description,
            "required_level": required_level,
            "status": "pending",
        }

    # -----------------------------------------------------------------
    def get_user_progress(self, user_id: str) -> dict[str, Any]:
        """Получить прогресс пользователя."""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        user = self.users[user_id]
        total_skills = len(user["skills"])
        completed = sum(1 for level in user["skills"].values() if level >= 4)
        return {
            "user_id": user_id,
            "total_skills": total_skills,
            "completed_skills": completed,
            "progress_percentage": (completed / total_skills * 100) if total_skills else 0,
            "skills": user["skills"],
            "history": user["progress_history"],
        }

    # -----------------------------------------------------------------
    def check_competency_achievement(self, user_id: str) -> dict[str, Any]:
        """Проверить достижение компетенций пользователем."""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        user = self.users[user_id]
        achieved = []
        for marker_id, marker in self.competency_markers.items():
            max_skill_level = max(user["skills"].values()) if user["skills"] else 0
            if max_skill_level >= marker["required_level"]:
                achieved.append(marker_id)
        return {
            "user_id": user_id,
            "achieved_markers": achieved,
            "total_markers": len(self.competency_markers),
            "completion_rate": len(achieved) / len(self.competency_markers) * 100 if self.competency_markers else 0,
        }

    # -----------------------------------------------------------------
    def get_user_skills(self, user_id: str) -> dict[str, int]:
        """Получить список навыков пользователя."""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        return cast(dict[str, int], self.users[user_id]["skills"].copy())

    # -----------------------------------------------------------------
    def generate_progress_report(self, user_id: str) -> str:
        """Сгенерировать отчёт о прогрессе пользователя."""
        progress = self.get_user_progress(user_id)
        achievement = self.check_competency_achievement(user_id)
        report = f"Progress Report for {user_id}:\n"
        report += f"  Skills: {progress['total_skills']} total, {progress['completed_skills']} completed\n"
        report += f"  Progress: {progress['progress_percentage']:.1f}%\n"
        report += f"  Competencies: {achievement['completion_rate']:.1f}% achieved\n"
        return report

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
    def list_pending_markers(self) -> list[CompetencyMarker]:
        """Вернуть список всех маркеров, которые ещё не завершены."""
        pending = []
        for skill in self.profile.skills:
            pending.extend([m for m in skill.markers if m.status != "completed"])
        return pending
