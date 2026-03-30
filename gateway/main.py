"""
Unified API Gateway для экосистемы сервисов.
Единая точка входа с аутентификацией, rate limiting и мониторингом.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import jwt
import redis
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import yaml
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Конфигурация
CONFIG_DIR = Path(__file__).parent / "config"

# Глобальные переменные
redis_client = None
http_client = None
services_config = {}
routes_config = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    global redis_client, http_client, services_config, routes_config
    
    logger.info("Starting API Gateway...")
    
    # Загружаем конфигурацию
    try:
        with open(CONFIG_DIR / "services.yaml", "r") as f:
            services_config = yaml.safe_load(f)
        with open(CONFIG_DIR / "routes.yaml", "r") as f:
            routes_config = yaml.safe_load(f)["routes"]
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        services_config = {}
        routes_config = []
    
    # Инициализируем Redis
    try:
        redis_client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True
        )
        redis_client.ping()
        logger.info("Redis connected successfully")
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
    lifespan=lifespan
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
class HealthResponse:
    status: str
    timestamp: str
    services: Dict[str, str]
    metrics: Dict[str, Any]

class AuthRequest:
    username: str
    password: str

class AuthResponse:
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
        detail=f"Service {service_name} not configured"
    )

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Верифицировать JWT токен."""
    token = credentials.credentials
    
    # Получаем секрет из конфигурации или используем значение по умолчанию
    SECRET_KEY = services_config.get("auth", {}).get(
        "jwt_secret",
        "development-secret-key-change-in-production"
    )
    
    # Получаем алгоритм из конфигурации
    algorithm = services_config.get("auth", {}).get("algorithm", "HS256")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def check_rate_limit(user_id: str, endpoint: str) -> bool:
    """Проверить rate limit для пользователя и endpoint."""
    if not redis_client:
        return True  # Пропускаем если Redis недоступен
    
    key = f"rate_limit:{user_id}:{endpoint}:{int(time.time() // 3600)}"
    
    try:
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, 3600)  # Expire через час
        
        # Получаем лимит из конфигурации
        limit = 100  # По умолчанию
        for route in routes_config:
            if endpoint.startswith(route["path"]):
                limit_str = route.get("rate_limit", "100/hour")
                limit = int(limit_str.split("/")[0])
                break
        
        return current <= limit
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return True  # Fail open

async def forward_request(
    service_name: str,
    path: str,
    method: str,
    request: Request,
    user_payload: Optional[Dict] = None
) -> JSONResponse:
    """Перенаправить запрос к целевому сервису."""
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
        except:
            body = await request.body()
    
    # Отправляем запрос
    try:
        response = await http_client.request(
            method=method,
            url=target_url,
            headers=headers,
            json=body if isinstance(body, dict) else None,
            content=body if not isinstance(body, dict) else None,
            params=dict(request.query_params)
        )
        
        # Возвращаем ответ
        return JSONResponse(
            content=response.json() if response.headers.get("content-type") == "application/json" else response.text,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=f"Service {service_name} timeout"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Service {service_name} unavailable: {str(e)}"
        )

# Middleware для логирования и rate limiting
@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    """Middleware для обработки всех запросов."""
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
    
    # Логируем начало запроса
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    # Проверяем rate limit для аутентифицированных пользователей
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            # Декодируем токен для получения user_id
            SECRET_KEY = "development-secret-key-change-in-production"
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_signature": False})
            user_id = payload.get("sub", "unknown")
            
            if not check_rate_limit(user_id, request.url.path):
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Rate limit exceeded",
                            "details": {
                                "limit": "100/hour",
                                "reset_in": 3600
                            }
                        }
                    }
                )
        except:
            pass  # Если не удалось декодировать токен, пропускаем rate limiting
    
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
async def health_check() -> Dict[str, Any]:
    """Health check gateway и всех сервисов."""
    services_status = {}
    
    # Проверяем каждый сервис
    for service_name, config in services_config.get("services", {}).items():
        try:
            health_url = f"{config['base_url']}{config.get('health_check', '/health')}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(health_url)
                services_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception as e:
            services_status[service_name] = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": services_status,
        "metrics": {
            "uptime": "0d 0h 0m",  # В production считать от времени старта
            "request_count": redis_client.get("gateway:request_count") if redis_client else 0
        }
    }

@app.post("/auth/login")
async def login(auth: AuthRequest) -> AuthResponse:
    """Аутентификация пользователя."""
    # В production использовать реальную базу пользователей
    # Здесь упрощенная реализация для демонстрации
    
    # Проверяем credentials (в production - против базы данных)
    if auth.username == "admin" and auth.password == "admin":
        payload = {
            "sub": auth.username,
            "roles": ["admin", "editor", "viewer"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        # Получаем секрет и алгоритм из конфигурации
        SECRET_KEY = services_config.get("auth", {}).get(
            "jwt_secret",
            "development-secret-key-change-in-production"
        )
        algorithm = services_config.get("auth", {}).get("algorithm", "HS256")
        token = jwt.encode(payload, SECRET_KEY, algorithm=algorithm)
        
        return AuthResponse(
            access_token=token,
            expires_in=86400  # 24 часа в секундах
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

# Динамические routes на основе конфигурации
def setup_routes():
    """Настроить маршруты на основе конфигурации."""
    for route in routes_config:
        path = route["path"]
        target = route["target"]
        methods = route.get("methods", ["GET"])
        auth_required = route.get("auth_required", False)
        
        # Создаем endpoint для каждого метода
        for method in methods:
            # Создаем closure для захвата текущих значений
            def create_handler(route_path, route_target, route_auth_required):
                if route_auth_required:
                    async def handler(request: Request, user_payload: Dict = Depends(verify_token)):
                        # Извлекаем остаток пути после префикса
                        request_path = request.url.path
                        if request_path.startswith(route_path):
                            service_path = request_path[len(route_path):] or "/"
                        else:
                            service_path = request_path
                        
                        return await forward_request(
                            service_name=route_target,
                            path=service_path,
                            method=request.method,
                            request=request,
                            user_payload=user_payload
                        )
                else:
                    async def handler(request: Request):
                        # Извлекаем остаток пути после префикса
                        request_path = request.url.path
                        if request_path.startswith(route_path):
                            service_path = request_path[len(route_path):] or "/"
                        else:
                            service_path = request_path
                        
                        return await forward_request(
                            service_name=route_target,
                            path=service_path,
                            method=request.method,
                            request=request,
                            user_payload=None
                        )
                return handler
            
            # Создаем и регистрируем handler
            handler = create_handler(path, target, auth_required)
            
            # Регистрируем endpoint
            app.add_api_route(
                path=path + "{rest_of_path:path}",
                endpoint=handler,
                methods=[method],
                include_in_schema=True
            )

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
            "redoc": "/redoc"
        },
        "routes": [
            {
                "path": route["path"],
                "target": route["target"],
                "methods": route.get("methods", ["GET"]),
                "auth_required": route.get("auth_required", False)
            }
            for route in routes_config
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)