# 🚀 Quickstart (2 минуты до первого запуска)

## 1. Clone & Docker Up
```bash
git clone https://github.com/leadarchitect-ai/portfolio-system-architect.git
cd portfolio-system-architect
git lfs install  # Если LFS файлы
docker compose up -d  # 7 services: IT-Compass, RAG API, ML Registry
```

## 2. Verify (30s)
| Service | URL | What |
|---------|-----|------|
| **IT-Compass** | http://localhost:8501 | Competency tracker |
| **Cloud-Reason (RAG)** | http://localhost:8000/docs | AI reasoning API |
| **ML Registry** | http://localhost:8001/docs | Model versioning |
| **Grafana** | http://localhost:3000 | Monitoring (admin/prom) |

`open index.html` — Portfolio overview.

## 3. Users Examples
- **Newcomer**: [04_DEVELOPMENT/examples/newcomer-example.md](../04_DEVELOPMENT/examples/newcomer-example.md)
- **Developer**: pytest + extend src/
- **Noobs**: Edit markers in it-compass → track progress.

## Troubleshooting
- Logs: `docker compose logs`
- LFS: `./scripts/check-lfs.sh`
- Python dev: `pip install -r requirements-dev.txt && pytest`

**Time-to-Value: <2min. Questions?** [INDEX.md](INDEX.md)

