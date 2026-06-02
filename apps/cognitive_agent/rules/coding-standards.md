---
apply: Always
mode: Agent
---

## Python Coding Standards

### 1. **Code Formatting:**

**Black:**
- Line length: 100 characters
- Target version: Python 3.12
- String quotes: Double quotes

**isort:**
- Profile: black
- Line length: 100
- Order: future, standard_library, third_party, first_party, local_folder

### 2. **Linting (Ruff):**

**Enabled rules:**
- E: pycodestyle errors
- W: pycodestyle warnings
- F: Pyflakes
- I: isort
- N: pep8-naming
- UP: pyupgrade
- YTT: flake8-2020
- S: flake8-bandit (security)
- BLE: flake8-blind-except
- B: flake8-bugbear
- A: flake8-builtins
- C4: flake8-comprehensions
- DTZ: flake8-datetimez
- T10: flake8-debugger
- ISC: flake8-implicit-str-concat
- ICN: flake8-import-conventions
- G: flake8-logging-format
- INP: flake8-no-pep420
- PIE: flake8-pie
- T20: flake8-print
- PT: flake8-pytest-style
- Q: flake8-quotes
- RSE: flake8-raise
- RET: flake8-return
- SLF: flake8-self
- SIM: flake8-simplify
- TID: flake8-tidy-imports
- ARG: flake8-unused-arguments
- PTH: flake8-use-pathlib
- ERA: eradicate (commented-out code)
- PD: pandas-vet
- PGH: pygrep-hooks
- PL: pylint
- TRY: tryceratops
- FLY: flynt
- PERF: perflint
- RUF: Ruff-specific rules

### 3. **Type Hints:**

**Required:**
- Function parameters (except self, cls)
- Function return types
- Variable annotations for complex types

**Optional:**
- Simple local variables
- self, cls in methods

**Tools:**
- mypy: strict mode
- pyright: basic type checking

### 4. **Docstrings:**

**Style:** Google Style

**Required for:**
- Modules
- Classes
- Public functions
- Public methods

**Example:**
```python
def process_data(data: list[dict], timeout: int = 30) -> dict:
    """Process input data with configurable timeout.

    Args:
        data: List of dictionaries containing input records.
        timeout: Request timeout in seconds (default: 30).

    Returns:
        Dictionary with processed results and metadata.

    Raises:
        ValueError: If data format is invalid.
        TimeoutError: If processing exceeds timeout.
    """
```

### 5. **Naming Conventions:**

| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `user_service.py` |
| Classes | PascalCase | `UserService` |
| Functions | snake_case | `get_user_by_id()` |
| Variables | snake_case | `user_count` |
| Constants | UPPER_CASE | `MAX_RETRIES` |
| Private | _prefix | `_internal_cache` |
| Type vars | PascalCase | `T`, `KT`, `VT` |

### 6. **Error Handling:**

**Rules:**
- Catch specific exceptions (not bare `except:`)
- Use `raise from` for exception chaining
- Log exceptions with context
- Don't swallow exceptions silently

**Example:**
```python
try:
    result = await fetch_data(url)
except aiohttp.ClientError as e:
    logger.error(f"Failed to fetch {url}: {e}", extra={"url": url})
    raise DataServiceError(f"Failed to fetch data: {e}") from e
```

### 7. **Async/Await:**

**Rules:**
- Use `async def` for I/O-bound operations
- Use `asyncio.gather()` for concurrent operations
- Always `await` coroutines
- Use `async with` for async context managers
- Timeout long-running operations

### 8. **Testing:**

**Framework:** pytest

**Rules:**
- Test file naming: `test_*.py`
- Test function naming: `test_*`
- Use fixtures for setup/teardown
- Mock external dependencies
- Minimum 80% code coverage
- Parametrize similar tests

### 9. **Imports:**

**Order:**
1. Future imports
2. Standard library
3. Third-party
4. First-party
5. Local folder

**Rules:**
- One import per line
- Absolute imports preferred
- No wildcard imports (`from x import *`)
- No circular imports

### 10. **Security:**

**Rules:**
- No hardcoded secrets (use environment variables)
- Validate all inputs
- Use parameterized queries (no SQL injection)
- Hash passwords (bcrypt, argon2)
- Verify SSL certificates
- Rate limit public APIs

---

## Quick Commands

```bash
# Format code
black .
isort .

# Lint code
ruff check .
ruff format .

# Type checking
mypy src/

# Run tests
pytest tests/ -v --cov=. --cov-report=html

# Security audit
bandit -r src/ -ll
pip-audit
```
