from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from apps.portfolio_organizer.domain.entities import Portfolio, Project

# from apps.portfolio_organizer.src.core.ITCompassAPI import ITCompassAPI  # ← пока заглушка


class PortfolioService:
    async def create_portfolio(self, owner_id: UUID, name: str, compass_markers: list[str]) -> Portfolio:
        """
        СОЗДАТЬ НОВОЕ ПОРТФОЛИО

        Бизнес-правила:
        - owner_id должен быть валидным UUID
        - compass_markers должны существовать в IT-Compass
        - name не может быть пустым
        """
        if not name or not name.strip():
            raise ValueError("Название портфолио не может быть пустым")

        now = datetime.utcnow()
        return Portfolio(
            id=uuid4(),  # Генерируем корректный UUID v4
            owner_id=owner_id,
            name=name,
            compass_markers=compass_markers,
            created_at=now,
            updated_at=now,
        )

    async def get_portfolio(self, portfolio_id: UUID) -> Portfolio | None:
        return None

    async def get_projects(self, portfolio_id: UUID) -> list[Project]:
        return []

    async def add_project(self, portfolio_id: UUID, project: Project) -> Project:
        now = datetime.utcnow()
        project.created_at = now
        project.updated_at = now
        return project

    async def analyze_portfolio(self, portfolio_id: UUID) -> dict[str, Any]:
        projects = await self.get_projects(portfolio_id)
        all_demonstrated = []
        for p in projects:
            all_demonstrated.extend(p.demonstrated_markers)

        # all_markers = self.it_compass.list_markers()
        return {
            "portfolio_id": portfolio_id,
            "total_projects": len(projects),
            "covered_markers": list(set(all_demonstrated)),
            "gap_markers": [],
            "recommendations": ["Добавьте больше доказательств"],
        }
