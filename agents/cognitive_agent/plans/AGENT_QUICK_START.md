# 🤖 Cognitive Automation Agent — Быстрый старт

## ✅ **Проверка готовности**

```bash
# 1. Убедись, чтоguardrails.yaml существует
ls -l agents/cognitive_agent/config/guardrails.yaml

# 2. Запусти агента
python -m agents.cognitive_agent.autonomous_agent --start

# 3. Проверь статус (где будут allowed_paths)
python -m agents.cognitive_agent.autonomous_agent --status
