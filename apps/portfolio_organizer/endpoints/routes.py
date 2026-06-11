from datetime import datetime
from uuid import UUID, uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from apps.portfolio_organizer.domain.entities import Project
from apps.portfolio_organizer.domain.use_cases import PortfolioService

app = FastAPI(title="Portfolio Organizer API", version="1.0.0")
service = PortfolioService()


class PortfolioCreate(BaseModel):
    owner_id: str
    name: str
    compass_markers: list[str]


class ProjectCreate(BaseModel):
    portfolio_id: str
    name: str
    description: str
    evidence_links: list[str]
    test_coverage: float | None = None
    security_score: float | None = None
    demonstrated_markers: list[str]


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "portfolio_organizer"}


@app.post("/portfolio")
async def create_portfolio(payload: PortfolioCreate):
    portfolio = await service.create_portfolio(
        owner_id=UUID(payload.owner_id),
        name=payload.name,
        compass_markers=payload.compass_markers,
    )
    return {"id": str(portfolio.id), "name": portfolio.name}


@app.post("/project")
async def add_project(payload: ProjectCreate):
    now = datetime.utcnow()
    project = Project(
        id=uuid4(),
        portfolio_id=UUID(payload.portfolio_id),
        name=payload.name,
        description=payload.description,
        evidence_links=payload.evidence_links,
        test_coverage=payload.test_coverage,
        security_score=payload.security_score,
        demonstrated_markers=payload.demonstrated_markers,
        created_at=now,
        updated_at=now,
    )
    saved_project = await service.add_project(
        portfolio_id=UUID(payload.portfolio_id),
        project=project,
    )
    return {"id": str(saved_project.id), "name": saved_project.name}
