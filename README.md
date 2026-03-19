**Secrets for GitHub Actions:**
```
DOCKER_USERNAME = your_dockerhub_username
DOCKER_PASSWORD = your_dockerhub_token (app password)
TELEGRAM_BOT_TOKEN = bot token
TELEGRAM_CHAT_ID = chat id
```
See: https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions

**Documentation:**
- API Docs: [docs/api/_build/html/index.html](docs/api/_build/html/index.html)
- Scaling Plan: [docs/scaling-plan.md](docs/scaling-plan.md)

**Monitoring (Grafana/Prometheus):**
```
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d prometheus grafana
```
Grafana: http://localhost:3000 (admin/admin)
Prometheus: http://localhost:9090
