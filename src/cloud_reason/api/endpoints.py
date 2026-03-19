# components/cloud-reason/api/endpoints.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Cloud Reason API")

class ReasonRequest(BaseModel):
    repo: str
    query: str = ""

@app.get("/")
async def health():
    return {"status": "healthy", "service": "cloud-reason"}

@app.post("/reason")
async def reason(request: ReasonRequest):
    # Stub reasoning logic
    return {"reasoning": f"Analyzed {request.repo}: {request.query}", "confidence": 0.95}
