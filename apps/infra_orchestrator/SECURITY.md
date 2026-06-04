# Security Policy

## Supported Versions

Only the latest version of Infra-Orchestrator receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 5.x+    | ✅ Python (Current) |
| 6.x     | ❌ PowerShell (Deprecated) |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it privately via the repository's security advisory feature (GitHub) or contact the maintainers directly.

Do not disclose the vulnerability publicly until it has been addressed.

## Security Measures

- All input validation is performed using Pydantic models.
- Secrets are managed via environment variables and `.env` files (not committed).
- Regular dependency scanning with `pip-audit` and `safety`.
- Static analysis with Bandit for Python security issues.
- Container scanning with Trivy for Docker images.

## Deprecated PowerShell Version

The previous PowerShell-based implementation (v6.0.0 and earlier) is no longer supported. If you are still using it, please migrate to the Python version (v5.0.0+) immediately.
