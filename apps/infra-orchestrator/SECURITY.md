# Security Policy

## Supported Versions

Only the latest major version of Infra-Orchestrator Framework receives security updates.

## Reporting a Vulnerability

If you discover a security vulnerability, please report it privately via the repository's security advisory feature (GitHub) or contact the maintainers directly.

Do not disclose the vulnerability publicly until it has been addressed.

## Security Measures

- All PowerShell scripts are analyzed with PSScriptAnalyzer for best practices.
- Secrets are managed via secure vaults (Windows Credential Manager, Azure Key Vault).
- Module signing is recommended for production deployments.
- Regular dependency scanning for known vulnerabilities.
