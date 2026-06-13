"""
JWT Auth Service
Исполняет и валидирует JWT tokens для API Gateway
"""

import logging
import os
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:

# Интеграция с AI Config Manager
try:
    from apps.auth_service.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    auth_config = config_manager.get_config() or {}
    logger = logging.getLogger(__name__)
    logger.info("✅ Auth Service: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Auth Service: AI Config Manager недоступен ({e}), используется локальный конфиг")
    auth_config = {}


import jwt
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from src.common.health_check import init_health_checks

# --- OpenTelemetry Tracing ---
try:
    from config.otel import OTEL_ENABLED
except ImportError:
    OTEL_ENABLED = False

# --- Prometheus Metrics ---
try:
    from prometheus_fastapi_instrumentator import Instrumentator

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

# JWT конфигурация с валидацией
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET and auth_config:
    JWT_SECRET = auth_config.get("jwt", {}).get("secret")

if not JWT_SECRET:
    raise ValueError(
        "JWT_SECRET environment variable is required for production. "
        "Set it via environment variable or secrets manager."
    )

# Валидация длины секрета для HS256 (минимум 32 символа)
if len(JWT_SECRET) < 32:
    raise ValueError(f"JWT_SECRET must be at least 32 characters for HS256. Current length: {len(JWT_SECRET)}")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
if auth_config:
    JWT_EXPIRATION_HOURS = int(auth_config.get("jwt", {}).get("expiry_hours", JWT_EXPIRATION_HOURS))

# Безопасные константы (не хардкодить в коде!)
BLOCKED_USERNAME = os.getenv("BLOCKED_USERNAME", "demo")
BLOCKED_PASSWORD = os.getenv("BLOCKED_PASSWORD", "demo")

# Rate limiting (простая реализация)
LOGIN_ATTEMPTS = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 минут

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="JWT Authentication Service for API Gateway",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
if PROMETHEUS_AVAILABLE:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

security = HTTPBearer()

# OpenTelemetry instrumentation
if OTEL_ENABLED:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("✅ OpenTelemetry FastAPI Instrumentation активировано")
    except Exception as e:
        logger.warning(f"⚠️ OpenTelemetry не настроен: {e}")

# ============================================================================
# МОДЕЛИ ДАННЫХ
# ============================================================================


class TokenRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class User(BaseModel):
    username: str
    role: str = "user"


class VerifyResponse(BaseModel):
    valid: bool
    username: str | None = None
    role: str | None = None


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================


def check_rate_limit(username: str) -> bool:
    """Проверяет rate limit для пользователя"""
    current_time = time.time()

    if username not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[username] = {"attempts": 0, "last_attempt": 0, "locked_until": 0}

    user_data = LOGIN_ATTEMPTS[username]

    # Проверка блокировки
    if user_data["locked_until"] > current_time:
        return False

    # Сброс счетчика после истечения времени
    if current_time - user_data["last_attempt"] > LOCKOUT_TIME:
        user_data["attempts"] = 0

    return user_data["attempts"] < MAX_ATTEMPTS


def record_failed_attempt(username: str):
    """Записывает неудачную попытку входа"""
    current_time = time.time()

    if username not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[username] = {"attempts": 0, "last_attempt": 0, "locked_until": 0}

    user_data = LOGIN_ATTEMPTS[username]
    user_data["attempts"] += 1
    user_data["last_attempt"] = current_time

    # Блокировка при превышении лимита
    if user_data["attempts"] >= MAX_ATTEMPTS:
        user_data["locked_until"] = current_time + LOCKOUT_TIME
        logger.warning(f"🚫 Account locked due to too many failed attempts: {username}")


def reset_attempts(username: str):
    """Сбрасывает счетчик попыток после успешного входа"""
    if username in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[username] = {"attempts": 0, "last_attempt": 0, "locked_until": 0}


# ============================================================================
# JWT ФУНКЦИИ
# ============================================================================


def create_token(username: str, role: str = "user") -> dict:
    """Create JWT token"""
    payload = {
        "sub": username,  # Standard JWT claim
        "username": username,
        "role": role,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iss": "auth-service",
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    logger.info(f"✅ Token issued for user: {username}, role: {role}")

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_HOURS * 3600,
    }


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_aud": False}
        )

        # Валидация обязательных полей
        if "username" not in payload or "role" not in payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        return payload

    except jwt.ExpiredSignatureError as err:
        logger.warning("⚠️ Token expired for credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from err
    except jwt.InvalidTokenError as err:
        logger.warning(f"⚠️ Invalid token: {err}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from err


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.post("/auth/token", response_model=TokenResponse)
async def login(request: TokenRequest):
    """
    Issue JWT token

    For demo purposes, any username/password combination is accepted except demo/demo.
    In production, implement real authentication against a user database.
    """
    # Rate limiting
    if not check_rate_limit(request.username):
        logger.warning(f"🚫 Rate limit exceeded for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts. Please try again later."
        )

    # Block demo credentials for security
    if request.username == BLOCKED_USERNAME and request.password == BLOCKED_PASSWORD:
        logger.warning(f"⚠️ Blocked credentials attempt: {request.username}")
        record_failed_attempt(request.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Demo credentials not allowed")

    # In production, replace with real auth (e.g., database lookup, LDAP, OAuth)
    if request.username and request.password:
        # For demo: assign admin role to 'admin' username, user role to others
        role = "admin" if request.username == "admin" else "user"

        # Успешный вход
        reset_attempts(request.username)
        logger.info(f"✅ Successful login: {request.username}")

        return create_token(request.username, role=role)

    # Неудачный вход
    record_failed_attempt(request.username)
    logger.warning(f"❌ Failed login attempt: {request.username}")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@app.post("/auth/verify", response_model=VerifyResponse)
async def verify(payload: dict = Depends(verify_token)):
    """Verify token validity"""
    return VerifyResponse(
        valid=True,
        username=payload.get("username"),
        role=payload.get("role"),
    )


# Инициализируем health-check эндпоинты
init_health_checks(app, service_name="auth-service", version="1.0.0")


@app.get("/")
async def root():
    """Service info"""
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "POST /auth/token": "Issue JWT token",
            "POST /auth/verify": "Verify token",
            "GET /health": "Health check",
            "GET /ready": "Readiness probe",
            "GET /live": "Liveness probe",
            "GET /metrics": "Prometheus metrics",
        },
        "security": {
            "rate_limiting": "enabled",
            "max_attempts": MAX_ATTEMPTS,
            "lockout_time": f"{LOCKOUT_TIME}s",
        },
    }


# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("AUTH_SERVICE_PORT", "8100"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level=log_level,
        access_log=True,
    )
