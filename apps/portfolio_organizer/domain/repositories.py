from uuid import UUID

from apps.portfolio_organizer.domain.entities import Portfolio, Project


class PortfolioRepository:
    async def save(self, portfolio: Portfolio) -> Portfolio:
        return portfolio

    async def get(self, portfolio_id: UUID) -> Portfolio | None:
        return None


class ProjectRepository:
    async def save(self, project: Project) -> Project:
        return project

    async def get_all(self, portfolio_id: UUID) -> list[Project]:
        return []
