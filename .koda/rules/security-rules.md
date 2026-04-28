---
apply: Always
mode: Agent
---

## Security Rules

### 1. **Secrets Management:**

**NEVER commit:**
- API keys
- Passwords
- Database credentials
- Private keys
- JWT secrets
- OAuth tokens

**Use environment variables:**
```python
# ✅ Good
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# ❌ Bad
SECRET_KEY = "super-secret-key-123"
DATABASE_URL = "postgresql://user:pass@localhost/db"
```

**.env.example template:**
```bash
# Required variables
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0

# Optional variables
DEBUG=false
LOG_LEVEL=INFO
```

### 2. **Input Validation:**

**Rules:**
- Validate ALL user inputs
- Use Pydantic models for data validation
- Sanitize HTML/rich text
- Validate file uploads (type, size)
- Rate limit public endpoints

**Example:**
```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
```

### 3. **SQL Injection Prevention:**

**Rules:**
- Use ORM (SQLAlchemy, Django ORM)
- Parameterized queries only
- No string concatenation for SQL

**Example:**
```python
# ✅ Good (SQLAlchemy)
user = session.query(User).filter(User.email == email).first()

# ✅ Good (parameterized)
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# ❌ Bad (SQL injection)
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### 4. **Authentication & Authorization:**

**Rules:**
- Use JWT or session-based auth
- Hash passwords (bcrypt, argon2)
- Implement MFA for sensitive operations
- Role-based access control (RBAC)
- Validate permissions on every request

**Password hashing:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### 5. **XSS Prevention:**

**Rules:**
- Escape all user-generated content
- Use Content-Security-Policy headers
- Sanitize HTML with bleach
- Set HttpOnly flag on cookies

**Example:**
```python
import bleach

def sanitize_html(content: str) -> str:
    return bleach.clean(
        content,
        tags=['p', 'br', 'strong', 'em'],
        attributes={},
        strip=True
    )
```

### 6. **CSRF Prevention:**

**Rules:**
- Use CSRF tokens for state-changing operations
- SameSite cookie attribute
- Verify Origin/Referer headers

### 7. **Security Headers:**

**Required headers:**
```python
headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}
```

### 8. **Dependency Security:**

**Tools:**
- `pip-audit` - Check for vulnerabilities
- `safety` - Alternative vulnerability checker
- `dependabot` - Automated updates

**Commands:**
```bash
# Check vulnerabilities
pip-audit
safety check

# Update dependencies
pip-review --auto

# Pin versions
pip freeze > requirements.txt
```

### 9. **Logging Security:**

**Rules:**
- Don't log sensitive data (passwords, tokens, PII)
- Use structured logging
- Set appropriate log levels
- Rotate logs regularly

**Example:**
```python
import logging

logger = logging.getLogger(__name__)

# ✅ Good
logger.info(f"User login attempt", extra={"user_id": user_id, "ip": request.ip})

# ❌ Bad
logger.info(f"User login: {email}, password: {password}")
```

### 10. **Security Scanning:**

**Tools:**
- `bandit` - Python security linter
- `trufflehog` - Secret detection
- `gitleaks` - Git secret scanning

**Commands:**
```bash
# Bandit security audit
bandit -r src/ -ll

# Find secrets
trufflehog filesystem .
gitleaks detect --source . -v
```

---

## Security Checklist

### Before Commit:
- [ ] No secrets in code
- [ ] No hardcoded credentials
- [ ] Input validation added
- [ ] SQL queries parameterized

### Before Merge:
- [ ] Security tests pass
- [ ] Dependency audit clean
- [ ] Bandit scan clean
- [ ] AuthZ/AuthN reviewed

### Before Release:
- [ ] Penetration test (if major changes)
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Monitoring alerts set up
