"""
JWT Auth Service
Issues and validates JWT tokens for API Gateway
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional

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
    
    Demo: username=demo, password=demo → returns token
    """
    # Demo auth (replace with real auth in production)
    if request.username == "demo" and request.password == "demo":
        return create_token(request.username, role="admin")
    
    if request.username and request.password:
        # Allow any username/password for demo
        return create_token(request.username, role="user")
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/verify")
async def verify(payload: dict = Depends(verify_token)):
    """Verify token validity"""
    return {
        "valid": True,
        "username": payload.get("username"),
        "role": payload.get("role"),
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service"}

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
        },
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
