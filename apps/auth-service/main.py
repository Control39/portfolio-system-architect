"""
JWT Auth Service
Issues and validates JWT tokens for API Gateway
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel
import jwt
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

# Добавляем путь для импорта общих модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.common.health_check import init_health_checks

app = FastAPI(title="Auth Service", version="1.0.0")
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is required (production security)")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = 24

class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class User(BaseModel):
    username: str
    role: str = "user"

def create_token(username: str, role: str = "user") -> dict:
    """Create JWT token"""
    payload = {
        "username": username,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_HOURS * 3600,
    }

def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/token", response_model=TokenResponse)
async def login(request: TokenRequest):
    """
    Issue JWT token
    
    For demo purposes, any username/password combination is accepted except demo/demo.
    In production, implement real authentication against a user database.
    """
    # Block demo/demo credentials for security
    if request.username == "demo" and request.password == "demo":
        raise HTTPException(status_code=401, detail="Demo credentials not allowed")
    
    # In production, replace with real auth (e.g., database lookup, LDAP, OAuth)
    if request.username and request.password:
        # For demo: assign admin role to 'admin' username, user role to others
        role = "admin" if request.username == "admin" else "user"
        return create_token(request.username, role=role)
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/verify")
async def verify(payload: dict = Depends(verify_token)):
    """Verify token validity"""
    return {
        "valid": True,
        "username": payload.get("username"),
        "role": payload.get("role"),
    }


# Инициализируем health-check эндпоинты
init_health_checks(
    app,
    service_name="auth-service",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Service info"""
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "endpoints": {
            "POST /auth/token": "Issue JWT token",
            "POST /auth/verify": "Verify token",
            "GET /health": "Health check",
            "GET /ready": "Readiness probe",
            "GET /live": "Liveness probe",
        },
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
