# API Interfaces & Module Boundaries

This document describes the public interfaces of each microservice, ensuring loose coupling and clear module boundaries.

## Overview

All services are exposed via the central API Gateway (Traefik) at `http://localhost:80`. Each service has a dedicated path prefix.

## Service Endpoints

| Service | Path Prefix | Port (Internal) | Description |
|---------|-------------|-----------------|-------------|
| Auth Service | `/auth` | 8100 | JWT token issuance and validation |
| IT-Compass | `/it-compass` | 8501 | Skill tracking UI (Streamlit) |
| Cloud-Reason | `/cloud-reason` | 8001 | RAG API for document reasoning |
| ML Model Registry | `/ml-registry` | 8001 | Model versioning and deployment |
| Career Development | `/career-dev` | 8000 | Career path recommendations |
| Portfolio Organizer | `/portfolio-organizer` | 8004 | Project portfolio management |
| System Proof | `/system-proof` | 8003 | Chain-of-Thought storage and retrieval |
| Arch Compass | `/arch-compass` | 8002 | Architecture decision tracking |

## Interface Contracts

### 1. Auth Service
- **POST /auth/token** – Issue JWT token (username/password)
- **POST /auth/validate** – Validate token
- **GET /auth/health** – Health check

### 2. Cloud-Reason
- **POST /cloud-reason/api/v1/query** – Submit a natural language query
- **GET /cloud-reason/api/v1/status** – Service status
- **GET /cloud-reason/api/v1/docs** – OpenAPI spec

### 3. ML Model Registry
- **POST /ml-registry/api/v1/models** – Register a new model
- **GET /ml-registry/api/v1/models/{id}** – Retrieve model metadata
- **PUT /ml-registry/api/v1/models/{id}/deploy** – Deploy model

### 4. System Proof
- **POST /system-proof/api/v1/proofs** – Store a proof
- **GET /system-proof/api/v1/proofs/{id}** – Retrieve proof
- **GET /system-proof/health** – Health check

### 5. Career Development
- **GET /career-dev/api/v1/paths** – List career paths
- **POST /career-dev/api/v1/recommend** – Get personalized recommendations

### 6. Portfolio Organizer
- **GET /portfolio-organizer/api/v1/projects** – List projects
- **POST /portfolio-organizer/api/v1/projects** – Add project

### 7. IT-Compass
- Web UI only; no external API.

### 8. Arch Compass
- **GET /arch-compass/api/v1/decisions** – List architecture decisions
- **POST /arch-compass/api/v1/decisions** – Create new decision

## Versioning

All APIs follow semantic versioning via URL path:
- `/api/v1/...` – current stable version
- `/api/v2/...` – future version (when needed)

## Communication Patterns

- **Synchronous HTTP/REST** – for request/response interactions.
- **Event‑Driven (planned)** – using Redis Pub/Sub for async notifications.
- **Database per Service** – each service owns its PostgreSQL schema; no direct cross‑service DB access.

## Gateway Rules

Traefik routing labels are defined in `docker-compose.yml`. Each service must:

1. Expose a health endpoint at `/health` (HTTP 200).
2. Use the `traefik.enable=true` label.
3. Define a unique router rule based on `PathPrefix`.

## Dependency Matrix

Services may call each other only via their public HTTP endpoints. Internal dependencies:

- Cloud‑Reason → Auth (token validation)
- System Proof → Auth (optional)
- ML Model Registry → Cloud‑Reason (model inference)

## Monitoring & Observability

Each service exports Prometheus metrics at `/metrics`. Logs are aggregated via Loki. Traces are collected via Jaeger.

## Change Management

When modifying an API endpoint:

1. Update this document.
2. Update the service’s OpenAPI spec (if any).
3. Notify dependent service owners.
4. Maintain backward compatibility for at least one release cycle.

## See Also

- [Traefik Configuration](../docker-compose.yml)
- [Service Health Checks](../scripts/healthcheck.py)
- [API Gateway Dashboard](http://localhost:8080)