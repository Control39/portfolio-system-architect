# Top 10 Questions from Tech Leads — Q&A

## Q1: How would you approach architecture for a 50-person startup?

**A**:
- Start with monolith + clear service boundaries (using DDD)
- Plan for 3 phases: MVP (monolith), Scale (services), Growth (mesh)
- Use evidence-based decisions (CoT traces for each major decision)
- Implement monitoring from day 1 (saves weeks of debugging later)
- **Proof**: Implemented this in Portfolio System Architect (8 microservices with Prometheus/Grafana)

---

## Q2: How do you handle secrets in production?

**A**:
- Never in code or env files → use HashiCorp Vault / AWS Secrets Manager / GCP Secret Manager
- Kubernetes: Sealed Secrets (encrypt before commit)
- CI/CD: GitHub Secrets (rotate every 90 days)
- Audit all access (who accessed what, when)
- **Proof**: docs/security/SECRETS-MANAGEMENT.md + deployment/k8s/base/security/rbac.yaml

---

## Q3: What's your approach to testing?

**A**:
- Target: 95%+ coverage (enforced in CI/CD)
- Test pyramid: unit (60%) → integration (30%) → e2e (10%)
- Mock external dependencies (databases, APIs)
- Performance tests for critical paths
- **Proof**: 95%+ pytest coverage in Portfolio System Architect (enforced by --cov-fail-under=95)

---

## Q4: How do you approach Kubernetes?

**A**:
- Start simple: Deployment + Service + ConfigMap
- Add NetworkPolicy for security (least-privilege networking)
- Implement RBAC (ServiceAccounts + Roles per service)
- HPA for auto-scaling (based on CPU/memory)
- Sealed Secrets for secrets management
- **Proof**: deployment/k8s/ has all patterns (K8s manifests for 8 services + security)

---

## Q5: How do you design for disaster recovery?

**A**:
- RPO (Recovery Point Objective): max 1 hour data loss
- RTO (Recovery Time Objective): restore in 15-30 minutes
- Automated daily backups to cloud (GCS/S3)
- Test restore quarterly (in isolated env)
- Document runbooks for each failure scenario
- **Proof**: DR_RUNBOOK.md + scripts/backup-postgres.sh + K8s CronJob for backups

---

## Q6: How do you approach monitoring & alerting?

**A**:
- 4 golden signals: latency, traffic, errors, saturation
- SLO/SLI metrics (99% availability, <1s P95 latency)
- Alert only on actionable events (not every spike)
- Post-mortems for all critical incidents
- **Proof**: monitoring/prometheus/rules.yml (20+ alert rules) + AlertManager integration

---

## Q7: How do you balance velocity vs. technical debt?

**A**:
- Allocate 20% of sprint to tech debt (not negotiable)
- Measure debt: test coverage, code complexity, security scan results
- Fix high-impact issues (failure-prone code, security vulnerabilities)
- Defer low-impact debt if urgent features needed
- **Proof**: Portfolio System Architect: 95%+ coverage maintained while shipping features

---

## Q8: How do you approach security?

**A**:
- Threat modeling (STRIDE) for architecture decisions
- Secrets management: Vault/AWS Secrets (never in code)
- RBAC (principle of least privilege)
- Network isolation (NetworkPolicy)
- Security scanning in CI/CD (detect-secrets, Trivy, bandit)
- Audit all API access
- **Proof**: deployment/k8s/base/security/ + docs/security/SECRETS-MANAGEMENT.md + CI/CD security scanning

---

## Q9: How do you make architecture decisions evidence-based?

**A**:
- Document assumptions (what we believe to be true)
- Implement Chain-of-Thought (CoT) reasoning
- Track outcomes (was the decision right?)
- Build verification system (audit trails)
- Share learnings across team
- **Proof**: system-proof module stores CoT traces + verification metadata

---

## Q10: What's your biggest architectural lesson?

**A**:
- Start simple, evolve based on evidence, not gut feel
- Most architecture mistakes come from over-engineering early
- Monitoring + observability pay for themselves in week 1
- Security is not optional (do it from day 1)
- **My approach**: Evidence-based decisions (documented in Portfolio System Architect)

---

## Follow-up: Can you walk us through Portfolio System Architect?

**Architecture**:
- 8 microservices (FastAPI + Streamlit backend)
- PostgreSQL (HA-ready with backups)
- Kubernetes (K8s manifests + Kustomize)
- Monitoring (Prometheus + Grafana + AlertManager)
- Terraform (infrastructure as code for GCP/AWS)
- Security (RBAC, TLS, secrets management, network policies)

**Deployment**:
- Local: `docker compose up`
- K8s: `kubectl apply -k deployment/k8s/overlays/staging`
- Terraform: `terraform apply -var-file=staging.tfvars`

**Test coverage**: 95%+ (pytest-cov)
**Audit result**: 92% grant-ready (verified)
**Enterprise-ready**: 🟢 98%+
