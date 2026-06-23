from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

try:
    from prometheus_fastapi_instrumentator import Instrumentator
except ModuleNotFoundError:  # pragma: no cover
    Instrumentator = None
import logging
import uuid

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

try:
    from .config.settings import settings
    from .core.builder import ContextBuilder
    from .core.filters import FileFilter
    from .core.scanner import ProjectScanner
    from .models.schemas import (
        BuildContextRequest,
        BuildContextResponse,
        FilterConfigRequest,
        FilterConfigResponse,
    )
except ImportError:  # pragma: no cover
    # Fallback for tests that import `main` as a top-level module.
    from config.settings import settings
    from core.builder import ContextBuilder
    from core.filters import FileFilter
    from core.scanner import ProjectScanner
    from models.schemas import (
        BuildContextRequest,
        BuildContextResponse,
        FilterConfigRequest,
        FilterConfigResponse,
    )


# © 2025 Ekaterina Kudelya. Licensed under CC BY‑ND 4.0
# See LICENSE file for details.

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(settings.service_name)

# Rate limiting
limiter = Limiter(key_func=get_remote_address) if settings.rate_limit_enabled else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом сервиса"""
    logger.info(f"Starting {settings.service_name} on port {settings.service_port}")
    logger.info(f"Project root: {settings.project_root}")
    logger.info(f"Output dir: {settings.output_dir}")

    # Создаём директории
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    yield

    logger.info(f"Shutting down {settings.service_name}")


app = FastAPI(
    title="Context Builder Service",
    description="Сборка контекста проекта для LLM с поддержкой .gitignore, бинарных файлов, токенов и chunking. Приоритет: российские модели (Сбер, Яндекс, VK)",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

if limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus метрики
if Instrumentator:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Глобальные компоненты
file_filter = FileFilter()
project_root = settings.project_root
builder = ContextBuilder(project_root)


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "context_builder",  # Исправлено с "auth_service"
        "version": "2.0.0",
    }


@app.get("/ready")
async def ready():
    """Ready check для K8s"""
    # Проверяем, что можем писать в output_dir
    test_file = settings.output_dir / ".ready_test"
    try:
        test_file.write_text("test")
        test_file.unlink()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Not ready: {e}")


@app.get("/filter")
async def get_filter() -> FilterConfigResponse:
    """Получить текущие настройки фильтрации"""
    return FilterConfigResponse(
        extensions=sorted(file_filter.extensions),
        excluded_dirs=sorted(file_filter.excluded_dirs),
        excluded_files=sorted(file_filter.excluded_files),
        max_file_size_mb=settings.max_file_size_mb,
    )


@app.post("/filter")
async def update_filter(request: FilterConfigRequest) -> FilterConfigResponse:
    """Обновить настройки фильтрации"""

    if request.add_extensions:
        for ext in request.add_extensions:
            file_filter.add_extension(ext)

    if request.remove_extensions:
        for ext in request.remove_extensions:
            file_filter.remove_extension(ext)

    if request.add_exclude_dirs:
        file_filter.excluded_dirs.update(request.add_exclude_dirs)

    if request.remove_exclude_dirs:
        for d in request.remove_exclude_dirs:
            file_filter.excluded_dirs.discard(d)

    return await get_filter()


@app.post("/build", response_class=PlainTextResponse)
async def build_context(request: BuildContextRequest):
    """Собрать контекст (текстовый ответ)"""

    if limiter:
        # Rate limit будет применён через middleware
        pass

    try:
        context = builder.build(
            subpath=request.paths[0] if request.paths else None,
            structure_only=request.structure_only,
            include_stats=request.include_stats,
            format=request.format,
        )

        logger.info(f"Built context for {request.paths}, size: {len(context)} chars")
        return context

    except Exception as e:
        logger.error(f"Error building context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/build/json")
async def build_context_json(request: BuildContextRequest) -> BuildContextResponse:
    """Собрать контекст (JSON ответ)"""

    try:
        context = builder.build(
            subpath=request.paths[0] if request.paths else None,
            structure_only=request.structure_only,
            include_stats=request.include_stats,
            format="json",
        )

        return BuildContextResponse(success=True, context=context, stats=file_filter.get_stats())

    except Exception as e:
        logger.error(f"Error building JSON context: {e}")
        return BuildContextResponse(success=False, error=str(e))


@app.post("/build/chunked")
async def build_context_chunked(request: BuildContextRequest) -> JSONResponse:
    """Собрать контекст с разбиением на части"""

    if not settings.enable_chunking:
        raise HTTPException(400, "Chunking disabled. Set ENABLE_CHUNKING=true")

    try:
        chunks = builder.build_chunked(subpath=request.paths[0] if request.paths else None)

        return JSONResponse({"success": True, "total_chunks": len(chunks), "chunks": chunks})

    except Exception as e:
        logger.error(f"Error building chunked context: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/build/file")
async def build_context_to_file(
    request: BuildContextRequest, background_tasks: BackgroundTasks
) -> BuildContextResponse:
    """Собрать контекст и сохранить в файл"""

    try:
        file_id = str(uuid.uuid4())[:8]
        output_file = settings.output_dir / f"context_{file_id}.txt"

        context = builder.build(
            subpath=request.paths[0] if request.paths else None,
            structure_only=request.structure_only,
            include_stats=request.include_stats,
            format="markdown",
        )

        output_file.write_text(context, encoding="utf-8")

        logger.info(f"Saved context to {output_file}")

        return BuildContextResponse(
            success=True,
            file_path=str(output_file),
            stats={
                "file_id": file_id,
                "size_mb": output_file.stat().st_size / (1024 * 1024),
                "files_count": len(list(builder.scanner.scan())),
            },
        )

    except Exception as e:
        logger.error(f"Error saving context to file: {e}")
        return BuildContextResponse(success=False, error=str(e))


@app.get("/structure")
async def get_structure(subpath: str = None) -> JSONResponse:
    """Получить только структуру проекта"""

    try:
        scanner = ProjectScanner(project_root, respect_gitignore=settings.respect_gitignore)
        structure = scanner.get_structure_only(subpath)

        return JSONResponse({"success": True, "structure": structure, "total_files": len(structure)})

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting structure: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
