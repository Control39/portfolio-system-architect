import logging
import yaml
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from pathlib import Path

from src.api.routes import router
from src.utils.telemetry import setup_logging, setup_tracing

CONFIG_PATH = Path(__file__).parent.parent / "config" / "gap_engine.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    setup_tracing("competency_gap_engine")
    app.state.config = load_config()
    logging.info("✅ Competency Gap Engine started")
    yield
    logging.info("🛑 Competency Gap Engine stopped")


app = FastAPI(
    title="Competency Gap Engine",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

# Прометей-метрики
Instrumentator(
    should_group_status_codes=False,
    should_instrument_requests_inprogress=True,
).instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "competency_gap_engine",
        "version": app.state.config["service"]["version"],
    }
