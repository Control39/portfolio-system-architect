# Security Policy

## 🔒 Supported Versions

| Version | Supported |
|---------|-----------|
| main (latest) | ✅ |
| < 1.0.0 | ⚠️ Use latest |

## 🛡️ Security Practices

This project follows enterprise-grade security practices:

### Automated Security Scanning
- **Trivy** - Container and dependency vulnerability scanning
- **Bandit** - Python security linting
- **Dependabot** - Automated dependency updates
- **Secret scanning** - GitGuardian / Trivy secret detection

### Infrastructure Security
- **Sealed Secrets** - Encrypted Kubernetes secrets
- **Network Policies** - Pod-to-pod communication restrictions
- **Pod Security Policies** - Container runtime restrictions
- **Rate Limiting** - Traefik API gateway protection

### Code Quality & Security
- **Pre-commit hooks** - Automated security checks before commit
- **CI/CD gates** - Security scans in every pipeline
- **Dependency pinning** - Fixed versions to prevent supply chain attacks
- **Least privilege** - Minimal permissions for service accounts

## 📊 Security Metrics

| Metric | Status |
|--------|--------|
| Trivy scans | ✅ Weekly |
| Bandit scans | ✅ Pre-commit |
| Dependabot | ✅ Enabled |
| Secret detection | ✅ Active |
| Security docs | ✅ Updated |

## 🐛 Reporting a Vulnerability

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. **DO** email: leadarchitect@yandex.ru
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within **48 hours** and provide:
- Acknowledgment of receipt
- Timeline for fix
- Credit (if desired)

## 🔍 Security Audit Trail

All security-related changes are documented in:
- [`docs/security/`](docs/security/) - Security documentation
- [`docs/security/SECURITY-SCAN.md`](docs/security/SECURITY-SCAN.md) - Scan results
- GitHub Security tab - Dependabot alerts

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

*Last updated: May 2026*
