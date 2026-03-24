from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="ML Model Registry API")

# Instrument for Prometheus metrics
Instrumentator().instrument(app).expose(app)

@app.get("/health")
async def health():
    """Health check endpoint for Docker healthcheck"""
    return {"status": "healthy", "service": "ml-model-registry"}

@app.get("/")
async def root():
    return {"message": "ML Model Registry API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)