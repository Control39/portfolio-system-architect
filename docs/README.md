---
layout: home
title: Portfolio System Architect
description: Production-ready cognitive architecture ecosystem
---

# 🧠 Portfolio System Architect

**Production-ready cognitive architecture ecosystem** demonstrating senior-level expertise in system design, AI integration, and DevOps.

> **This is NOT a tutorial project.** This is a working system used for real career development, portfolio organization, and AI-assisted decision making.

---

## 🚀 Quick Navigation

### For HR & Recruiters (2 min read)
- [Key Projects & Skills](./for_hr/key_projects.md)
- [Business Impact & ROI](./cases/business/README.md)
- [Career Development Path](./for_hr/career_path.md)

### For Technical Interviewers (10 min read)
- [Architecture Overview](./ARCHITECTURE.md)
- [Master diagram (Mermaid)](./diagrams/master-system.mmd)
- [Integration Cases](./cases/integration/README.md)
- [Technical Deep Dives](./cases/technical/README.md)

### For Architects & Senior Engineers
- [System Design Principles](./docs/architecture/atoms-and-molecules.md)
- [Decision Records (ADRs)](./docs/architecture/decisions/)
- [Case Studies: System Thinking](./cases/thinking/README.md)

### For Developers
- [Quick Start Guide](./QUICK_START.md)
- [Service Catalog](./apps/README.md)
- [Contribution Guide](./CONTRIBUTING.md)

---

## 📊 What Makes This Different

| Typical Portfolio | **This Portfolio** |
|------------------|-------------------|
| "I learned Docker" | ✅ Docker Compose + K8s in production |
| "I understand AI" | ✅ RAG, reasoning engines, multi-agent systems |
| "I can code" | ✅ Full CI/CD, monitoring, security, testing |
| Resume claims | **Executable evidence** |

---

## 🏗️ Architecture: Atoms & Molecules

This system uses a **compositional architecture** where:

- **Atoms** (`src/`) — Reusable components (security, schemas, utilities)
- **Molecules** (`apps/`) — Full services built from atoms

```
┌─────────────────────────────────────────┐
│           Atoms (Shared)                │
│  src/security/  src/shared/  src/core/  │
└─────────────────────────────────────────┘
              ↕️ reused by ↕️
┌─────────────────────────────────────────┐
│          Molecules (Services)           │
│  IT Compass │ AI Config │ Decision Eng  │
│  21 services total                      │
└─────────────────────────────────────────┘
```

---

## 📚 Documentation Index

### Cases (Proof of Work)
- [Integration Cases](./cases/integration/) — Multi-service integrations
- [Business Cases](./cases/business/) — ROI and value demonstration
- [Thinking Cases](./cases/thinking/) — Systematic problem solving
- [Evolution Cases](./cases/evolution/) — Architecture evolution journey
- [Technical Cases](./cases/technical/) — Deep technical implementations

### Services (21 Microservices)
- [AI Config Manager](./apps/ai_config_manager/) — Centralized AI configuration
- [IT Compass](./apps/it_compass/) — Competency tracking methodology
- [Decision Engine](./apps/decision_engine/) — AI reasoning with RAG
- [Portfolio Organizer](./apps/portfolio_organizer/) — Evidence collection
- [Career Development](./apps/career_development/) — Career path planning
- ... and 16 more services

### Infrastructure
- [Docker Setup](./DOCKERFILE_TEMPLATE_MONOREPO.txt)
- [Kubernetes Deploy](./deployment/k8s-README.md)
- [Monitoring Stack](./monitoring/README.md)

---

## 🎯 Why This Matters

This portfolio demonstrates **production-grade thinking**:

1. **Not "I studied"** — but "I built a working system"
2. **Not "I understand"** — but "I implemented with monitoring, tests, security"
3. **Not "Resumé claims"** — but "Executable evidence"

---

## 📞 Contact & Next Steps

- **GitHub:** [control39/portfolio-system-architect](https://github.com/control39/portfolio-system-architect)
- **Live Demo:** This site (GitHub Pages)
- **Source Code:** Full repository with 5000+ files
- **Methodology:** [IT Compass Framework](./cases/methodology/)

---

*Last updated: {{ site.time | date: "%Y-%m-%d" }}*

