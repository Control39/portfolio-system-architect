# 🚀 Quick Start Guide

Get started with the Portfolio System Architect in under 5 minutes. This guide walks you through setting up the complete cognitive architecture ecosystem locally.

## 📋 Prerequisites

- **Docker & Docker Compose** (Docker Desktop or Docker Engine)
- **Git** with Git LFS (Large File Storage)
- **4GB+ RAM** available for containers
- **Python 3.12+** (optional, for development)

## 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/leadarchitect-ai/portfolio-system-architect.git
cd portfolio-system-architect

# Initialize Git LFS (required for some model files)
git lfs install
git lfs pull
```

## 2. Start the Ecosystem

```bash
# Start all services with Docker Compose
docker compose up -d

# Check service status
docker compose ps
```

The ecosystem includes 8 integrated microservices:
- **IT-Compass** - Skills tracking and career navigation
- **Cloud-Reason** - AI reasoning API with RAG capabilities
- **ML Model Registry** - Versioned AI model management
- **Portfolio Organizer** - Automated evidence collection
- **Career Development** - AI-driven career planning
- **System Proof** - Formal verification of decisions
- **Monitoring Stack** - Prometheus, Grafana, AlertManager
- **Database** - PostgreSQL with pgAdmin

## 3. Access Services

| Service | URL | Purpose | Default Credentials |
|---------|-----|---------|-------------------|
| **IT-Compass UI** | http://localhost:8501 | Competency tracker & portfolio | - |
| **Cloud-Reason API** | http://localhost:8000/docs | AI reasoning & RAG | - |
| **ML Registry API** | http://localhost:8001/docs | Model versioning | - |
| **Grafana** | http://localhost:3000 | Monitoring & dashboards | admin/admin |
| **Prometheus** | http://localhost:9090 | Metrics collection | - |
| **pgAdmin** | http://localhost:5050 | Database management | admin@admin.com/admin |
| **Portfolio Dashboard** | http://localhost:8080 | System overview | - |

## 4. Verify Installation

### Quick Health Check
```bash
# Run the health check script
python scripts/python/healthcheck.py

# Or check Docker logs
docker compose logs --tail=50
```

### Test API Endpoints
```bash
# Test Cloud-Reason API
curl http://localhost:8000/health

# Test ML Registry
curl http://localhost:8001/health

# Test overall system health
curl http://localhost:8080/health
```

## 5. First Steps

### Explore IT-Compass
1. Open http://localhost:8501
2. Navigate through competency tracking features
3. Try the burnout prevention analytics
4. Explore career path recommendations

### Try Cloud-Reason AI
1. Open http://localhost:8000/docs
2. Try the `/rag/query` endpoint with technical questions
3. Test systematic thinking prompts
4. Experiment with different reasoning modes

### Monitor System Health
1. Open Grafana at http://localhost:3000
2. Login with admin/admin
3. Explore the "Portfolio System" dashboard
4. Check service metrics and performance

## 6. Development Setup (Optional)

For development and contribution:

```bash
# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run the audit tool
python -m tools.repo_audit.audit --level base
```

## 7. Troubleshooting

### Common Issues

#### Docker Compose Fails
```bash
# Check Docker daemon is running
docker ps

# Check for port conflicts
netstat -an | grep -E ":(8501|3000|9090|5050)"

# Clean start
docker compose down -v
docker compose up -d
```

#### Git LFS Issues
```bash
# Reinstall Git LFS
git lfs uninstall
git lfs install
git lfs pull

# Check LFS files
git lfs ls-files
```

#### Insufficient Resources
```bash
# Reduce resource allocation in docker-compose.override.yml
# Or increase Docker Desktop resources (Settings → Resources)
```

#### Services Not Starting
```bash
# Check specific service logs
docker compose logs it-compass
docker compose logs cloud-reason

# Check database connectivity
docker compose exec postgres psql -U architect -d portfolio
```

### Getting Help

- **Documentation**: See [README.md](../README.md) for overview
- **Technical Details**: [FOR-TECH.md](FOR-TECH.md) for architects
- **Issue Tracking**: GitHub Issues for bug reports
- **Community**: SourceCraft platform for discussions

## 8. Next Steps

### For Evaluation
- Review [PROFESSIONAL-IDENTITY-PLAN.md](PROFESSIONAL-IDENTITY-PLAN.md) for context
- Check [TEST-COVERAGE-METRICS.md](TEST-COVERAGE-METRICS.md) for quality metrics
- Explore [FOR-TECH.md](FOR-TECH.md) for architectural details

### For Development
- Read [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Set up pre-commit hooks: `pre-commit install`
- Run full test suite: `pytest --cov`

### For Production
- Review [deployment/](../deployment/) for Kubernetes configurations
- Check [monitoring/](../monitoring/) for observability setup
- Read [SECURITY_FIXES_COMPLETED.md](../SECURITY_FIXES_COMPLETED.md) for security

---

**Need more help?**  
- Check the [troubleshooting guide](../docs/troubleshooting.md)
- Open an issue on [GitHub](https://github.com/leadarchitect-ai/portfolio-system-architect/issues)
- Contact via [SourceCraft](https://sourcecraft.io/portfolio-system-architect)

*The Portfolio System Architect is designed to demonstrate production-grade cognitive architecture. Each component is fully functional and production-ready.*

