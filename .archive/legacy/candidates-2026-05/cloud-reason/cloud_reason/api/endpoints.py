# components/cloud-reason/api/endpoints.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Cloud-Reason API")

@app.get("/api/v1/status")
async def status():
    """Health check endpoint for Docker healthcheck"""
    return {"status": "healthy", "service": "cloud-reason"}

@app.get("/health")
async def health():
    """Alternative health endpoint"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Cloud-Reason API", "version": "1.0.0"}
