"""Portfolio Organizer API endpoints."""

from fastapi import FastAPI

app = FastAPI(title="Portfolio Organizer API", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "portfolio_organizer"}
