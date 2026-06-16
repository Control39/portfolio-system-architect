# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

Если вы обнаружили уязвимость, пожалуйста, отправьте отчёт на leadarchitect@yandex.ru

## Known Vulnerabilities (Monitoring)

### chromadb 1.5.9 - CVE-2026-45829
- **Severity**: High
- **Status**: ⚠️ Fix not yet released
- **Mitigation**: Monitor PyPI for updates, auto-update via Dependabot
- **Impact**: Vector storage component (used by embedding_agent)

### torch 2.12.0 - CVE-2025-3000
- **Severity**: Medium
- **Status**: ⚠️ Fix not yet released
- **Mitigation**: Monitor PyPI for updates, auto-update via Dependabot
- **Impact**: ML framework (dependency of sentence-transformers for RAG)

## Automated Monitoring

- **Dependabot**: Enabled for Python dependencies
- **pip-audit**: Run weekly in CI/CD
- **Trivy**: Container and dependency scanning
- **CodeQL**: Static analysis for security issues

## Update Policy

All dependencies are automatically updated via Dependabot when security fixes are released.
