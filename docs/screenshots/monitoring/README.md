# Monitoring Screenshots

This directory contains screenshots of the monitoring stack in action, demonstrating production-grade observability.

## 📸 Required Screenshots

### 1. Grafana Dashboards
- **`grafana-ai-service.png`** - AI service monitoring dashboard
- **`grafana-portfolio-overview.png`** - Portfolio overview dashboard
- **`grafana-infrastructure.png`** - Infrastructure metrics dashboard (optional)

### 2. Alert Notifications
- **`telegram-alert-example.png`** - Example of alert delivered via Telegram
- **`alertmanager-webui.png`** - Alertmanager web interface showing active alerts (optional)

### 3. Prometheus UI
- **`prometheus-targets.png`** - Prometheus targets page showing healthy services
- **`prometheus-graph.png`** - Prometheus graph showing metric queries (optional)

## 🚀 How to Capture Screenshots

### Prerequisites
1. Start the monitoring stack:
   ```bash
   docker compose -f docker-compose.monitoring.yml up -d
   ```

2. Wait for services to be healthy (check with `docker ps`)

### Step-by-Step Capture

#### Grafana Dashboards
1. Access Grafana at http://localhost:3000 (admin/admin)
2. Navigate to "Dashboards" → "Portfolio" dashboard
3. Adjust time range to show meaningful data (e.g., "Last 6 hours")
4. Take full-page screenshot (Ctrl+Shift+S on Windows, Cmd+Shift+4 on Mac)
5. Save as `grafana-portfolio-overview.png`

#### AI Service Dashboard
1. In Grafana, navigate to "Dashboards" → "AI Service" (or create it)
2. Ensure metrics are visible (may need to generate load on the AI service)
3. Capture screenshot and save as `grafana-ai-service.png`

#### Alert Notifications
1. Trigger a test alert:
   ```bash
   # Simulate high CPU usage
   docker run --rm -it busybox sh -c "while true; do :; done"
   ```
2. Wait 5+ minutes for alert to trigger
3. Check Telegram channel for alert notification
4. Capture screenshot of Telegram message
5. Save as `telegram-alert-example.png`

## 🎯 Best Practices for Screenshots

1. **Show meaningful data** - Ensure graphs have visible trends, not empty/zero lines
2. **Include context** - Capture browser URL, time range selector, dashboard title
3. **High resolution** - Use at least 1920x1080 resolution
4. **Annotate if needed** - Add arrows/circles to highlight key metrics
5. **Update references** - After adding screenshots, update `monitoring/README.md` image paths

## 📁 File Structure
```
docs/screenshots/monitoring/
├── README.md                          # This file
├── grafana-ai-service.png             # AI service dashboard
├── grafana-portfolio-overview.png     # Portfolio overview dashboard
├── telegram-alert-example.png         # Telegram alert notification
└── placeholder/                       # Placeholder images (temporary)
    ├── grafana-ai-service-placeholder.png
    └── telegram-alert-placeholder.png
```

## ⚠️ Placeholder Images

Currently, this directory contains placeholder images. To replace them with actual screenshots:

1. Delete the placeholder images
2. Capture actual screenshots following the instructions above
3. Name them exactly as specified in `monitoring/README.md`
4. Commit the actual screenshots to the repository

> **Note**: Placeholder images are intentionally empty/blank to avoid committing misleading or fake data. The portfolio's credibility depends on showing real, working monitoring.

