# 🏛️ Portfolio System Architect - Architecture Guide

**Last Updated**: 2026-05-04  
**Status**: 🟢 Production Ready  
**Version**: 2.0 (After Option B Completion)

---

## 📚 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Service Tiers](#service-tiers)
4. [Data Flow](#data-flow)
5. [Integration Points](#integration-points)
6. [Deployment Model](#deployment-model)
7. [Scalability](#scalability)
8. [High Availability](#high-availability)

---

## 🔍 System Overview

### Vision
Portfolio System Architect is a **microservices-based intelligent platform** that combines:
- 🤖 AI-powered automation
- 🧠 Advanced decision-making
- 🗺️ System thinking methodology
- 📊 Knowledge management
- 🔧 Infrastructure orchestration

### Core Principles
1. **Microservices Architecture** - Independent, deployable services
2. **Scalability First** - Horizontal scaling built-in
3. **Resilience** - Fault tolerance and recovery
4. **Observability** - Complete visibility into system
5. **Testability** - 100% test coverage mandate

### Key Metrics
- **Services**: 15 microservices
- **Test Coverage**: 100% (325+ tests)
- **Health Score**: 100% (all services operational)
- **Uptime Target**: 99.9%
- **Response Time**: <200ms (p99)

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│                   CLIENT LAYER                      │
│         (Web UI, Mobile, API Clients)               │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              API GATEWAY LAYER                      │
│    (Request routing, Authentication, Rate limit)   │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│           MICROSERVICES LAYER                       │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │
│  │ AI Services  │ │ Core Logic   │ │ Infra Mgmt │  │
│  └──────────────┘ └──────────────┘ └────────────┘  │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│            DATA LAYER                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │PostgreSQL│ │  Redis   │ │ChromaDB  │           │
│  └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│         MONITORING & LOGGING LAYER                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │Prometheus│ │ Grafana  │ │ELK Stack │           │
│  └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. Client Layer
- User interfaces
- External integrations
- Request initiation

#### 2. API Gateway
- Request routing
- Authentication/Authorization
- Rate limiting
- Request validation

#### 3. Microservices Layer
- Business logic
- Service-specific operations
- Inter-service communication

#### 4. Data Layer
- Persistent storage
- Caching
- Vector embeddings

#### 5. Monitoring Layer
- Metrics collection
- Log aggregation
- Alerting

---

## 🎯 Service Tiers

### Tier 1: Core AI Services (4 services)

**Purpose**: Intelligent decision-making and automation

#### cognitive-agent 🤖
- **Role**: AI-powered automation engine
- **Dependencies**: decision-engine, knowledge-graph
- **Capabilities**: Learning, reasoning, task execution
- **Scaling**: Horizontal (stateless)
- **Tests**: 15 basic + 16 integration = 31 tests

#### decision-engine 🧠
- **Role**: Core decision-making system
- **Dependencies**: it_compass, knowledge-graph
- **Capabilities**: Complex reasoning, constraint solving
- **Scaling**: Horizontal (stateless)
- **Tests**: 15 basic + 16 integration = 31 tests

#### it_compass 🗺️
- **Role**: System thinking and architecture analysis
- **Dependencies**: decision-engine, knowledge-graph
- **Capabilities**: Architecture analysis, pattern recognition
- **Scaling**: Horizontal (compute-intensive can scale)
- **Tests**: 15 basic + 16 integration = 31 tests

#### knowledge-graph 📊
- **Role**: Knowledge management and relationships
- **Dependencies**: None (core data service)
- **Capabilities**: Entity storage, relationship querying, graph analysis
- **Scaling**: Vertical + Read replicas
- **Tests**: 15 basic tests = 15 tests

**Tier 1 Total**: 4 services, 108 tests

### Tier 2: Infrastructure Services (4 services)

**Purpose**: System management and protocol handling

#### infra-orchestrator ⚙️
- **Role**: Infrastructure management
- **Dependencies**: auth_service, mcp-server
- **Capabilities**: Service orchestration, resource allocation
- **Scaling**: Single master + workers
- **Tests**: 15 basic + 16 integration = 31 tests

#### auth_service 🔐
- **Role**: Authentication and authorization
- **Dependencies**: None (core security service)
- **Capabilities**: Token management, permission checking
- **Scaling**: Horizontal + caching
- **Tests**: 15 basic tests = 15 tests

#### mcp-server 📡
- **Role**: Model Context Protocol implementation
- **Dependencies**: cognitive-agent, decision-engine
- **Capabilities**: Protocol handling, message routing
- **Scaling**: Horizontal (stateless)
- **Tests**: 15 basic + 16 integration = 31 tests

#### ml-model-registry 🧮
- **Role**: ML model storage and versioning
- **Dependencies**: None (data service)
- **Capabilities**: Model management, version control, retrieval
- **Scaling**: Distributed storage
- **Tests**: 15 basic tests = 15 tests

**Tier 2 Total**: 4 services, 92 tests

### Tier 3: Business Services (7 services)

**Purpose**: Domain-specific functionality

#### portfolio_organizer 💼
- Role: Portfolio management
- Tests: 15 tests

#### career_development 📈
- Role: Career progression tracking
- Tests: 15 tests

#### job-automation-agent 🤖
- Role: Task automation and scheduling
- Tests: 15 tests

#### ai-config-manager ⚙️
- Role: Configuration management
- Tests: 15 tests

#### template-service 📋
- Role: Template rendering and management
- Tests: 15 tests

#### system-proof ✅
- Role: System validation and proof generation
- Tests: 15 tests

#### thought-architecture 💭
- Role: Thought architecture design
- Tests: 15 tests

**Tier 3 Total**: 7 services, 105 tests

---

## 🔄 Data Flow

### Request Flow

```
Client Request
    ↓
API Gateway (routing, auth)
    ↓
Service Handler (business logic)
    ↓
Dependency Resolution
    ├─ Same-tier services (sync calls)
    ├─ Cross-tier services (async/queues)
    └─ Data services (cached when possible)
    ↓
Data Layer (query/cache/store)
    ├─ PostgreSQL (relational)
    ├─ Redis (cache)
    └─ ChromaDB (vectors)
    ↓
Response Assembly
    ↓
Client Response
```

### Service Communication Patterns

#### Synchronous (Direct Calls)
- Same tier services
- Real-time decisions needed
- Low latency critical

#### Asynchronous (Message Queue)
- Cross-tier dependencies
- Batch operations
- Fire-and-forget tasks

#### Event-Driven
- Service notifications
- State changes
- Audit logging

---

## 🔗 Integration Points

### Service Dependencies

#### Tier 1 Dependencies
```
cognitive-agent ──→ decision-engine
              ├─→ knowledge-graph
              └─→ mcp-server (protocol)

decision-engine ──→ it_compass
                ├─→ knowledge-graph
                └─→ auth_service (permissions)

it_compass ─────→ decision-engine
           ├─→ knowledge-graph
           └─→ ml-model-registry (models)

knowledge-graph → (no dependencies - core service)
```

#### Tier 2 Dependencies
```
infra-orchestrator ─→ auth_service
                   ├─→ mcp-server
                   └─→ ml-model-registry

auth_service ──→ (no dependencies - core service)

mcp-server ────→ cognitive-agent
            ├─→ decision-engine
            └─→ knowledge-graph

ml-model-registry → (no dependencies - core service)
```

#### Tier 3 Dependencies
- Tier 3 services primarily depend on Tier 1 & 2
- Can call each other for domain-specific operations
- Mostly stateless for scalability

### Data Store Integration

#### PostgreSQL
- Relational data
- ACID transactions
- Services: auth_service, ml-model-registry, Tier 3

#### Redis
- Caching layer
- Session storage
- Rate limiting
- All services with cache needs

#### ChromaDB
- Vector embeddings
- Semantic search
- Services: knowledge-graph, ai-config-manager

---

## 🚀 Deployment Model

### Container-Based Deployment

#### Docker Architecture
```
Service Container
├── Python runtime (3.10/3.11/3.12)
├── Application code
├── Dependencies (pip)
├── Configuration
└── Health checks
```

#### Multi-Stage Builds
```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY src/ /app/src/
CMD ["python", "-m", "uvicorn", "src.main:app"]
```

### Kubernetes Deployment

#### Service Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cognitive-agent
spec:
  replicas: 3  # Horizontal scaling
  selector:
    matchLabels:
      app: cognitive-agent
  template:
    metadata:
      labels:
        app: cognitive-agent
    spec:
      containers:
      - name: cognitive-agent
        image: portfolio-architect/cognitive-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "INFO"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

#### Service Exposure
```yaml
apiVersion: v1
kind: Service
metadata:
  name: cognitive-agent
spec:
  selector:
    app: cognitive-agent
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP  # Internal service
```

---

## 📈 Scalability

### Horizontal Scaling

#### Stateless Services (Easy)
- cognitive-agent ✅
- decision-engine ✅
- mcp-server ✅
- Tier 3 services ✅

**Strategy**: Add more replicas
```bash
kubectl scale deployment cognitive-agent --replicas=5
```

#### Stateful Services (Medium)
- knowledge-graph (read replicas)
- ml-model-registry (distributed)

**Strategy**: Database replication + cache

#### Single-Master Services (Complex)
- infra-orchestrator (requires coordination)

**Strategy**: Load balancing + message queue

### Performance Optimization

#### Caching Strategy
```
Level 1: In-memory (application level)
   ├─ Result caching (30s TTL)
   ├─ Configuration caching (1h TTL)
   └─ Session caching (24h TTL)

Level 2: Redis (shared cache)
   ├─ User data cache (1h)
   ├─ Query results (5m)
   └─ API responses (30s)

Level 3: Database query optimization
   ├─ Indexed queries
   ├─ Connection pooling
   └─ Read replicas
```

#### Load Balancing
```
Nginx/HAProxy
    ├─ Round-robin for stateless services
    ├─ Sticky sessions for stateful
    └─ Circuit breaker on failure
         ↓
    Service Replicas (N instances)
```

---

## 🔒 High Availability

### Redundancy Model

```
Primary Region
├─ 3× cognitive-agent replicas
├─ 3× decision-engine replicas
├─ 2× knowledge-graph (1 primary, 1 replica)
├─ PostgreSQL primary + replica
├─ Redis sentinel
└─ Health monitors

Secondary Region (DR)
├─ Standby replicas
├─ PostgreSQL standby
├─ Data sync via replication
└─ DNS failover ready
```

### Failure Scenarios

#### Service Failure
- **Detection**: Liveness probe fails
- **Action**: Remove from load balancer
- **Recovery**: New pod spins up
- **SLA**: <30 seconds

#### Database Failure
- **Detection**: Connection pool exhausted
- **Action**: Failover to replica
- **Recovery**: Automatic (Kubernetes)
- **SLA**: <1 minute

#### Network Partition
- **Detection**: Service unreachable
- **Action**: Circuit breaker opens
- **Recovery**: Exponential backoff retry
- **SLA**: Graceful degradation

### Monitoring & Alerts

#### Key Metrics
```
Service Level:
- Error rate (threshold: >1%)
- Latency p99 (threshold: >500ms)
- Request rate (threshold: >10k/s)

Infrastructure:
- CPU utilization (threshold: >80%)
- Memory utilization (threshold: >85%)
- Disk I/O (threshold: >90%)

Database:
- Connection pool utilization
- Query latency
- Replication lag
```

#### Alert Actions
```
Severity: Critical (SLA: respond <5m)
├─ Service down
├─ High error rate (>5%)
└─ Database unavailable

Severity: Warning (SLA: respond <15m)
├─ High latency (>1s)
├─ High CPU (>90%)
└─ High memory (>90%)

Severity: Info (SLA: respond <1h)
├─ Unusual patterns
├─ Approaching limits
└─ Performance degradation
```

---

## 🔧 Configuration Management

### Environment-Based Configuration

#### Development
```yaml
log_level: DEBUG
cache_ttl: 60
api_timeout: 30s
db_pool_size: 5
```

#### Staging
```yaml
log_level: INFO
cache_ttl: 300
api_timeout: 10s
db_pool_size: 20
```

#### Production
```yaml
log_level: WARN
cache_ttl: 3600
api_timeout: 5s
db_pool_size: 50
circuit_breaker_threshold: 5
```

### Secrets Management

```
Kubernetes Secrets:
├─ Database credentials
├─ API keys
├─ TLS certificates
└─ OAuth tokens

Rotation Policy:
├─ Credentials: 90 days
├─ Certificates: 1 year
└─ Tokens: On demand
```

---

## 🧪 Testing Architecture

### Test Pyramid

```
       ▲
      /  \          Integration Tests (5%)
     /    \         - Cross-service
    /      \        - End-to-end scenarios
   /────────\
  /          \      Enhanced Tests (25%)
 /            \     - Error handling
/              \    - Performance
────────────────    - Resource mgmt
Unit Tests (70%)
- Basic functionality
- Edge cases
- Mock dependencies
```

### Test Types

#### Unit Tests (210 tests)
- Basic functionality
- Error scenarios
- Resource management
- Performance baselines

#### Integration Tests (80+ tests)
- Cross-service communication
- Dependency management
- Error recovery
- Concurrent operations

#### End-to-End Tests (Coming)
- Full user workflows
- Multi-service scenarios
- Production-like data

---

## 📋 Best Practices

### Service Development

1. **Stateless Design**
   - No in-memory state across requests
   - All state in persistent storage
   - Enables horizontal scaling

2. **Error Handling**
   - Explicit error types
   - Proper logging
   - Graceful degradation

3. **Testing**
   - Minimum 15 tests per service
   - Mock external dependencies
   - Test error scenarios

4. **Documentation**
   - API documentation
   - Configuration guide
   - Troubleshooting guide

### API Design

1. **RESTful Principles**
   - Standard HTTP methods
   - Resource-based endpoints
   - Proper status codes

2. **Versioning**
   - API version in URL: `/api/v1/`
   - Backward compatibility
   - Deprecation path

3. **Pagination**
   - Limit/offset or cursor-based
   - Default page size
   - Maximum page size

4. **Error Responses**
   ```json
   {
     "error": "invalid_request",
     "message": "User not found",
     "code": 404,
     "timestamp": "2026-05-04T12:00:00Z"
   }
   ```

---

## 🚦 Deployment Pipeline

```
Developer Push
    ↓
[1] Code Review
    └─ Pass PR checks
    ↓
[2] Build
    ├─ Multi-stage Docker build
    ├─ Security scan
    └─ Tag with commit SHA
    ↓
[3] Test
    ├─ Unit tests (210+)
    ├─ Integration tests (80+)
    └─ Coverage report
    ↓
[4] Security
    ├─ Dependency scan
    ├─ SAST analysis
    └─ Container scan
    ↓
[5] Deploy
    ├─ Staging environment
    ├─ Smoke tests
    └─ Blue-green deployment
    ↓
[6] Production
    ├─ Canary rollout (5%)
    ├─ Monitor metrics
    ├─ Full rollout (100%)
    └─ Post-deployment tests
```

---

## 📞 Support & Troubleshooting

### Common Issues

#### Service Not Responding
1. Check pod status: `kubectl get pods`
2. Check logs: `kubectl logs <pod-name>`
3. Check health endpoint: `curl localhost:8000/health`
4. Check dependencies: `kubectl describe pod <pod-name>`

#### High Latency
1. Check CPU/Memory: `kubectl top pods`
2. Check database: `SELECT * FROM performance_stats`
3. Check cache hit rate
4. Review query plans

#### High Error Rate
1. Check application logs
2. Check database connectivity
3. Check external service availability
4. Review error types distribution

---

## 🔗 Related Documentation

- [Service README](../../apps/cognitive-agent/README.md) - Individual service guides
- [Deployment Guide](./DEPLOYMENT.md) - Step-by-step deployment
- [API Reference](./API_REFERENCE.md) - API endpoints
- [Testing Guide](./TESTING.md) - Test execution guide

---

**Status**: 🟢 Production Ready  
**Last Updated**: 2026-05-04  
**Maintainer**: Architecture Team

