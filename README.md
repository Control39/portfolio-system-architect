# Portfolio System Architect

This repository contains a comprehensive portfolio system for a Lead AI Systems Architect, demonstrating advanced capabilities in AI-driven career development, cloud reasoning, and system architecture.

## Project Structure

- `apps/` - Main application modules
- `src/` - Shared source code
- `tests/` - Test suites
- `docs/` - Documentation
- `deployment/` - Deployment configurations
- `diagrams/` - Architecture diagrams
- `scripts/` - Utility scripts
- `tools/` - Development tools

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements-dev.txt`
3. Set up environment variables
4. Run the application: `docker compose up -d`

## Docker

A `.dockerignore` file is included to optimize build performance by excluding unnecessary files:

```
__pycache__/
*.pyc
.git/
.venv/
node_modules/
*.log
.env
.coverage
htmlcov/
.pytest_cache/
dist/
build/
*.egg-info/
```

## Documentation for Employers

For a quick overview of the project's value and capabilities, see the [One-Pager](docs/employer/ONE-PAGER.md) designed for technical leads and hiring managers.

## GitOps & CI/CD

The project implements a modern GitOps workflow with automated security gates, container scanning, and Kubernetes deployment.

- **CI Pipeline**: Security scanning (detect‑secrets, safety, pip‑audit, Trivy), linting, testing, Docker builds, and GitOps deployment.
- **GitOps**: Kubernetes manifests are managed with Kustomize and automatically applied via Argo CD or GitHub Actions.
- **Secrets Management**: Encrypted secrets using Sealed Secrets / SOPS.

For detailed instructions, see [GitOps Guide](docs/DEVOPS_GITOPS_GUIDE.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

See: https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions

**Documentation:**
- API Docs: https://Control39.github.io/cognitive-systems-architecture/
- Scaling Plan: [docs/scaling-plan.md](docs/scaling-plan.md)
- GitOps Guide: [docs/DEVOPS_GITOPS_GUIDE.md](docs/DEVOPS_GITOPS_GUIDE.md)
- Security: [docs/security/SECRETS-MANAGEMENT.md](docs/security/SECRETS-MANAGEMENT.md)

**Monitoring (Grafana/Prometheus):**
```
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d prometheus grafana
```
Grafana: http://localhost:3000 (admin/admin)
Prometheus: http://localhost:9090
