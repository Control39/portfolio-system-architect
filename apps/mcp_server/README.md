# MCP Server

**Model Context Protocol (MCP) server for AI agents**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 24/24 | ✅ 100% |
| **Покрытие** | ~85% | ✅ |
| **Линтинг** | Чисто | ✅ |
| **Уязвимости** | 0 | ✅ |

---

## 🚀 Возможности

- **MCP Protocol Support** — совместимость с Model Context Protocol
- **Tool Registration** — регистрация инструментов для AI-агентов
- **Resource Management** — управление ресурсами
- **Prompt Templates** — шаблоны промптов
- **Server Lifecycle** — запуск, остановка, health checks
- **API endpoints**:
  - `POST /tools` — регистрация инструмента
  - `GET /tools` — список инструментов
  - `POST /resources` — добавление ресурса
  - `GET /health` — health check

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/mcp_server/tests/ -v

# С покрытием
pytest apps/mcp_server/tests/ --cov=apps/mcp_server --cov-report=html
```

### Ключевые тесты
- **24 теста** (включая бизнес-логику)
- Покрытие: регистрация инструментов, управление ресурсами, обработка ошибок

---

**Last Updated**: 2026-05-15
**Status**: 🟢 Production Ready