import os
import re
from pathlib import Path

apps_dir = Path(r"C:\repo\apps")
services = [
    "ai_config_manager",
    "auth_service",
    "career_development",
    "cognitive_agent",
    "decision_engine",
    "infra_orchestrator",
    "it_compass",
    "job_automation_agent",
    "knowledge_graph",
    "mcp_server",
    "ml_model_registry",
    "portfolio_organizer",
    "system_proof",
    "template_service",
    "thought_architecture",
]

# Ключевые секции, которые должны быть в README (по шаблону template_service)
required_sections = [
    r"## 🎯 Назначение",
    r"## 🏗️ Архитектура",
    r"## 🚀 Быстрый старт|## 🚀 Quick Start",
    r"## 🧪 Тестирование|## Testing",
    r"## 📦 Зависимости|## Dependencies",
    r"## 🛡️ Безопасность|## Security",
]

print("=== Анализ структуры README ===\n")
print(f"{'Сервис':<25} {'Структура':<15} {'Секции':<10} {'Несовпадения'}")
print("-" * 80)

for service in services:
    service_dir = apps_dir / service
    readme = service_dir / "README.md"
    
    if not readme.exists():
        print(f"{service:<25} ❌ MISSING")
        continue
    
    content = readme.read_text(encoding="utf-8")
    
    # Определяем тип структуры по первым строкам
    lines = content.split("\n")[:10]
    first_lines = "\n".join(lines)
    
    if "Template Service" in first_lines or "шаблон" in first_lines.lower():
        structure = "Template"
    elif "## Contributing" in first_lines and "## Deployment" in first_lines:
        structure = "Legacy"
    elif "Статус:" in first_lines and "🎯 Назначение" in content[:200]:
        structure = "Modern"
    else:
        structure = "Mixed"
    
    # Считаем совпадения с требуемыми секциями
    matches = 0
    missing = []
    for section in required_sections:
        if re.search(section, content, re.IGNORECASE):
            matches += 1
        else:
            missing.append(re.sub(r"[^\w\s]", "", section).strip())
    
    status = "✅" if matches >= 5 else "⚠️"
    missing_str = ", ".join(missing[:2]) if missing else "-"
    
    print(f"{service:<25} {structure:<15} {matches}/6 {status} {missing_str}")

print("\n\n=== Вывод ===")
print(f"Всего сервисов: {len(services)}")
print(f"Шаблон (template_service): 1 сервис")
print(f"Legacy-структура: auth_service и др.")
print(f"Рекомендация: унифицировать все README по шаблону template_service")
