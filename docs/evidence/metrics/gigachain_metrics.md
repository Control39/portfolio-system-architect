# GigaChain Metrics Dashboard

## Key Metrics (Targets from Plan)
| Metric | Current | Target | Test Command |
|--------|---------|--------|--------------|
| MCP Latency | N/A | <3s | `locust -f load_test.py` |
| Verification Accuracy | 95% (stub) | >90% | `pytest tests/ -m verification` |
| Test Coverage | N/A | >92% | `pytest --cov=cloud_reason/` |
| RAG Throughput | N/A | 20 qpm | `ab -n 100 http://localhost:8000/rag` |

## Logging
- Traces → system-proof/.
- Self-improve suggestions logged.

**Update:** Run after `docker compose up decision-engine`.
