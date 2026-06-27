#!/usr/bin/env python3
"""Test Generation Demo - генерация тестов для Decision Engine models"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к агенту
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.cognitive_agent.src.prompt_engine import PromptEngine


async def generate_tests():
    """Генерация тестов для Decision Engine models"""

    print("=" * 80)
    print("🧪 Test Generation Demo - Decision Engine")
    print("=" * 80)

    # Инициализация PromptEngine
    prompts_dir = Path("agents/cognitive_agent/prompts")
    engine = PromptEngine(prompts_dir=prompts_dir)

    # Контекст для Django-like модели (Pydantic)
    context = {
        "repo_path": "C:/repo",
        "service_name": "decision_engine",
        "python_version": "3.12",
        "framework": "base",  # Используем base для Pydantic
        "current_coverage": "45",
        "coverage_target": "85",
        "file_path": "apps/decision_engine/core/models.py",
        "file_type": "models",
        "code": '''\"\"\"\nModels for Decision Engine.\n\"\"\"\n\nfrom typing import Any\n\nfrom pydantic import BaseModel, Field\n\n\nclass DecisionContext(BaseModel):\n    \"\"\"Контекст для принятия решения\"\"\"\n\n    environment: str = Field(..., description=\"Окружение (staging/production)\")\n    user_role: str = Field(..., description=\"Роль пользователя\")\n    resources_available: bool = Field(..., description=\"Доступность ресурсов\")\n    maintenance_mode: bool | None = False\n    backup_verified: bool | None = False\n    custom_data: dict[str, Any] | None = None\n\n\nclass DecisionRequest(BaseModel):\n    \"\"\"Запрос на принятие решения\"\"\"\n\n    user_id: str = Field(..., description=\"ID пользователя\")\n    action: str = Field(..., description=\"Действие\")\n    context: DecisionContext = Field(..., description=\"Контекст\")\n    include_explanation: bool | None = False\n\n\nclass DecisionResponse(BaseModel):\n    \"\"\"Ответ движка решений\"\"\"\n\n    user_id: str\n    action: str\n    decision: str  # allow/deny/require_approval\n    confidence: float | None = None\n    reason: str | None = None\n    explanation: dict[str, Any] | None = None\n    conditions_checked: int | None = 0
'''
    }

    # Загружаем шаблон
    print("\n✅ Loading template: python/base/unit")
    template = engine.load_template("python/base/unit")
    print(f"   • Template version: {template.version}")
    print(f"   • Content length: {len(template.content)} characters")

    # Рендерим
    print("\n✅ Rendering prompt with context...")
    try:
        prompt = engine.render("python/base/unit", context)
        print(f"   • Rendered prompt length: {len(prompt)} characters")
        print(f"   • First 500 chars:\n{prompt[:500]}...")
    except Exception as e:
        print(f"   ✗ Rendering failed: {e}")
        return

    print("\n" + "=" * 80)
    print("✅ Test Generation Demo Complete!")
    print("=" * 80)
    print("\n📋 Next steps:")
    print("   1. Отправить сгенерированный prompt LLM для получения тестов")
    print("   2. Проверить сгенерированный код тестов")
    print("   3. Добавить тесты в соответствующий файл")
    print("\n💡 Для реальной генерации используйте:")
    print("   await engine.execute_strategy(\"python/base/unit\", context)")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(generate_tests())
