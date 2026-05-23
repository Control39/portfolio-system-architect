---
hide:
  - navigation
  - toc
---
<div align="center">
# 🏗️ Portfolio System Architect
## Zero IT → Architect. Human leads AI: Proof | Metrics
<br>
[![🎯 Навигатор для работодателя](https://img.shields.io/badge/🎯_Навигатор_для_работодателя-3_минуты_до_ответа-4CAF50?style=for-the-badge&logo=readthedocs&logoColor=white)](employer/NAVIGATOR.md)
[![📚 Смотреть кейсы](https://img.shields.io/badge/📚_Кейсы-3_доказательства_компетенций-2196F3?style=for-the-badge&logo=github&logoColor=white)](cases/README.md)
[![🧬 Атомы и Молекулы](https://img.shields.io/badge/🧬_Архитектура-Атомы_и_Молекулы-9C27B0?style=for-the-badge&logo=databricks&logoColor=white)](architecture/atoms-and-molecules.md)
</div>
---
## ⚡ За 30 секунд
Этот проект — **доказательство архитектурного мышления уровня Senior/Architect**.
Построен по принципу **«Атомы и Молекулы»**:
- 🧬 **Атомы** (`src/`) — переиспользуемые компоненты (безопасность, схемы, утилиты)
- 🧪 **Молекулы** (`apps/`) — 18+ сервисов, собранных из атомов

**Подробнее:** [AI_INSTRUCTIONS.md](../AI_INSTRUCTIONS.md) — инструкция для ИИ о том, как понимать эту архитектуру.
---
## 🎯 Быстрая навигация по ролям
| Ваша роль | Что смотреть |
|-----------|--------------|
| 👔 **HR / Рекрутер** | [`FOR-HR.md`](FOR-HR.md) • [`ONE-PAGER.md`](ONE-PAGER.md) • [`COVER-LETTER.md`](COVER-LETTER.md) |
| 💻 **Tech Lead** | [`FOR-TECH.md`](FOR-TECH.md) • [`architecture/decisions/`](architecture/decisions/) • [`DEPENDENCY-MAP.md`](DEPENDENCY-MAP.md) |
| 🛠️ **DevOps** | [`DEPLOYMENT.md`](DEPLOYMENT.md) • [`MONITORING-CONFIGURATION.md`](MONITORING-CONFIGURATION.md) • [`SECURITY_AUDIT_REPORT.md`](SECURITY_AUDIT_REPORT.md) |
| 🏆 **Grant Committee** | [`FOR-GRANT.md`](FOR-GRANT.md) • [`grants/`](grants/) |
---
## 🧬 Архитектура в двух словах
```
src/ (Атомы)                apps/ (Молекулы)
├── security/        ──→    ├── auth_service/
├── shared/          ──→    ├── it_compass/
├── core/            ──→    ├── decision_engine/
└── common/          ──→    └── job_automation_agent/
```

**Принципы:**
- Слабая связанность (Loose Coupling)
- Переиспользование атомов
- Доказательная база через работающий код
---
## 📞 Контакты
- **Email:** leadarchitect@yandex.ru
- **GitHub:** [control39/portfolio-system-architect](https://github.com/control39/portfolio-system-architect)
---
<div align="center">
**Последнее обновление:** Май 2026
</div>
