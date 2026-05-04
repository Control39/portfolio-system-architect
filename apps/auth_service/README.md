# Auth Service

Authentication and authorization service for Portfolio System Architect.

## Getting Started

```bash
cd apps/auth_service
pytest tests/ -v
```

## Configuration

Configuration files are in `config/` directory.

## API Endpoints

- POST `/auth/login` - User login
- POST `/auth/logout` - User logout
- GET `/auth/verify` - Token verification

## Testing

```bash
pytest tests/ -v --cov
```

## Development

See `src/` for source code and `tests/` for test files.
