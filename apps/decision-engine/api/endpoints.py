# components/decision-engine/api/endpoints.py
from fastapi import FastAPI

app = FastAPI(title="Decision Engine API")

@app.get("/api/v1/status")
async def status():
    """Health check endpoint for Docker healthcheck"""
    return {"status": "healthy", "service": "decision-engine"}

@app.get("/health")
async def health():
    """Alternative health endpoint"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Decision Engine API", "version": "1.0.0"}


