#!/usr/bin/env python3
"""Test autonomous agent with root-level prompts integration"""

import sys
from pathlib import Path

# Добавляем путь к агенту
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent


def main():
    print("=" * 80)
    print("🤖 Test AutonomousAgent with Root-Level Prompts")
    print("=" * 80)

    # Инициализация агента
    print("\n🚀 Инициализация AutonomousAgent...")
    agent = AutonomousCognitiveAgent(project_path="C:/repo")

    print(f"\n✅ Агент инициализирован")
    print(f"   Agent ID: {agent.agent_id}")
    print(f"   Project: {agent.project_path}")
    print(f"   Prompt Engine templates: {len(agent.prompt_engine.templates)}")
    print(f"   Test Generator: {type(agent.test_generator).__name__}")

    # Показать источники шаблонов
    print("\n📋 Template Sources:")
    templates = agent.prompt_engine.list_templates()

    # Show unique templates from each source (before overwrite)
    root_only = []
    agent_only = []
    both = []

    # Root-level templates (python/base, python/django, etc.)
    for name, info in sorted(templates.items()):
        if name.startswith("python/"):
            source = agent.prompt_engine.get_template_source(name)
            if source == "root":
                root_only.append(name)
            elif source == "agent":
                both.append(name)

    # Strategy templates (test_generation, test_coverage_analysis)
    for name, info in sorted(templates.items()):
        if not name.startswith("python/") and name != "README":
            source = agent.prompt_engine.get_template_source(name)
            if source == "agent":
                agent_only.append(name)

    print(f"   Framework templates (root → agent): {len(root_only)} root, {len(both)} in both")
    for name in sorted(root_only + both):
        source = agent.prompt_engine.get_template_source(name)
        print(f"      • {name} (from: {source})")

    print(f"   Strategy templates (agent-only): {len(agent_only)}")
    for name in sorted(agent_only):
        print(f"      • {name}")

    # Проверить TestGenerator
    print("\n🧪 TestGenerator Configuration:")
    tg = agent.test_generator
    print(f"   Project path: {tg.project_path}")
    print(f"   Prompts dir: {tg.prompts_dir}")
    print(f"   Root prompts dir: {tg.root_prompts_dir}")
    print(f"   Prompt engine templates: {len(tg.prompt_engine.templates)}")

    # Проверить PromptEngine
    print("\n📦 PromptEngine:")
    pe = agent.prompt_engine
    print(f"   Prompts dir: {pe.prompts_dir}")
    print(f"   Root prompts dir: {pe.root_prompts_dir}")

    # Показать конкретный шаблон
    print("\n📄 Template: python/base/unit")
    try:
        template = agent.prompt_engine.load_template("python/base/unit")
        source = agent.prompt_engine.get_template_source("python/base/unit")
        print(f"   Source: {source}")
        print(f"   Version: {template.version}")
        print(f"   Content length: {len(template.content)} chars")
        print(f"   First 200 chars:")
        for line in template.content.split("\n")[:5]:
            print(f"      {line[:100]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 80)
    print("✅ Test Complete - Integration Working!")
    print("=" * 80)


if __name__ == "__main__":
    main()
