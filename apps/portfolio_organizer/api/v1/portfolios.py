"""
Portfolio API endpoints.

RESTful endpoints for portfolio management with Pydantic v2 validation.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


# --- Pydantic Models (v2) ---
class PortfolioCreate(BaseModel):
    """Model for creating a new portfolio."""

    name: str
    description: Optional[str] = None


class PortfolioResponse(BaseModel):
    """Model for portfolio response."""

    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    owner_id: int

    model_config = {"from_attributes": True}


class Config:
    """Pydantic configuration."""

    from_attributes = True


# --- Mock Data (заменить на реальную БД позже) ---
fake_portfolios = [
    {
        "id": 1,
        "name": "My First Project",
        "description": "Test portfolio",
        "created_at": datetime.now(),
        "owner_id": 1,
    }
]


# --- Endpoints ---
@router.post("/", response_model=PortfolioResponse, status_code=201)
async def create_portfolio(portfolio: PortfolioCreate):
    """
    Create a new portfolio.

    - **name**: Portfolio name (required)
    - **description**: Optional description
    """
    new_id = len(fake_portfolios) + 1
    new_portfolio = {
        "id": new_id,
        **portfolio.model_dump(),  # Pydantic v2
        "created_at": datetime.now(),
        "owner_id": 1,  # Заглушка, потом брать из токена
    }
    fake_portfolios.append(new_portfolio)
    return new_portfolio


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: int):
    """
    Get portfolio by ID.

    - **portfolio_id**: Portfolio identifier
    """
    for p in fake_portfolios:
        if p["id"] == portfolio_id:
            return p
    raise HTTPException(status_code=404, detail="Portfolio not found")


@router.get("/", response_model=List[PortfolioResponse])
async def list_portfolios():
    """
    List all portfolios.

    Returns all available portfolios in the system.
    """
    return fake_portfolios
