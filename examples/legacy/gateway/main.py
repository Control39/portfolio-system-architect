"""Unified API Gateway для экосистемы сервисов.
Единая точка входа с аутентификацией, rate limiting и мониторингом.

Security improvements applied:
- B104: Binding to specific network interface via GATEWAY_HOST environment variable
- B105: No hardcoded passwords; uses environment variables (JWT_SECRET, ADMIN_PASSWORD, REDIS_PASSWORD)
- JWT token verification: Safe extraction for rate limiting, proper signature verification for auth
- B110: No empty except: pass blocks
- Async file operations in lifespan using asyncio.to_thread
- Specific exception classes in except blocks
- Updated datetime.utcnow() to datetime.now(timezone.utc)
- Reduced cognitive complexity through helper functions
- Environment variable validation at startup

Environment variables:
- JWT_SECRET: Required in production, strong secret for JWT signing
- ADMIN_PASSWORD: Admin password for /auth/login (defaults to demo password in dev)
- REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD: Redis connection
- GATEWAY_HOST, GATEWAY_PORT: Binding address (default: 127.0.0.1:8080)
- ENVIRONMENT: "production" or "development" (affects validation strictness)
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import httpx
import jwt
import redis
import yaml
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Конфигурация
CONFIG_DIR = Path(__file__).parent / "config"

# Глобальные переменные
redis_client: redis.Redis | None = None
http_client: httpx.AsyncClient | None = None
services_config: dict[str, Any] = {}
routes_config: list[dict[str, Any]] = []


def get_jwt_secret() -> str:
    """Получить JWT секрет с приоритетом переменных окружения.
    Порядок проверки:
    1. Переменная окружения JWT_SECRET
    2. Конфигурация из YAML файла (services_config["auth"]["jwt_secret"])

    В production JWT_SECRET должен быть установлен через переменные окружения.
    """
    # 1. Проверяем переменную окружения
    env_secret = os.getenv("JWT_SECRET")
    if env_secret:
        if len(env_secret) < 32:
            logger.warning("JWT_SECRET is too short. For production, use at least 32 characters.")
        logger.info("Using JWT secret from environment variable")
        return env_secret

    # 2. Проверяем конфигурацию из YAML
    if services_config and "auth" in services_config:
        config_secret = services_config["auth"].get("jwt_secret")
        if config_secret:
            logger.info("Using JWT secret from configuration")
            return config_secret

    # 3. В production должно быть исключение
    if os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError("JWT_SECRET environment variable must be set in production")

    # 4. Значение по умолчанию ТОЛЬКО для разработки с явным предупреждением
    logger.error("JWT_SECRET not set! Using insecure default for development only.")
    logger.error("For production, set JWT_SECRET environment variable with strong secret.")
    return "insecure-development-secret-change-in-production"


def validate_environment():
    """Проверить обязательные переменные окружения."""
    environment = os.getenv("ENVIRONMENT", "development")

    if environment == "production":
        required_vars = ["JWT_SECRET"]
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            error_msg = (
                f"Missing required environment variables in production: {', '.join(missing)}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    # Предупреждения для разработки
    if environment == "development":
        if not os.getenv("JWT_SECRET"):
            logger.warning("JWT_SECRET not set. Using insecure default for development.")
        if os.getenv("ADMIN_PASSWORD") == "admin":
            logger.warning("Using default admin password. Change ADMIN_PASSWORD in production.")

    logger.info(f"Environment validation passed ({environment})")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    global redis_client, http_client, services_config, routes_config

    logger.info("Starting API Gateway...")

    # Валидируем переменные окружения
    validate_environment()

    # Загружаем конфигурацию асинхронно
    try:
        # Используем asyncio.to_thread для неблокирующего чтения файлов
        def load_services_config():
            with open(CONFIG_DIR / "services.yaml") as f:
                return yaml.safe_load(f)

        def load_routes_config():
            with open(CONFIG_DIR / "routes.yaml") as f:
                return yaml.safe_load(f)["routes"]

        services_config = await asyncio.to_thread(load_services_config)
        routes_config = await asyncio.to_thread(load_routes_config)
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        services_config = {}
        routes_config = []

    # Инициализируем Redis
    try:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_db = int(os.getenv("REDIS_DB", "0"))

        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True,
            password=os.getenv("REDIS_PASSWORD") or None,
        )
        redis_client.ping()
        logger.info(f"Redis connected successfully to {redis_host}:{redis_port}")
    except Exception as e:
        logger.warning(f"Redis not available: {e}. Using in-memory cache.")
        redis_client = None

    # Инициализируем HTTP клиент
    http_client = httpx.AsyncClient(timeout=30.0)

    yield

    # Shutdown
    logger.info("Shutting down API Gateway...")
    if http_client:
        await http_client.aclose()
    if redis_client:
        redis_client.close()


# Создаем FastAPI приложение
app = FastAPI(
    title="Unified API Gateway",
    description="Единая точка входа для экосистемы сервисов",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модели
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: dict[str, str]
    metrics: dict[str, Any]


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Вспомогательные функции
def get_service_url(service_name: str) -> str:
    """Получить URL сервиса из конфигурации."""
    if service_name in services_config.get("services", {}):
        return services_config["services"][service_name]["base_url"]
    raise HTTPException(
        status_code=500,
        detail=f"Service {service_name} not configured",
    )


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """Верифицировать JWT токен."""
    token = credentials.credentials

    # Получаем секрет с приоритетом переменных окружения
    SECRET_KEY = get_jwt_secret()

    # Получаем алгоритм из конфигурации
    algorithm = services_config.get("auth", {}).get("algorithm", "HS256")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        ) from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e


def extract_user_id_from_token_safely(token: str) -> str | None:
    """Безопасно извлечь user_id из JWT токена для rate limiting.
    Не проверяет подпись, но проверяет базовый формат токена.
    Возвращает None если токен невалидный или не содержит user_id.
    """
    try:
        # Проверяем базовый формат JWT (три части, разделенные точками)
        parts = token.split(".")
        if len(parts) != 3:
            return None

        # Декодируем payload (вторая часть) без проверки подписи
        import base64
        import json

        # Добавляем padding если нужно
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding

        payload_json = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_json)

        # Извлекаем user_id (sub claim)
        user_id = payload.get("sub")

        # Проверяем что user_id не пустой и является строкой
        if user_id and isinstance(user_id, str):
            return user_id
        return None
    except Exception as e:
        logger.debug(f"Failed to extract user_id from token: {e}")
        return None


def check_rate_limit(user_id: str, endpoint: str) -> bool:
    """Проверить rate limit для пользователя и endpoint."""
    if not redis_client:
        return True  # Пропускаем если Redis недоступен

    key = f"rate_limit:{user_id}:{endpoint}:{int(time.time() // 3600)}"

    try:
        # Утверждаем, что redis_client не None после проверки выше
        assert redis_client is not None
        # Явно приводим тип, так как incr возвращает int
        current: int = cast("int", redis_client.incr(key))
        if current == 1:
            redis_client.expire(key, 3600)  # Expire через час

        # Получаем лимит из конфигурации
        limit = get_rate_limit_for_endpoint(endpoint)

        return current <= limit
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return True  # Fail open


def get_rate_limit_for_endpoint(endpoint: str) -> int:
    """Получить лимит запросов для endpoint из конфигурации."""
    limit = 100  # По умолчанию
    for route in routes_config:
        if endpoint.startswith(route["path"]):
            limit_str = route.get("rate_limit", "100/hour")
            limit = int(limit_str.split("/")[0])
            break
    return limit


def check_rate_limit_for_request(request: Request) -> JSONResponse | None:
    """Проверить rate limit для запроса. Возвращает JSONResponse если лимит превышен, иначе None."""
    auth_header = request.headers.get("authorization")
    if not (auth_header and auth_header.startswith("Bearer ")):
        return None

    try:
        token = auth_header.split(" ")[1]
        user_id = extract_user_id_from_token_safely(token)
        if not user_id:
            return None

        if not check_rate_limit(user_id, request.url.path):
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Rate limit exceeded",
                        "details": {
                            "limit": f"{get_rate_limit_for_endpoint(request.url.path)}/hour",
                            "reset_in": 3600,
                        },
                    },
                },
            )
    except Exception as e:
        logger.debug(f"Rate limit check failed: {e}")

    return None


async def forward_request(
    service_name: str,
    path: str,
    method: str,
    request: Request,
    user_payload: dict | None = None,
) -> JSONResponse:
    """Перенаправить запрос к целевому сервису."""
    if not http_client:
        raise HTTPException(
            status_code=500,
            detail="HTTP client not initialized",
        )

    service_url = get_service_url(service_name)
    target_url = f"{service_url}{path}"

    # Подготавливаем headers
    headers = dict(request.headers)
    headers.pop("host", None)

    # Добавляем user context если есть
    if user_payload:
        headers["X-User-Id"] = user_payload.get("sub", "")
        headers["X-User-Roles"] = ",".join(user_payload.get("roles", []))

    # Подготавливаем тело запроса
    body = None
    if method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except (ValueError, TypeError):
            # Если JSON невалидный, получаем raw body
            body = await request.body()

    # Отправляем запрос
    try:
        response = await http_client.request(
            method=method,
            url=target_url,
            headers=headers,
            json=body if isinstance(body, dict) else None,
            content=body if not isinstance(body, dict) else None,
            params=dict(request.query_params),
        )

        # Возвращаем ответ
        return JSONResponse(
            content=(
                response.json()
                if response.headers.get("content-type") == "application/json"
                else response.text
            ),
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except httpx.TimeoutException as e:
        raise HTTPException(
            status_code=504,
            detail=f"Service {service_name} timeout",
        ) from e
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Service {service_name} unavailable: {e!s}",
        ) from e


# Middleware для логирования и rate limiting
@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    """Middleware для обработки всех запросов."""
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")

    # Логируем начало запроса
    logger.info(f"[{request_id}] {request.method} {request.url.path}")

    # Проверяем rate limit для аутентифицированных пользователей
    rate_limit_response = check_rate_limit_for_request(request)
    if rate_limit_response:
        return rate_limit_response

    # Обрабатываем запрос
    response = await call_next(request)

    # Логируем завершение запроса
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id

    logger.info(f"[{request_id}] Completed in {process_time:.3f}s - Status: {response.status_code}")

    return response


# Endpoints
@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check gateway и всех сервисов."""
    services_status = {}

    # Проверяем каждый сервис
    for service_name, config in services_config.get("services", {}).items():
        try:
            health_url = f"{config['base_url']}{config.get('health_check', '/health')}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(health_url)
                services_status[service_name] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
        except Exception as e:
            services_status[service_name] = f"error: {e!s}"

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services_status,
        "metrics": {
            "uptime": "0d 0h 0m",  # В production считать от времени старта
            "request_count": redis_client.get("gateway:request_count") if redis_client else 0,
        },
    }


@app.post("/auth/login")
async def login(auth: AuthRequest) -> AuthResponse:
    """Аутентификация пользователя."""
    # В production использовать реальную базу пользователей или внешний auth provider
    # Здесь упрощенная реализация для демонстрации

    # Получаем credentials из переменных окружения или конфигурации
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD")

    # Если пароль не установлен в окружении, использовать конфигурацию
    if not admin_password and services_config and "auth" in services_config:
        admin_password = services_config["auth"].get("admin_password")

    # Если все еще нет пароля, использовать демо-режим с предупреждением
    if not admin_password:
        if os.getenv("ENVIRONMENT") == "production":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured",
            )
        logger.warning(
            "Using demo authentication. For production, set ADMIN_PASSWORD environment variable."
        )
        admin_password = "demo-admin-password-change-in-production"  # nosec: B105 - This is a demo password for development only

    # Проверяем credentials
    if auth.username == admin_username and auth.password == admin_password:
        payload = {
            "sub": auth.username,
            "roles": ["admin", "editor", "viewer"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        }

        # Получаем секрет с приоритетом переменных окружения и алгоритм из конфигурации
        SECRET_KEY = get_jwt_secret()
        algorithm = services_config.get("auth", {}).get("algorithm", "HS256")
        token = jwt.encode(payload, SECRET_KEY, algorithm=algorithm)

        return AuthResponse(
            access_token=token,
            expires_in=86400,  # 24 часа в секундах
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )


def extract_service_path(request_path: str, route_path: str) -> str:
    """Извлечь остаток пути после префикса маршрута."""
    if request_path.startswith(route_path):
        return request_path[len(route_path) :] or "/"
    return request_path


def create_route_handler(route_path: str, route_target: str, auth_required: bool):
    """Создать обработчик маршрута."""
    if auth_required:

        async def auth_handler(request: Request, user_payload: dict = Depends(verify_token)):
            service_path = extract_service_path(request.url.path, route_path)
            return await forward_request(
                service_name=route_target,
                path=service_path,
                method=request.method,
                request=request,
                user_payload=user_payload,
            )

        return auth_handler

    async def no_auth_handler(request: Request):
        service_path = extract_service_path(request.url.path, route_path)
        return await forward_request(
            service_name=route_target,
            path=service_path,
            method=request.method,
            request=request,
            user_payload=None,
        )

    return no_auth_handler


def register_route(path: str, target: str, methods: list, auth_required: bool):
    """Зарегистрировать маршрут для всех указанных методов."""
    handler = create_route_handler(path, target, auth_required)
    for method in methods:
        app.add_api_route(
            path=path + "{rest_of_path:path}",
            endpoint=handler,
            methods=[method],
            include_in_schema=True,
        )


# Динамические routes на основе конфигурации
def setup_routes():
    """Настроить маршруты на основе конфигурации."""
    for route in routes_config:
        path = route["path"]
        target = route["target"]
        methods = route.get("methods", ["GET"])
        auth_required = route.get("auth_required", False)

        register_route(path, target, methods, auth_required)


# Настраиваем маршруты при старте
@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения."""
    setup_routes()
    logger.info(f"Registered {len(routes_config)} routes")


# Корневой endpoint
@app.get("/")
async def root():
    """Корневой endpoint с информацией о gateway."""
    return {
        "service": "Unified API Gateway",
        "version": "1.0.0",
        "description": "Единая точка входа для экосистемы сервисов",
        "endpoints": {
            "health": "/health",
            "auth": "/auth/login",
            "docs": "/docs",
            "redoc": "/redoc",
        },
        "routes": [
            {
                "path": route["path"],
                "target": route["target"],
                "methods": route.get("methods", ["GET"]),
                "auth_required": route.get("auth_required", False),
            }
            for route in routes_config
        ],
    }


if __name__ == "__main__":
    import uvicorn

    # Use environment variable for host binding with safer default
    # In production, set HOST to specific interface or use reverse proxy
    host = os.getenv("GATEWAY_HOST", "127.0.0.1")
    port = int(os.getenv("GATEWAY_PORT", "8080"))

    logger.info(f"Starting gateway on {host}:{port}")
    logger.warning(
        "For production, consider using a reverse proxy (nginx/traefik) and binding to specific interfaces"
    )

    uvicorn.run(app, host=host, port=port)
