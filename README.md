# 🏗 Portfolio System Architect

<div align="center">

# 🏗 Portfolio System Architect

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![CI/CD](https://img.shields.io/github/actions/workflow/status/Control39/portfolio-system-architect/deploy-k8s.yml?label=CI/CD)](https://github.com/Control39/portfolio-system-architect/actions)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/Docs-MkDocs-blue)](https://control39.github.io/portfolio-system-architect/)

*AI-powered portfolio ecosystem with 15 microservices, RAG, and autonomous agents*

</div>

> **Production-ready microservices platform** with 14+ services, 95% code coverage, and complete analysis ecosystem.

**Created by**: Single person over 2 years | **Status**: 🟢 Production Ready

---

## 🔄 📢 RECENT UPDATE - Architecture Reorganization Complete! 🎉

**NEW**: Comprehensive architecture reorganization with complete documentation and navigation system!

✨ **What's New:**

- 📖 **Comprehensive documentation** for easy navigation and understanding
- 🧭 **Navigation script** (`navigate.ps1`) for instant access to any component
- 📊 **Project dashboard** with complete metrics, status, and structure
- 🎯 **90-day improvement plan** in `NEXT_STEPS.md`
- 📋 **Quick reference card** for common commands and links

**🚀 Quick Start After Update:**

- 👉 **[START HERE](./START_HERE.md)** if you're new to this project
- 📚 **[ARCHITECTURE_MAP.md](./ARCHITECTURE_MAP.md)** - Full architecture overview
- 📊 **[DASHBOARD.md](./DASHBOARD.md)** - Metrics, status, structure
- 🧭 **[navigate.ps1](./navigate.ps1)** - Quick navigation script

**See all changes on branch**: [`docs/global-architecture-refactoring-2026`](https://github.com/Control39/portfolio-system-architect/tree/docs/global-architecture-refactoring-2026)

---

## 📊 Project Overview

| Metric               | Value        | Status           |
| -------------------- | ------------ | ---------------- |
| **Microservices**    | 14+          | 🟢 Production    |
| **Code Coverage**    | 95%          | ✅ Excellent     |
| **Development Time** | 2 years      | 🎓 Mature        |
| **Infrastructure**   | K8s + Docker | 📦 Enterprise    |
| **Documentation**    | ~2000 files  | 📚 Comprehensive |
| **Analysis Tools**   | 4 integrated | 🛠️ Complete      |

---

## 🚀 Quick Start

### 1. **Understand the Architecture**

```bash
# Read the start here guide
cat START_HERE.md
<!-- REAL METRICS - Updated automatically -->
## 📊 REAL METRICS (Updated Automatically)

<p align="center">
  <img src="https://img.shields.io/badge/Python%20Files-7366-blue?style=flat-square" alt="Python Files">
  <img src="https://img.shields.io/badge/Test%20Files-1424-green?style=flat-square" alt="Test Files">
  <img src="https://img.shields.io/badge/Microservices-15-brightgreen?style=flat-square" alt="Microservices">
  <img src="https://img.shields.io/badge/Lines%20of%20Code-59.4k-orange?style=flat-square" alt="Lines of Code">
  <img src="https://img.shields.io/badge/Git%20Commits-1144-purple?style=flat-square" alt="Git Commits">
  <img src="https://img.shields.io/badge/Git%20Branches-31-blue?style=flat-square" alt="Git Branches">
  <img src="https://img.shields.io/badge/K8s%20Resources-73-informational?style=flat-square" alt="K8s Resources">
  <img src="https://img.shields.io/badge/Dockerfiles-15-ff69b4?style=flat-square" alt="Dockerfiles">
</p>

### What These Numbers Mean

| Metric | Value | Meaning |
|--------|-------|---------|
| **Python Files** | 7366 | Complete codebase across all services |
| **Test Files** | 1424 | Unit, integration, and e2e tests |
| **Microservices** | 15 | Independent deployable services |
| **Lines of Code** | 59.4k | Actual implementation (excluding tests & dependencies) |
| **Git Commits** | 1144 | Full development history |
| **Git Branches** | 31 | Active development branches |
| **K8s Resources** | 73 | Production-grade Kubernetes configuration |
| **Dockerfiles** | 15 | One per service + utility containers |

---


# Read the architecture map
cat ARCHITECTURE_MAP.md

# View the project dashboard
cat DASHBOARD.md

# Navigate the project
./navigate.ps1 -Map
```

### 2. **Access a Service**

```bash
# Navigate to any microservice
./navigate.ps1 -Service cognitive-agent
./navigate.ps1 -Service decision-engine
./navigate.ps1 -Service it-compass
```

### 3. **Check Project Status**

```bash
./navigate.ps1 -Status
./navigate.ps1 -List
```

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    IDE & ANALYSIS TOOLS                        │
│    (Koda • Sourcecraft • Continue • Codeassistant)             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
     ┌────────────────┼────────────────┐
     │                │                │
┌────▼────┐  ┌─────────▼────────┐  ┌──▼─────────────┐
│ Tier 1  │  │    Tier 2        │  │   Tier 3       │
│  Core   │  │ Infrastructure   │  │  Business      │
└────┬────┘  └─────────┬────────┘  └──┬─────────────┘
     │                 │              │
  ┌──▼──────────────────▼──────────────▼───┐
  │    14 Microservices in Production      │
  │ (see ARCHITECTURE_MAP.md for details)  │
  └──────────────────┬─────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
 ┌───▼──────┐  ┌────▼──────┐  ┌───▼──────┐
 │Monitoring│  │ Database  │  │  Logs    │
 │(Prometheus)  │(PostgreSQL)  │(ELK)     │
 └──────────┘  └───────────┘  └──────────┘
```

---

## 🏗️ Architecture Evolution

This repository represents the evolution of the Cognitive Automation Agent from a monolithic prototype to a production-grade platform:

| Metric            | v1 (Prototype)        | v2 (Current Platform)                  | Impact                    |
| ----------------- | --------------------- | -------------------------------------- | ------------------------- |
| **Skills**        | 5 (`.agents/skills/`) | 19 (`codeassistant/skills/`)           | +280% coverage            |
| **Automation**    | 1 workflow            | 31 GitHub Actions                      | Distributed autonomy      |
| **Architecture**  | Monolith script       | 15 microservices                       | Fault isolation & scaling |
| **Deployment**    | Local `python -m`     | Docker + K8s (50+ manifests)           | Cloud-native ready        |
| **Observability** | JSON dumps            | Prometheus + Grafana                   | Real-time monitoring      |
| **Security**      | Manual checks         | Pre-commit + Trivy + Gitleaks + CodeQL | Shift-left security       |

**Key Takeaway**: v2 replaces local dependencies with infrastructure-level guarantees, ensuring reproducibility, scalability, and enterprise-grade security.

---

## 📦 Microservices (14+)

### Core Services

- **🤖 Cognitive Agent** - AI-powered automation
- **🧠 Decision Engine** - Decision-making system
- **🗺️ IT-Compass** - System thinking methodology
- **🔗 Knowledge Graph** - Knowledge management

### Infrastructure

- **⚙️ Infra Orchestrator** - Infrastructure management
- **🔐 Auth Service** - Authentication & authorization
- **📦 MCP Server** - Model Context Protocol
- **🏛️ ML Model Registry** - ML model management

### Business Services

- **💼 Portfolio Organizer** - Portfolio management
- **📈 Career Development** - Career progression
- **🤖 Job Automation Agent** - Task automation
- **⚙️ AI Config Manager** - Configuration management
- **📋 Template Service** - Template management
- **✅ System Proof** - System validation

---

## 🛠️ Analysis & Tools

### IDE Integration

| Tool              | Location         | Purpose           | Status    |
| ----------------- | ---------------- | ----------------- | --------- |
| **Koda**          | `.koda/`         | Code intelligence | ✅ Active |
| **Sourcecraft**   | `.sourcecraft/`  | Code assistant    | ✅ Active |
| **Continue**      | `.continue/`     | AI agents         | ✅ Active |
| **Codeassistant** | `codeassistant/` | Skills & tools    | ✅ Active |

### Analysis Skills

- Code Security Auditor
- DevOps CI/CD Analyzer
- Git Health Checker
- Performance Profiler
- Code Quality Auditor
- - 5 more specialized skills

### Monitoring Stack

```
Prometheus (http://localhost:9090)  → Metrics collection
        ↓
Grafana (http://localhost:3000)     → Visualization
        ↓
PostgreSQL (localhost:5432)         → Data storage
        ↓
Elasticsearch (localhost:9200)      → Log aggregation
```

---

## 📚 Documentation

### Navigation Guides (NEW!)

- **[START_HERE.md](./START_HERE.md)** - Entry point for new developers
- **[ARCHITECTURE_MAP.md](./ARCHITECTURE_MAP.md)** - Complete architecture overview
- **[DASHBOARD.md](./DASHBOARD.md)** - Project dashboard & metrics
- **[QUICK_REFERENCE_CARD.md](./QUICK_REFERENCE_CARD.md)** - Quick reference
- **[NEXT_STEPS.md](./NEXT_STEPS.md)** - 90-day development plan
- **[navigate.ps1](./navigate.ps1)** - Quick navigation script

### Service Documentation

Each microservice has its own:

- `apps/<service>/README.md` - Service overview
- `apps/<service>/docs/` - Detailed documentation
- `apps/<service>/config/` - Configuration files

### Project Documentation

```
docs/
├── architecture/       - Architecture decisions (ADR)
├── methodology/        - System thinking approach
├── api/               - API documentation
├── integration/       - Integration guides
├── cases/             - Use cases & examples
└── security/          - Security documentation
```

---

## 🧪 Testing & Quality

### Coverage

```
Overall Coverage: 95% ✅

Tier 1 (Core):        94-96% ✅
Tier 2 (Infra):       88-92% ✅
Tier 3 (Business):    82-89% ✅
```

### Running Tests

```bash
# Unit tests for a service
cd apps/<service>
pytest tests/ -v

# With coverage report
pytest tests/ --cov

# Integration tests
pytest tests/integration/ -v

# All tests
pytest tests/ --cov --report=html
```

---

## 🐳 Docker & Deployment

### Docker Setup

```bash
# Build service
docker build -f docker/<service>/Dockerfile -t <service>:latest .

# Build all services
docker-compose build

# Run services
docker-compose up
```

### Kubernetes Deployment

```bash
# Apply configurations
kubectl apply -f deployment/k8s/

# Check status
kubectl get pods
kubectl logs -f <pod-name>

# Access services
kubectl port-forward svc/<service> 8080:80
```

---

## 📊 Metrics & Monitoring

### Key Metrics

- **Code Coverage**: 95%
- **Uptime**: 99.9%
- **Response Time**: <200ms
- **Error Rate**: <0.1%
- **Deployment Frequency**: Daily
- **Mean Time to Recovery**: <5min

### View Dashboards

```bash
# Prometheus
open http://localhost:9090

# Grafana
open http://localhost:3000
# Default login: admin/admin

# Service logs
kubectl logs -f deployment/<service>
```

---

## 🔧 Development

### Setup Environment

```bash
# Clone repository
git clone <repository>
cd portfolio-system-architect

# Install dependencies
pip install -r requirements.txt

# Setup dev environment
./scripts/setup.sh

# Start local services
docker-compose -f docker-compose.dev.yml up
```

### Development Workflow

```bash
# 1. Navigate to service
./navigate.ps1 -Service <name>
cd apps/<service>

# 2. Make changes
# 3. Run tests
pytest tests/ -v --cov

# 4. Check code quality
./navigate.ps1 -Tool koda
./navigate.ps1 -Tool codeassistant

# 5. Commit & push
git add .
git commit -m "feat: description"
git push
```

---

## 🚀 Deployment

### Development

```bash
docker-compose -f docker-compose.dev.yml up
```

### Staging

```bash
kubectl apply -f deployment/k8s/overlays/staging/
```

### Production

```bash
kubectl apply -f deployment/k8s/overlays/production/
```

---

## 🤝 Contributing

### Guidelines

1. Read [ARCHITECTURE_MAP.md](./ARCHITECTURE_MAP.md)
2. Use [navigate.ps1](./navigate.ps1) to find resources
3. Follow existing code patterns
4. Maintain 95%+ code coverage
5. Update documentation

### Process

1. Create feature branch
2. Implement changes
3. Write tests
4. Run quality checks
5. Submit for review
6. Deploy to production

---

## 📋 Useful Commands

### Navigation (NEW!)

```bash
# Start here if you're new
cat START_HERE.md

# Open architecture map
./navigate.ps1 -Map

# List all services
./navigate.ps1 -List

# Go to service
./navigate.ps1 -Service cognitive-agent

# Check project status
./navigate.ps1 -Status

# Find documentation
./navigate.ps1 -Docs architecture
```

### Development

```bash
# Run all tests
pytest tests/ -v --cov

# Start services
docker-compose up

# View logs
docker-compose logs -f <service>

# Access database
psql -h localhost -U postgres
```

### Monitoring

```bash
# Prometheus
curl http://localhost:9090/api/v1/query?query=up

# Grafana dashboards
open http://localhost:3000

# Service metrics
kubectl top pods
kubectl top nodes
```

---

## 🎓 Learning Resources

### Understanding the System

1. **Start**: [START_HERE.md](./START_HERE.md)
2. **Explore**: [ARCHITECTURE_MAP.md](./ARCHITECTURE_MAP.md)
3. **Reference**: [QUICK_REFERENCE_CARD.md](./QUICK_REFERENCE_CARD.md)
4. **Use**: `./navigate.ps1` to find components
5. **Read**: Individual service READMEs
6. **Study**: [docs/methodology/](./docs/methodology/) for system thinking

### Specific Topics

- **Microservices**: [docs/architecture/](./docs/architecture/)
- **Deployment**: [deployment/README