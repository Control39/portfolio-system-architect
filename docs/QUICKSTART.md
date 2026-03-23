# 🚀 Quickstart (2 минуты до первого запуска)

## 1. Clone & Docker Up
```bash
git clone https://github.com/leadarchitect-ai/portfolio-system-architect.git
cd portfolio-system-architect
git lfs install
docker compose up -d
```

## 2. Verify (30s)
| Service | URL | What |
|---------|-----|------|
| **IT-Compass** | http://localhost:8501 | Competency tracker |
| **Cloud-Reason** | http://localhost:8000/docs | AI reasoning API |
| **ML Registry** | http://localhost:8001/docs | Model versioning |
| **Grafana** | http://localhost:3000 | Monitoring |

`open index.html`

## 3. PowerShell Super Tree 🗂️
```powershell
# Magic tree с Git/Size/JSON
tree -Icon -Size -GitStatus  # 📁 apps [✅ Clean] (1.2 MB)
tree -Json apps > structure.json  # CI
tree -Filter '*.ps1' -Modified
```

## 4. Установка tree глобально
```powershell
pwsh scripts/dev/setup-profile.ps1
# Теперь `tree` всегда доступна!
```

## 5. Другие tools
- `pwsh tests/run-tests.ps1`
- `pwsh tools/run_daily.ps1`

## Troubleshooting
- Docker logs
- `./scripts/check-lfs.sh`

**Ready to rock! 🎸**

