# Onboarding & Cognitive-Drift Mitigation

## Windows Quickstart (RF audience)

```cmd
git clone ...
cd portfolio-system-architect
docker compose up -d
start http://localhost:8501
```

## Formal Onboarding Checklist


1. **Clone & Setup**:
   ```
   git clone https://github.com/leadarchitect-ai/portfolio-system-architect.git
   cd portfolio-system-architect
   git lfs install
   ```

2. **Verify LFS**: `./scripts/check-lfs.sh`

3. **Local CI**:
   ```
   pip install -r requirements-dev.txt
   pytest BENCHMARK_SUITE/
   chmod +x BENCHMARK_SUITE/*.sh && BENCHMARK_SUITE/test_coverage.sh
   ```

4. **Production Stack** (with PostgreSQL + Monitoring):
   ```
   docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.monitoring.yml up -d postgres pgadmin prometheus grafana
   ```

5. **Schema Pipeline**:
   ```
   python tools/generate_pydantic.py  # Generate shared pydantic models
   cd apps/career-development && alembic upgrade head  # Migrate DB
   ```

6. **Verify Stack**:
   | Service | URL | Credentials |
   |---------|-----|-------------|
   | PgAdmin | localhost:5050 | admin/admin123 |
   | Postgres | localhost:5432 | architect/arch_pass_2024 |
   | Grafana | localhost:3000 | admin/admin |
   | IT-Compass | localhost:8501 | - |
   | Career-Dev | localhost:8000/docs | - |
   | Health Check | `python scripts/healthcheck.py` | - |
   | Ecosystem Sync | `python scripts/sync-from-my-ecosystem.py --preview` | docs/external-ecosystem/ |
   
7. **Daily Ops**:
   ```
   python scripts/healthcheck.py          # 🟢 All systems healthy
   python tools/generate_pydantic.py      # Refresh schemas
   python tools/benchmark.py              # 🏆 Benchmark report (latency <200ms)
   ```
   
   **Example Healthcheck Output:**
   ```
   🩺 Portfolio System Health Check
   postgres             🟢 UP localhost:5432
   pgadmin              🟢 UP localhost:5050
   prometheus           🟢 UP localhost:9090
   grafana              🟢 UP localhost:3000
   ✅ ALL SYSTEMS HEALTHY
   ```


## Cognitive-Drift Mitigation

**Daily Protocol**:
- Run `./07_TOOLS/run_daily.ps1` → Review output.
- Check `low_energy_mode.log` in it-compass logs.
- Update `02_MODULES/it-compass/support/resources/crisis_contacts.json` if needed.

**Crisis Response**:
- `low_energy_mode.py` → Generate report: `python 02_MODULES/it-compass/src/core/mental/support.py`.
- Contacts from `crisis_contacts.json`.

**Mental Load Testing**:
1. Simulate 100RPS → Grafana RPS/CPU.
2. If CPU>70% or latency>200ms → Activate low_energy_mode.

## ADR Template

**Title**: [Short Title]

**Status**: Proposed | Accepted | Deprecated

**Context**: ...

**Decision**: ...

**Consequences**: ...

**Module Manifest Update**:
```json
{"adr": "path/to/adr.md", "version": "1.0"}
```

Sign-off: Signed-off-by: Name <email>

