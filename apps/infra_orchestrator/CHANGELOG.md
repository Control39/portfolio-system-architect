# Changelog

All notable changes to the Infra-Orchestrator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Migration from PowerShell to Python**: Service converted from PowerShell-based implementation to Python/FastAPI.
- Dockerfile updated to use `python:3.11-slim` base image.
- PowerShell module files (`.psd1`, `.psm1`) removed.
- Dependencies switched to Python packages (pydantic, requests, python-dotenv).

### Added
- FastAPI-based REST API with Swagger documentation.
- Uvicorn as ASGI server.
- Python unit tests with pytest (33 tests, ~75% coverage).
- AI Config Manager integration.

### Removed
- PowerShell module (`InfraOrchestrator.psd1`, `InfraOrchestrator.psm1`).
- Pester tests and PSScriptAnalyzer configuration.
- PowerShell-specific CI/CD pipelines.

## [5.0.0] - 2026-03-21
### Added
- Python FastAPI implementation for infrastructure orchestration.
- REST API endpoints for service management, deployment, and scaling.
- Integration with AI Config Manager.
- Docker support with Python base image.

### Changed
- Migrated from PowerShell implementation (v6.0.0) to Python.
- Replaced Pester tests with pytest.
- Updated documentation to reflect Python stack.

## [6.0.0] - 2026-03-21 (PowerShell Legacy)
### Added
- PowerShell module for architectural decision automation.
- Integration with AI assistants for architectural analysis.
- Security scanning and validation features.
- YAML-based configuration management.
- CI/CD pipeline support.

> **Note:** This version is deprecated. The service has been migrated to Python (v5.0.0+).